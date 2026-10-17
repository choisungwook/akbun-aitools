import { expect, mock, test } from 'claude-code/testing'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const BAND = { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80, scroll: { offset: 0, bodyRows: 3 }, view: {} }
const PANE = { title: 'Diagram', isFocused: false, bodyColumns: 80, placement: 'dock' as const, scroll: { offset: 0, bodyRows: 20 } }
const REPLY = '제목: 자막 변환 흐름\nslug: Transcript Flow\n```mermaid\nflowchart LR\n  A[yt-dlp] --> B[cleaned]\n  B --> C[Markdown]\n```\n'

function world(on: Parameters<Parameters<typeof test>[1]>[1], written: Record<string, string>, copied: string[]) {
  mock.clock(on, { now: 1_760_000_000_000 })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('fs.write', (_, e) => {
    written[e.path] = e.text

    return { value: undefined }
  })
  on('model.fork', () => ({ value: { isAnswered: true as const, text: REPLY, usage: USAGE } }))
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('ui.copy', (_, e) => {
    copied.push(e.text)

    return { value: { isCopied: true as const } }
  })
  on('tool.call', () => ({ result: 'ok' }))
  on('ui.render', () => h('Text', { dimColor: true }, '-'))
}

test('/diagram 은 Mermaid 파일을 docs/diagrams/ 에 쓰고 클립보드에 복사하고 pane 에 보여 준다', async ($, on) => {
  const written: Record<string, string> = {}
  const copied: string[] = []
  world(on, written, copied)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'diagram', args: '자막 변환 스킬', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })

  expect(r.text ?? '').toContain('docs/diagrams/2025-10-09-transcript-flow.md')
  expect(r.text ?? '').toContain('flowchart LR')
  expect(written['/repo/docs/diagrams/2025-10-09-transcript-flow.md'] ?? '').toContain('```mermaid\nflowchart LR')
  expect(copied[0] ?? '').toStartWith('```mermaid')

  const pane = await $.ui.mount({ plugin: 'akbun-diagram', surface: 'terminal', component: 'Pane', requestId: 'diagram', props: PANE })
  expect(await pane.find({ type: 'Text', text: /A\[yt-dlp\]/ })).toBeDefined()
  await pane.unmount()
})

test('파일 3개를 고친 뒤에는 다이어그램 제안 띠가 뜨고 무시하면 사라진다', async ($, on) => {
  world(on, {}, [])

  for (const file of ['a.ts', 'b.ts', 'c.ts']) {
    await $.tool.call({ tool: 'Write', tool_use_id: `w-${file}`, file_path: `/repo/${file}`, content: 'x' })
  }

  const ui = await $.ui.mount({ plugin: 'akbun-diagram', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await ui.find({ type: 'Text', text: /변경 파일 3개/ })).toBeDefined()
  await $.ui.press({ plugin: 'akbun-diagram', key: 'dismiss' })
  expect(await ui.find({ type: 'Text', text: /변경 파일/ })).toBeUndefined()
  await ui.unmount()
})
