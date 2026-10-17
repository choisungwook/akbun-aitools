import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Edge, Node, Pin, WorkMap } from '../types'

const PLUGIN = 'akbun-diagram'
const PANE = 'diagrams'
const OUT_DIR = 'docs/diagrams'
const DEFAULT_EVERY = 3
const MAX_PINS = 5
const NOTE = '몇 턴이 지나면 작업 지도를 그린다. 지금 그리려면 /diagram'

const map = atom({ plugin: 'akbun-diagram', key: 'map' } as const, null)
const pins = atom({ plugin: 'akbun-diagram', key: 'pins' } as const, [])
const touched = atom({ plugin: 'akbun-diagram', key: 'touched' } as const, [])
const note = atom({ plugin: 'akbun-diagram', key: 'note' } as const, NOTE)

const SHAPE = '{"title":"<무엇인지 40자 이내>","nodes":[{"id":"a","label":"<20자 이내>","kind":"file|component|step","now":false}],"edges":[{"from":"a","to":"b","label":"<선택, 10자 이내>"}]}'

const FORK_PROMPT = (target: string) => `[${PLUGIN}] 이 메시지는 플러그인이 보낸 것이다. 작업을 이어가지 말고 도구도 쓰지 말고, ${target} 작은 지도로 그려라.
JSON 객체 하나만 답한다(설명과 코드 펜스 없이): ${SHAPE}
규칙: 대화가 아니라 작업을 그린다. step은 작업의 단계("할인 추가", "테스트 실행")이고 "파일 읽기"나 "설명"은 아니다. 노드 3~8개, 간선 10개 이내. 간선은 먼저 한 것에서 나중 것으로, 호출하는 쪽에서 호출받는 쪽으로 향한다. file의 label은 파일 이름만 쓴다. 지금 작업 중인 노드 하나에만 "now": true.`

const BASE_PROMPT = (m: WorkMap) => `\n\n사용자가 지금 보는 지도다:\n${toMermaid(m)}\n아직 맞는 노드의 id와 label은 그대로 두고, 작업이 바뀐 부분만 더하거나 빼거나 다시 연결한다.`

export function parseMap(text: string, turn: number): WorkMap | null {
  const start = text.indexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end <= start) return null
  try {
    const json = JSON.parse(text.slice(start, end + 1)) as { title?: unknown; nodes?: unknown; edges?: unknown }
    if (!Array.isArray(json.nodes)) return null
    const nodes: Node[] = json.nodes
      .filter((n): n is Record<string, unknown> => typeof n === 'object' && n !== null && typeof n.id === 'string')
      .map(n => ({
        id: String(n.id).replace(/[^A-Za-z0-9_]/g, '_'),
        label: String(n.label ?? n.id).trim().slice(0, 40),
        kind: n.kind === 'file' || n.kind === 'step' ? n.kind : 'component',
        now: n.now === true,
      }))
    if (nodes.length === 0) return null
    const ids = new Set(nodes.map(n => n.id))
    const edges: Edge[] = (Array.isArray(json.edges) ? json.edges : [])
      .filter((e): e is Record<string, unknown> => typeof e === 'object' && e !== null)
      .map(e => ({ from: String(e.from ?? '').replace(/[^A-Za-z0-9_]/g, '_'), to: String(e.to ?? '').replace(/[^A-Za-z0-9_]/g, '_'), label: String(e.label ?? '').trim().slice(0, 20) }))
      .filter(e => ids.has(e.from) && ids.has(e.to) && e.from !== e.to)

    return { title: String(json.title ?? '작업 지도').trim().slice(0, 60), nodes, edges, turn }
  } catch {
    return null
  }
}

// 간선을 따라 층을 나눈다. 들어오는 간선이 없는 노드가 0층, 나머지는 선행 노드 최대 층 +1.
export function layers(m: WorkMap): Node[][] {
  const depth = new Map<string, number>(m.nodes.map(n => [n.id, 0]))
  for (let pass = 0; pass < m.nodes.length; pass++) {
    let moved = false
    for (const e of m.edges) {
      const want = (depth.get(e.from) ?? 0) + 1
      if (want > (depth.get(e.to) ?? 0) && want < m.nodes.length) {
        depth.set(e.to, want)
        moved = true
      }
    }
    if (!moved) break
  }
  const rows: Node[][] = []
  for (const n of m.nodes) {
    const d = depth.get(n.id) ?? 0
    ;(rows[d] ??= []).push(n)
  }

  return rows.filter(r => r.length > 0)
}

