import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'akbun-session-meter',
  component: 'Pane',
  requestId: 'session-meter',
  props: {
    title: 'Session meter',
    isFocused: false,
    bodyColumns: 48,
    placement: 'widget',
    scroll: { offset: 0, bodyRows: 12 },
    view: {},
  },
} as const

const AGENT = {
  id: 'agent-1',
  description: 'repo 검색',
  type: 'Explore',
  status: 'running',
  kind: 'local_agent',
  taskStatus: 'running',
  label: 'Explore',
  startTime: 1,
  cwd: '/',
  tokenCount: 12_300,
  tokenSamples: [],
  hasRow: true,
  cost: { usd: 0.05 },
} as const

const GIT_DIFF = [
  'diff --git a/src/app.ts b/src/app.ts',
  'index 1111111..2222222 100644',
  '--- a/src/app.ts',
  '+++ b/src/app.ts',
  '@@ -1,2 +1,2 @@',
  ' const a = 1',
  '-const b = 2',
  '+const b = 3',
  '',
].join('\n')

const NEW_FILE_DIFF = [
  'diff --git a/notes.md b/notes.md',
  'new file mode 100644',
  'index 0000000..3333333',
  '--- /dev/null',
  '+++ b/notes.md',
  '@@ -0,0 +1 @@',
  '+hello',
  '',
].join('\n')

const DIFF_PANE = { ...PANE, requestId: 'session-diff', props: { ...PANE.props, title: 'Changes', placement: 'dock', bodyColumns: 100 } } as const

function answerGit(on: Parameters<Parameters<typeof test>[1]>[1]) {
  on('process.run', (_, e) => {
    const argv = e.argv.join(' ')
    if (argv.startsWith('git rev-parse')) return { value: { exitCode: 0, stdout: '/repo\n', stderr: '' } }
    if (argv.startsWith('git diff HEAD')) return { value: { exitCode: 0, stdout: GIT_DIFF, stderr: '' } }
    if (argv.startsWith('git ls-files')) return { value: { exitCode: 0, stdout: 'notes.md\0', stderr: '' } }
    if (argv.includes('--no-index')) return { value: { exitCode: 1, stdout: NEW_FILE_DIFF, stderr: '' } }
    return { value: { exitCode: 1, stdout: '', stderr: 'unexpected' } }
  })
}

test('pane과 status line에 세션 값과 에이전트 목록을 표시한다', async ($, on) => {
  const statuses: string[] = []
  on('command.register', () => ({ value: { command: 'session-meter' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', (_, e) => {
    statuses.push(String(e.text))
    return { value: undefined }
  })
  on('clock.every', () => ({ value: undefined }))
  on('session.id', () => ({ value: 'abcdef12-3456-7890' }))
  on('session.usage', () => ({
    value: { startedAt: 0, rateLimits: [], context: { tokens: 45_200, window: 200_000, percent: 23 }, cost: { usd: 1.234 } },
  }))
  on('agent.list', () => ({ value: [AGENT] }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  answerGit(on)

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  expect(statuses.at(-1)).toBe('abcdef12 | ~$1.23 | 45.2k/200.0k (23%) | agents 1')

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /^Session/ }))?.text).toBe('Session  abcdef12-3456-7890')
    expect((await ui.find({ type: 'Text', text: /^Context/ }))?.text).toBe('Context  23%')
    expect((await ui.find({ type: 'Text', text: /^Agents/ }))?.text).toBe('Agents (1)')
    expect((await ui.find({ type: 'Text', text: /repo 검색/ }))?.text).toBe('▶ repo 검색 [Explore] 12.3k ~$0.05')
    await ui.unmount()
  }

  for (const surface of ['terminal', 'desktop', 'vscode', 'mobile'] as const) {
    const ui = await $.ui.mount({ ...DIFF_PANE, surface })
    expect((await ui.find({ type: 'Text', text: /files changed/ }))?.text).toBe('2 files changed')
    expect(await ui.find({ type: 'Button', key: 'file:src/app.ts' })).toBeTruthy()
    expect(await ui.find({ type: 'Button', key: 'file:notes.md' })).toBeTruthy()
    const code = await ui.find({ type: 'Code' })
    expect(code?.props.format).toBe('diff')
    expect(code?.props.source).toBe('@@ -1,2 +1,2 @@\n const a = 1\n-const b = 2\n+const b = 3\n')
    await ui.unmount()
  }
})

test('측정 전에는 대기 문구를 표시한다', async $ => {
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('측정 대기 중')
  await ui.unmount()
})
