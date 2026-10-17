import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Diagram } from '../types'

const PLUGIN = 'akbun-diagram'
const PANE = 'diagram'
const OUT_DIR = 'docs/diagrams'
const SUGGEST_AFTER = 3

const last = atom({ plugin: 'akbun-diagram', key: 'last' } as const, null)
const touched = atom({ plugin: 'akbun-diagram', key: 'touched' } as const, [])

const PROMPT = (target: string) => `[${PLUGIN}] ${target}
Mermaid 다이어그램 하나로 그려라. 규칙:
- 구조·흐름이면 flowchart LR, 호출 순서면 sequenceDiagram.
- 노드 10개 이내, 라벨은 한국어 또는 코드 식별자. 대화에 없는 요소를 지어내지 않는다.
- 출력은 첫 줄 "제목: <한 줄>", 둘째 줄 "slug: <영문 소문자-하이픈 4단어 이내>", 그 다음 \`\`\`mermaid 코드 블록 하나. 그 밖의 설명은 쓰지 않는다.`

function parse(text: string): { title: string; slug: string; lines: string[] } | null {
  const m = /```mermaid\s*\n([\s\S]*?)```/.exec(text)
  if (!m || !m[1]) return null
  const title = (/제목:\s*(.+)/.exec(text)?.[1] ?? '다이어그램').trim()
  const slug = slugOf(/slug:\s*(.+)/.exec(text)?.[1] ?? title)

  return { title, slug, lines: m[1].trimEnd().split('\n') }
}

function slugOf(text: string): string {
  const ascii = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

  return ascii.length > 0 ? ascii.slice(0, 40) : 'diagram'
}

async function generate($: EngineInterface, target: string): Promise<Diagram | string> {
  const r = await $.model.fork({ prompt: PROMPT(target) })
  if (!r.isAnswered) return `생성 실패 (${r.reason})`
  const parsed = parse(r.text)
  if (parsed === null) return '응답에 mermaid 블록이 없다'

  const root = await $.session.root()
  const date = new Date(await $.clock.now()).toISOString().slice(0, 10)
  const name = `${date}-${parsed.slug}.md`
  const path = `${OUT_DIR}/${name}`
  const body = ['# ' + parsed.title, '', '아래는 Mermaid 소스다.', '', '```mermaid', ...parsed.lines, '```', ''].join('\n')
  await $.fs.write(`${root}/${path}`, body)

  const diagram: Diagram = { path, title: parsed.title, lines: parsed.lines }
  await update($, last, () => diagram)
  await update($, touched, () => [])
  await $.ui.open({ id: PANE, title: `Diagram: ${parsed.title}` })
  await $.ui.copy({ text: ['```mermaid', ...parsed.lines, '```'].join('\n') })

  return diagram
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'diagram',
      description: '세션에서 다룬 구조(또는 지정한 대상)를 Mermaid로 그려 docs/diagrams/에 저장하고 pane에 표시',
      argumentHint: '[대상 설명]',
    })

    return next(e)
  })

  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    await update($, touched, list => (list.includes(e.file_path) ? list : [...list, e.file_path]))

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    await update($, touched, list => (list.includes(e.file_path) ? list : [...list, e.file_path]))

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const files = await read($, touched)
    if (e.props.hasSurvey || files.length < SUGGEST_AFTER) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text dimColor>변경 파일 {files.length}개. 구조를 그릴까? </Text>
        <Button
          key="draw"
          label="다이어그램"
          onPress={async () => {
            const out = await generate($, `방금 변경한 파일들(${files.join(', ')})의 역할과 호출·의존 관계를`)
            $.ui.toast(typeof out === 'string' ? `${PLUGIN}: ${out}` : `${PLUGIN}: ${out.path} 저장, 클립보드 복사`)
          }}
        />
        <Text> </Text>
        <Button key="dismiss" label="무시" onPress={() => update($, touched, () => [])} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const d = await read($, last)
    const room = Math.max(1, (e.viewport?.rows ?? 24) - 3)

    return (
      <Box flexDirection="column">
        {d === null && <Text dimColor>/diagram 을 실행하면 여기에 Mermaid 소스가 표시된다.</Text>}
        {d !== null && <Text dimColor>{d.path}</Text>}
        {d !== null && d.lines.slice(0, room).map(line => <Text>{line}</Text>)}
      </Box>
    )
  })

  on('command.run', { command: 'diagram' }, async ($, e) => {
    const target = e.args.trim().length > 0 ? e.args.trim() + '을(를)' : '이 세션에서 다룬 코드·문서의 구조와 흐름을'
    const out = await generate($, target)
    if (typeof out === 'string') return { text: `${PLUGIN}: ${out}` }

    return {
      text: [`${PLUGIN}: ${out.path} 저장, pane 표시, 클립보드 복사`, '', '```mermaid', ...out.lines, '```'].join('\n'),
    }
  })
}
