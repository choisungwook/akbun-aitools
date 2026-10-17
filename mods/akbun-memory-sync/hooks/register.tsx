import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionMessage } from 'claude-code'

import type { Change, Run } from '../types'

const PLUGIN = 'akbun-memory-sync'
const PANE = 'memory'
const MAX_REFERENCED = 10
const MAX_PRIMARY_CHARS = 16000

const runs = atom({ plugin: 'akbun-memory-sync', key: 'runs' } as const, [])
const dismissed = atom({ plugin: 'akbun-memory-sync', key: 'dismissed' } as const, null)

const JUDGE = `너는 코딩 에이전트의 한 턴을 읽고 저장소의 메모리 파일(AGENTS.md와 그 파일이 참조하는 문서)을 고쳐야 하는지 판정한다.
메모리에 남기는 것은 다음 세션에도 적용되는 사실만이다.
- 사용자가 준 교정이나 확정한 작업 방식 ("앞으로 커밋 메시지는 한국어로", "다시는 README를 자동으로 고치지 마")
- 코드나 git에서 알 수 없는 프로젝트의 목표·제약·결정
- 사용자의 역할·선호
- 메모리에 이미 있는데 이번 턴에서 틀렸다고 드러난 규칙의 수정
이번 작업 하나에만 쓰이는 요청, 질문, 코드 구조 설명, 이미 메모리에 같은 뜻으로 있는 것은 SKIP이다.
정확히 한 줄로만 답한다: "UPDATE: <무엇을 남길지 20단어 이내>" 또는 "SKIP".`

const writerPrompt = (reason: string, files: Map<string, string>, primary: string) => {
  const shown = [...files].map(([name, text]) =>
    name === primary
      ? `<file name="${name}">\n${text.slice(0, MAX_PRIMARY_CHARS)}\n</file>`
      : `<file name="${name}" outline-only="true">\n${outline(text).join('\n')}\n</file>`,
  )

  return `[${PLUGIN}] 이 메시지는 ${PLUGIN} 플러그인이 보낸 것이고 사용자가 보낸 것이 아니다. 도구를 쓰지 말고 텍스트로만 답한다.

분류기가 이번 턴에서 메모리에 남길 것을 찾았다: ${reason}

아래 메모리 파일 중 가장 맞는 파일의 가장 맞는 섹션 끝에 덧붙일 줄을 정한다. 첫 파일이 규칙의 원본이고 나머지는 그 파일이 참조하는 문서다(참조 문서는 제목 목록만 보인다).
규칙:
- 섹션 제목은 파일에 있는 제목 줄을 글자 그대로 쓴다("## 플러그인 변경 규칙"처럼 # 포함).
- 규칙의 주제(커밋·PR, 플러그인 변경, 이미지, 결정 기록 등)와 같은 주제를 다루는 섹션을 고른다. 그 섹션 아래에 더 좁은 제목(###)이 맞으면 그 제목을 쓴다. 주제가 맞는 섹션이 없을 때만 일반 규칙 섹션에 둔다.
- 기존 문체를 따른다. 보통 "- "로 시작하는 한 줄이다. 새 파일이나 새 섹션은 만들지 않는다.
- 같은 뜻의 줄이 이미 있으면 edits를 비운다.

${shown.join('\n\n')}

JSON 객체 하나만 답한다: {"edits": [{"file": "<파일 경로>", "section": "<제목 줄>", "lines": ["<덧붙일 줄>"]}]}. 남길 것이 없으면 {"edits": []}.`
}