export function toMermaid(m: WorkMap): string {
  const shape = (n: Node) => (n.kind === 'file' ? `${n.id}[${n.label}]` : n.kind === 'step' ? `${n.id}[[${n.label}]]` : `${n.id}(${n.label})`)
  const lines = ['flowchart TD', ...m.nodes.map(n => `  ${shape(n)}`), ...m.edges.map(e => `  ${e.from} -->${e.label ? `|${e.label}|` : ''} ${e.to}`)]

  return lines.join('\n')
}

export function findMermaid(text: string): string[] {
  return [...text.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)].map(m => (m[1] ?? '').trimEnd()).filter(c => c.length > 0)
}

function slugOf(text: string): string {
  const ascii = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

  return ascii.length > 0 ? ascii.slice(0, 40) : 'work-map'
}

let isHeadless = false
let turn = 0
let sinceMap = 0
let isBusy = false

async function every($: EngineInterface): Promise<number> {
  const n = Number(await $.env.get('AKBUN_DIAGRAM_EVERY'))

  return Number.isFinite(n) && n >= 1 ? n : DEFAULT_EVERY
}

async function openPane($: EngineInterface, asked: boolean) {
  if (isHeadless) return
  await $.ui.open(asked ? { id: PANE, title: 'Diagrams', focus: true } : { id: PANE, title: 'Diagrams' })
}

async function refresh($: EngineInterface, force: boolean, lastAnswer: string) {
  if (isBusy) return
  isBusy = true
  sinceMap = 0
  try {
    const cur = await read($, map)
    const files = await read($, touched)
    if (cur !== null && !force) {
      await update($, note, () => '게이트: 작업 모양이 바뀌었는지 haiku가 확인 중…')
      const known = new Set(cur.nodes.map(n => n.label))
      const fresh = files.map(f => f.split('/').at(-1) ?? f).filter(f => !known.has(f))
      const gate = await $.model.complete({
        model: 'haiku',
        system: '코딩 에이전트의 작업 지도를 최신으로 유지하기 위해 지켜본다. YES 또는 NO 한 단어로만 답한다.',
        prompt: `현재 지도: ${cur.title} / ${cur.nodes.map(n => n.label).join(', ')}\n\n지도에 없는데 그 뒤 고친 파일: ${fresh.join(', ') || '없음'}\n\n마지막 답변:\n${lastAnswer.slice(0, 1500)}\n\n지도가 낡았으면(지도에 없는 파일·컴포넌트를 건드렸거나, 테스트·새 기능·수정 같은 단계가 생겼거나, 다른 작업으로 옮겼으면) YES, 지도가 여전히 작업을 보여 주면 NO.`,
        maxTokens: 5,
        timeoutMs: 20000,
      })
      if (!(gate.isAnswered && /^\s*yes/i.test(gate.text))) {
        await update($, note, () => `게이트: ${turn}턴 기준 작업 모양 그대로, 지도 유지${gate.isAnswered ? '' : ` (${gate.reason})`}`)

        return
      }
    }
    await update($, note, () => 'fork: 작업 지도를 그리는 중…')
    const r = await $.model.fork({ prompt: FORK_PROMPT('이 세션에서 지금 하는 작업(파일, 컴포넌트, 단계와 연결)을') + (cur !== null && !force ? BASE_PROMPT(cur) : '') })
    if (!r.isAnswered) {
      await update($, note, () => (r.reason === 'nothing-to-fork' ? '아직 그릴 대화가 없다. 프롬프트를 하나 보낸 뒤 /diagram' : `fork 실패: ${r.reason}`))

      return
    }
    const next = parseMap(r.text, turn)
    if (next === null) {
      await update($, note, () => `fork 답이 지도가 아니다: ${r.text.replace(/\s+/g, ' ').slice(0, 60)}`)

      return
    }
    await update($, map, () => next)
    await update($, touched, () => [])
    await update($, note, () => `${turn}턴에 지도 그림`)
  } finally {
    isBusy = false
  }
}

