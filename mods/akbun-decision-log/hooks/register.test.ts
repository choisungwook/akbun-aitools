import { expect, mock, test } from 'claude-code/testing'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const BAND = { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80, scroll: { offset: 0, bodyRows: 3 }, view: {} }
const DECISION = '{"title": "Notion 동기화는 CLI 우선", "slug": "notion-sync-cli-first", "scope": "akbun-md-to-notion", "decision": "CLI를 먼저 쓰고 MCP는 대체로 둔다.", "reason": "CLI가 빠르고 재현 가능하다.", "rejected": ["MCP 단독: 느리고 인증이 자주 끊긴다"]}'

function world(on: Parameters<Parameters<typeof test>[1]>[1], written: Record<string, string>) {
  mock.clock(on, { now: 1_760_000_000_000 })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('session.id', () => ({ value: 'sess-1' }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('fs.exists', (_, e) => ({ value: e.path === '/repo/docs/adr' || e.path === '/repo/docs/adr/README.md' }))
  on('fs.list', () => ({ value: [{ name: '0006-old.md', kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false }, { name: 'README.md', kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false }] }))
  on('fs.read', () => ({ value: '# 결정 기록\n\n| 번호 | 범위 | 결정 |\n|---|---|---|\n| [0006](0006-old.md) | x | y |\n' }))
  on('fs.write', (_, e) => {
    written[e.path] = e.text

    return { value: undefined }
  })
  on('model.complete', () => ({ value: { isAnswered: true as const, text: DECISION, usage: USAGE } }))
  on('model.fork', () => ({ value: { isAnswered: true as const, text: DECISION, usage: USAGE } }))
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
}

test('결정이 감지된 턴 뒤 띠에서 기록을 누르면 다음 번호의 ADR과 색인 행이 써진다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: 'CLI랑 MCP 중 뭘 기본으로 할까', wait: false, origin: { kind: 'composer' } })
  await $.turn.complete({ answer: 'CLI 우선으로 간다', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })

  const ui = await $.ui.mount({ plugin: 'akbun-decision-log', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await ui.find({ type: 'Text', text: /Notion 동기화는 CLI 우선/ })).toBeDefined()
  await $.ui.press({ plugin: 'akbun-decision-log', key: 'record' })
  await ui.unmount()

  const adr = written['/repo/docs/adr/0007-notion-sync-cli-first.md'] ?? ''
  expect(adr).toStartWith('# Notion 동기화는 CLI 우선')
  expect(adr).toContain('Scope: akbun-md-to-notion')
  expect(adr).toContain('## Rejected alternatives')
  expect(adr).toContain('MCP 단독')
  expect(written['/repo/docs/adr/README.md'] ?? '').toEndWith('| [0007](0007-notion-sync-cli-first.md) | akbun-md-to-notion | Notion 동기화는 CLI 우선 |\n')
})

test('/decision <한 줄> 은 대화를 fork 해 ADR을 바로 쓴다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'decision', args: 'CLI 우선', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('docs/adr/0007-notion-sync-cli-first.md')
  expect(Object.keys(written)).toContain('/repo/docs/adr/0007-notion-sync-cli-first.md')
})

test('/decision list 는 번호가 붙은 기록만 나열한다', async ($, on) => {
  world(on, {})

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'decision', args: 'list', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text).toBe('0006-old.md')
})
