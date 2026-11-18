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
})

test('측정 전에는 대기 문구를 표시한다', async $ => {
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('측정 대기 중')
  await ui.unmount()
})