async function save($: EngineInterface): Promise<string> {
  const cur = await read($, map)
  if (cur === null) return `${PLUGIN}: 저장할 지도가 없다. /diagram 으로 먼저 그린다.`
  const root = await $.session.root()
  const date = new Date(await $.clock.now()).toISOString().slice(0, 10)
  const path = `${OUT_DIR}/${date}-${slugOf(cur.title)}.md`
  const mermaid = toMermaid(cur)
  const body = [`# ${cur.title}`, '', `${date} Claude Code 세션 ${cur.turn}턴의 작업 지도다. 네모는 파일, 둥근 네모는 컴포넌트, 겹네모는 단계다.`, '', '```mermaid', mermaid, '```', ''].join('\n')
  await $.fs.write(`${root}/${path}`, body)
  const copied = await $.ui.copy({ text: ['```mermaid', mermaid, '```'].join('\n') })

  return `${PLUGIN}: ${path} 저장${copied.isCopied ? ', 클립보드 복사' : ''}`
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    isHeadless = e.isInteractive === false
    if (isHeadless) return next(e)
    await $.command.register({
      name: 'diagram',
      description: '작업 지도를 pane에 그린다. force 는 게이트 없이 새로 그림, save 는 docs/diagrams/에 Mermaid로 저장, open 은 pane에 포커스',
      argumentHint: '[force|save|open]',
    })
    await openPane($, false)

    return next(e)
  })

  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    if (e.agentId === undefined) await update($, touched, list => (list.includes(e.file_path) ? list : [...list, e.file_path]))

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    if (e.agentId === undefined) await update($, touched, list => (list.includes(e.file_path) ? list : [...list, e.file_path]))

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    const wait = (await $.env.get('AKBUN_DIAGRAM_WAIT')) === '1'
    if ((isHeadless && !wait) || e.agentId !== undefined || e.reason !== 'answer') return result

    turn += 1
    sinceMap += 1
    const codes = findMermaid(e.answer)
    if (codes.length > 0) {
      await update($, pins, list => {
        const seen = new Set(list.map(p => p.code))
        const fresh: Pin[] = codes.filter(c => !seen.has(c)).map(c => ({ code: c, title: (/^\s*(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram)\b.*/m.exec(c)?.[0] ?? 'mermaid').trim().slice(0, 40), turn }))

        return [...fresh.reverse(), ...list].slice(0, MAX_PINS)
      })
      await openPane($, false)
    }

    if (sinceMap >= (await every($))) {
      const work = refresh($, false, e.answer).catch(() => undefined)
      if (wait) await work
    }

    return result
  })

  on('command.run', { command: 'diagram' }, async ($, e) => {
    const arg = e.args.trim().toLowerCase()
    if (arg === 'save') return { text: await save($) }
    await openPane($, true)
    if (arg === 'open') return {}
    await refresh($, arg === 'force', '')

    return { text: `${PLUGIN}: ${await read($, note)}` }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const cur = await read($, map)
    const list = await read($, pins)
    const hint = await read($, note)
    const border = { file: 'single', component: 'round', step: 'double' } as const

    return (
      <Box flexDirection="column">
        <Text bold>{cur === null ? '작업 지도' : cur.title}</Text>
        <Text dimColor>{hint}</Text>
        {cur !== null && (
          <Box flexDirection="column" marginTop={1}>
            {layers(cur).map((row, i, rows) => (
              <Box flexDirection="column">
                <Box flexDirection="row" flexWrap="wrap" columnGap={1}>
                  {row.map(n => (
                    <Box borderStyle={border[n.kind]} borderColor={n.now ? 'green' : undefined} paddingX={1}>
                      <Text color={n.now ? 'green' : undefined}>{`${n.now ? '▶ ' : ''}${n.label}`}</Text>
                    </Box>
                  ))}
                </Box>
                {i < rows.length - 1 && (
                  <Text dimColor>
                    {'  ↓ ' +
                      cur.edges
                        .filter(ed => row.some(n => n.id === ed.from) && (rows[i + 1] ?? []).some(n => n.id === ed.to))
                        .map(ed => `${cur.nodes.find(n => n.id === ed.from)?.label} → ${cur.nodes.find(n => n.id === ed.to)?.label}${ed.label ? ` (${ed.label})` : ''}`)
                        .join(', ')}
                  </Text>
                )}
              </Box>
            ))}
            {cur.edges
              .filter(ed => {
                const rows = layers(cur)
                const from = rows.findIndex(r => r.some(n => n.id === ed.from))
                const to = rows.findIndex(r => r.some(n => n.id === ed.to))

                return to !== from + 1
              })
              .map(ed => (
                <Text dimColor>{`  ⇢ ${cur.nodes.find(n => n.id === ed.from)?.label} → ${cur.nodes.find(n => n.id === ed.to)?.label}${ed.label ? ` (${ed.label})` : ''}`}</Text>
              ))}
            <Text dimColor>□ 파일 ○ 컴포넌트 ▣ 단계 ▶ 지금</Text>
          </Box>
        )}
        {list.map(pin => (
          <Box flexDirection="column" marginTop={1} borderStyle="single" borderDimColor paddingX={1}>
            <Text bold>{`고정: ${pin.title}`}<Text dimColor>{`  (${pin.turn}턴)`}</Text></Text>
            {pin.code.split('\n').slice(0, 30).map(line => <Text>{line}</Text>)}
          </Box>
        ))}
      </Box>
    )
  })
}