export function outline(text: string): string[] {
  return text.split('\n').filter(line => /^#{1,6}\s/.test(line))
}

export type Edit = { file: string; section: string; lines: string[] }

export function parseEdits(text: string, allowed: string[]): Edit[] {
  const start = text.indexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end <= start) throw new Error('no json')
  const json = JSON.parse(text.slice(start, end + 1)) as { edits?: unknown }
  if (!Array.isArray(json.edits)) return []

  return json.edits
    .filter((e): e is Edit => typeof e === 'object' && e !== null)
    .map(e => ({
      file: String(e.file ?? '').replace(/^\.\//, ''),
      section: String(e.section ?? '').trim(),
      lines: Array.isArray(e.lines) ? e.lines.map(String).map(l => l.replace(/\s+$/, '')).filter(l => l.trim().length > 0) : [],
    }))
    .filter(e => allowed.includes(e.file) && e.section.length > 0 && e.lines.length > 0)
}

// 섹션 끝(다음 같은 급 이상 제목 앞)에 줄을 덧붙인다. 같은 줄이 이미 있으면 건너뛴다. 제목이 없으면 null.
export function insertIntoSection(text: string, section: string, lines: string[]): string | null {
  const rows = text.split('\n')
  const at = rows.findIndex(row => row.trim() === section)
  if (at < 0) return null
  const level = (/^#+/.exec(section) ?? ['#'])[0].length
  let end = rows.findIndex((row, i) => i > at && /^#{1,6}\s/.test(row) && (/^#+/.exec(row) ?? [''])[0].length <= level)
  if (end < 0) end = rows.length

  const existing = new Set(rows.slice(at, end).map(r => r.trim()))
  const fresh = lines.filter(l => !existing.has(l.trim()))
  if (fresh.length === 0) return text

  let k = end
  while (k > at + 1 && (rows[k - 1] ?? '').trim() === '') k--
  const prev = (rows[k - 1] ?? '').trim()
  const gap = k === at + 1 || /^[-*]\s|^\d+\.\s/.test(prev) ? [] : ['']

  return [...rows.slice(0, k), ...gap, ...fresh, ...rows.slice(k)].join('\n')
}

const toLines = (text: string) => (text === '' ? [] : text.replace(/\n$/, '').split('\n'))

export function lineDiff(before: string, after: string): { added: number; removed: number } {
  const a = toLines(before)
  const b = toLines(after)
  let row = new Array<number>(b.length + 1).fill(0)
  for (const line of a) {
    const next = [0]
    for (let j = 0; j < b.length; j++) next.push(line === b[j] ? (row[j] ?? 0) + 1 : Math.max(row[j + 1] ?? 0, next[j] ?? 0))
    row = next
  }
  const kept = row[b.length] ?? 0

  return { added: b.length - kept, removed: a.length - kept }
}

export function lastExchange(messages: SessionMessage[]): string {
  const start = messages.findLastIndex(m => m.role === 'user' && m.text.trim() !== '' && !m.toolResults?.length)
  const lines = messages.slice(Math.max(0, start)).flatMap(m => [
    ...(m.text.trim() ? [`${m.role.toUpperCase()}: ${m.text.trim()}`] : []),
    ...m.toolUses.map(t => `TOOL: ${t.tool}`),
  ])
  const text = lines.join('\n')

  return text.length > 12000 ? `${text.slice(0, 4000)}\n…\n${text.slice(-8000)}` : text
}

export async function memoryFiles($: EngineInterface): Promise<string[]> {
  const root = await $.session.root()
  const primary = (await $.fs.exists(`${root}/AGENTS.md`)) ? 'AGENTS.md' : 'CLAUDE.md'
  if (!(await $.fs.exists(`${root}/${primary}`))) return []

  const text = await $.fs.read(`${root}/${primary}`)
  const found = new Set<string>()
  for (const m of text.matchAll(/`([\w./-]+\.md)`|\]\(([\w./-]+\.md)\)/g)) {
    const path = (m[1] ?? m[2] ?? '').replace(/^\.\//, '')
    if (path && path !== primary && !path.includes('..')) found.add(path)
  }

  const referenced: string[] = []
  for (const path of found) {
    if (referenced.length >= MAX_REFERENCED) break
    if (await $.fs.exists(`${root}/${path}`)) referenced.push(path)
  }

  return [primary, ...referenced]
}

async function readAll($: EngineInterface, root: string, files: string[]): Promise<Map<string, string>> {
  const out = new Map<string, string>()
  for (const f of files) out.set(f, await $.fs.read(`${root}/${f}`).catch(() => ''))

  return out
}

const setRun = ($: EngineInterface, id: string, patch: Partial<Run>) =>
  update($, runs, list => list.map(run => (run.id === id ? { ...run, ...patch } : run)))

let isBusy = false
let isPending = false

async function consider($: EngineInterface) {
  if (isBusy) {
    isPending = true
    return
  }
  isBusy = true
  try {
    await sync($)
  } finally {
    isBusy = false
    if (isPending) {
      isPending = false
      void consider($).catch(() => undefined)
    }
  }
}

async function sync($: EngineInterface) {
  const files = await memoryFiles($)
  if (files.length === 0) return

  const id = crypto.randomUUID()
  await update($, runs, list => [...list, { id, at: Date.now(), status: 'judging', changes: [] } as Run].slice(-20))

  const root = await $.session.root()
  const primary = files[0] ?? 'AGENTS.md'
  const before = await readAll($, root, files)
  const index = [...before].map(([name, text]) => `${name}\n${outline(text).join('\n')}`).join('\n\n')
  const exchange = lastExchange(await $.session.messages())

  const verdict = await $.model.complete({
    model: 'haiku',
    system: JUDGE,
    prompt: `<memory_outline>\n${index}\n</memory_outline>\n\n<turn>\n${exchange}\n</turn>`,
    maxTokens: 80,
    timeoutMs: 20000,
  })
  if (!verdict.isAnswered) return setRun($, id, { status: 'failed', reason: `haiku: ${verdict.reason}` })

  const line = verdict.text.trim()
  if (!line.startsWith('UPDATE')) return setRun($, id, { status: 'skipped' })

  const reason = line.replace(/^UPDATE:?\s*/, '')
  await setRun($, id, { status: 'forking', reason })

  const reply = await $.model.fork({ prompt: writerPrompt(reason, before, primary) })
  if (!reply.isAnswered) return setRun($, id, { status: 'failed', reason: `fork: ${reply.reason}` })

  let edits: Edit[]
  try {
    edits = parseEdits(reply.text, files)
  } catch {
    return setRun($, id, { status: 'failed', reason: 'fork가 JSON으로 답하지 않음' })
  }

  const after = new Map(before)
  const missed: string[] = []
  for (const edit of edits) {
    const next = insertIntoSection(after.get(edit.file) ?? '', edit.section, edit.lines)
    if (next === null) missed.push(`${edit.file} ${edit.section}`)
    else after.set(edit.file, next)
  }

  const changes: Change[] = []
  const snapshot: Record<string, string> = {}
  for (const [file, text] of after) {
    const old = before.get(file) ?? ''
    if (old === text) continue
    await $.fs.write(`${root}/${file}`, text)
    snapshot[file] = old
    changes.push({ file, ...lineDiff(old, text) })
  }

  return setRun($, id, {
    status: 'done',
    changes,
    before: snapshot,
    reason: missed.length > 0 ? `${reason} (섹션 없음: ${missed.join(', ')})` : reason,
  })
}

async function undo($: EngineInterface, run: Run) {
  const root = await $.session.root()
  for (const [file, text] of Object.entries(run.before ?? {})) await $.fs.write(`${root}/${file}`, text)
  await setRun($, run.id, { status: 'undone' })
}

export const register: Register = on => {
  let isHeadless = false

  on('session.start', async ($, e, next) => {
    isHeadless = e.isInteractive === false
    if (isHeadless) return next(e)
    await $.command.register({
      name: 'memory-sync',
      description: '메모리 반영 기록 pane을 연다. now 는 지금 판정·반영, undo 는 마지막 반영 되돌리기',
      argumentHint: '[now|undo]',
    })
    void $.ui.open({ id: PANE, title: 'Memory' })

    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const { sections } = await next(e)
    const files = await memoryFiles($)
    if (files.length === 0) return { sections }

    return {
      sections: [
        ...sections,
        {
          id: `${PLUGIN}:handoff`,
          scope: 'session',
          text: `# 메모리 반영은 ${PLUGIN}이 맡는다\n이 저장소의 메모리(규칙) 원본은 ${files[0]}이고 참조 문서는 ${files.slice(1).join(', ') || '없음'}이다. 사용자가 "기억해", "앞으로는", "다시는" 같은 반복 규칙을 말하면 직접 파일을 고치지 말고 알겠다고만 답한다. 턴이 끝나면 플러그인이 백그라운드 fork로 그 파일들에 반영한다. "[${PLUGIN}]"으로 시작하는 메시지는 사용자가 아니라 플러그인이 보낸 것이다. 도구 없이 텍스트로만 답한다.`,
        },
      ],
    }
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId === undefined && e.reason === 'answer') {
      const work = consider($).catch(() => undefined)
      if ((await $.env.get('AKBUN_MEMORY_SYNC_WAIT')) === '1') await work
    }

    return result
  })

  on('command.run', { command: 'memory-sync' }, async ($, e) => {
    const arg = e.args.trim()
    if (arg === 'now') {
      await $.ui.open({ id: PANE, title: 'Memory' })
      await consider($)
      const latest = (await read($, runs)).at(-1)
      if (!latest) return { text: `${PLUGIN}: 작업 디렉터리에 AGENTS.md나 CLAUDE.md가 없다.` }
      if (latest.status === 'skipped') return { text: `${PLUGIN}: 이번 턴에는 남길 규칙이 없다.` }
      if (latest.status === 'failed') return { text: `${PLUGIN}: 실패 (${latest.reason})` }

      return { text: `${PLUGIN}: ${latest.changes.map(c => `${c.file} +${c.added} −${c.removed}`).join(', ') || '바뀐 파일 없음'}` }
    }
    if (arg === 'undo') {
      const latest = (await read($, runs)).findLast(run => run.status === 'done' && run.changes.length > 0)
      if (!latest) return { text: `${PLUGIN}: 되돌릴 반영이 없다.` }
      await undo($, latest)

      return { text: `${PLUGIN}: ${latest.changes.map(c => c.file).join(', ')} 되돌림` }
    }
    await $.ui.open({ id: PANE, title: 'Memory', focus: true })

    return { text: 'Memory pane 열림' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const latest = (await read($, runs)).findLast(run => run.status !== 'judging' && run.status !== 'skipped')
    if (e.props.hasSurvey || !latest || latest.id === (await read($, dismissed))) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const files = latest.changes.map(c => c.file).join(', ')
    const added = latest.changes.reduce((n, c) => n + c.added, 0)
    const removed = latest.changes.reduce((n, c) => n + c.removed, 0)

    return (
      <Box>
        <Text color={latest.status === 'failed' ? 'red' : undefined}>
          {latest.status === 'forking' && `메모리: 반영 중 (${latest.reason}) `}
          {latest.status === 'done' && '메모리: '}
          {latest.status === 'done' && latest.changes.length > 0 && <Text color="green">+{added} </Text>}
          {latest.status === 'done' && latest.changes.length > 0 && <Text color="red">−{removed} </Text>}
          {latest.status === 'done' && <Text dimColor>{files ? `· ${files} ` : '바뀐 파일 없음 '}</Text>}
          {latest.status === 'undone' && `메모리: 되돌림 · ${files} `}
          {latest.status === 'failed' && `메모리: 실패 (${latest.reason}) `}
        </Text>
        <Button key="open" label="열기" onPress={() => $.ui.open({ id: PANE, title: 'Memory', focus: true })} />
        <Text> </Text>
        {latest.status === 'done' && latest.changes.length > 0 && <Button key="undo" label="되돌리기" onPress={() => undo($, latest)} />}
        {latest.status === 'done' && latest.changes.length > 0 && <Text> </Text>}
        <Button key="hide" label="숨기기" onPress={() => update($, dismissed, () => latest.id)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const list = await read($, runs)
    const files = new Set(list.filter(r => r.status === 'done').flatMap(r => r.changes.map(c => c.file)))
    const added = list.filter(r => r.status === 'done').flatMap(r => r.changes).reduce((n, c) => n + c.added, 0)
    const room = Math.max(1, (e.viewport?.rows ?? 24) - 6)
    const time = (at: number) => new Date(at).toTimeString().slice(0, 5)

    return (
      <Box flexDirection="column">
        <Box>
          <Text bold>이 세션에서 메모리 파일 {files.size}개 변경 </Text>
          <Text color="green">+{added}</Text>
        </Box>
        {list.length === 0 && <Text dimColor>첫 턴이 끝나면 판정을 시작한다.</Text>}
        {[...list]
          .reverse()
          .filter(run => run.status !== 'skipped' || run === list[list.length - 1])
          .slice(0, room)
          .map(run => (
            <Box flexDirection="column" marginTop={1}>
              <Text dimColor={run.status === 'skipped'}>
                {time(run.at)}{' '}
                {run.status === 'judging' && 'haiku가 턴을 판정하는 중…'}
                {run.status === 'skipped' && '남길 규칙 없음'}
                {run.status === 'forking' && `fork가 쓰는 중: ${run.reason}`}
                {run.status === 'done' && (run.changes.length === 0 ? `fork가 바꾼 것 없음 (${run.reason})` : `${run.reason}`)}
                {run.status === 'undone' && `되돌림: ${run.reason}`}
                {run.status === 'failed' && `실패: ${run.reason}`}
              </Text>
              {run.changes.map(change => (
                <Box>
                  <Text color="yellow">{'  '}~ {change.file}{'  '}</Text>
                  <Text color="green">+{change.added}</Text>
                  <Text> </Text>
                  <Text color="red">−{change.removed}</Text>
                </Box>
              ))}
            </Box>
          ))}
      </Box>
    )
  })
}
