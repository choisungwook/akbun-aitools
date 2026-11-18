import { atom, read, update } from 'claude-code'
import type { AgentInfo, EngineInterface, Register, SessionContextUsage, SessionCost } from 'claude-code'

import type { AgentRow, DiffFile, Meter } from '../types'
import { readGitDiff } from './diff'

const PANE = 'session-meter'
const PANE_OPTIONS = { id: PANE, title: 'Session meter', placement: 'widget', rows: 13, columns: 48 } as const
const DIFF_PANE = 'session-diff'
const DIFF_PANE_OPTIONS = { id: DIFF_PANE, title: 'Changes', rows: 30, columns: 100 } as const
const FILE_CHANGING_TOOLS = ['Edit', 'Write', 'MultiEdit', 'NotebookEdit', 'Bash']
const AGENT_POLL_MS = 2000
const MAX_AGENT_ROWS = 8

const meter = atom({ plugin: 'akbun-session-meter', key: 'meter' } as const, null, { shape: 'meter-1' })
const agents = atom({ plugin: 'akbun-session-meter', key: 'agents' } as const, [], { shape: 'agents-1' })
const diff = atom({ plugin: 'akbun-session-meter', key: 'diff' } as const, { isGitRepo: true, files: [] }, { shape: 'diff-1' })
const selectedPath = atom({ plugin: 'akbun-session-meter', key: 'selectedPath' } as const, null, { shape: 'selected-1' })

const FILE_MARK: Record<DiffFile['status'], string> = { added: 'A', modified: 'M', deleted: 'D' }
const FILE_COLOR: Record<DiffFile['status'], string> = { added: 'green', modified: 'yellow', deleted: 'red' }

const ACTIVE_STATUSES = ['pending', 'running', 'waiting']
const STATUS_MARK: Record<string, string> = {
  pending: '…',
  running: '▶',
  waiting: '⏸',
  idle: '·',
  completed: '✓',
  failed: '✗',
  killed: '■',
}

const formatTokens = (n?: number) => {
  if (n === undefined) return '-'
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`
  return String(n)
}

const formatCost = (usd?: number) => (usd === undefined ? '-' : `~$${usd.toFixed(2)}`)

const sum = (files: DiffFile[], key: 'additions' | 'deletions') => files.reduce((n, f) => n + f[key], 0)

const contextColor = (percent: number) => (percent >= 80 ? 'red' : percent >= 60 ? 'yellow' : 'green')

const statusText = (m: Meter, activeAgents: number) =>
  `${m.sessionId.slice(0, 8)} | ${formatCost(m.costUsd)} | ` +
  `${formatTokens(m.tokens)}/${formatTokens(m.window)} (${m.percent ?? 0}%) | agents ${activeAgents}`

const toRow = (agent: AgentInfo): AgentRow => ({
  id: agent.id,
  label: agent.name ?? agent.description ?? agent.label,
  type: agent.type,
  status: agent.status,
  tokens: agent.tokenCount,
  costUsd: agent.cost?.usd,
})

// 실행 중인 agent를 위에, 같은 상태끼리는 최근 시작 순으로 둔다
const sortAgents = (list: AgentInfo[]) =>
  [...list].sort((a, b) => {
    const activeDiff = Number(ACTIVE_STATUSES.includes(b.status)) - Number(ACTIVE_STATUSES.includes(a.status))
    return activeDiff !== 0 ? activeDiff : b.startTime - a.startTime
  })

async function refreshStatus($: EngineInterface) {
  const m = await read($, meter)
  if (!m) return
  const list = await read($, agents)
  $.ui.status(statusText(m, list.filter(a => ACTIVE_STATUSES.includes(a.status)).length))
}

async function saveMeter($: EngineInterface, context: SessionContextUsage, cost?: SessionCost) {
  const value: Meter = {
    sessionId: await $.session.id(),
    costUsd: cost?.usd,
    tokens: context.tokens,
    window: context.window,
    percent: context.percent,
  }
  await update($, meter, () => value)
  await refreshStatus($)
}

async function saveAgents($: EngineInterface) {
  const rows = sortAgents(await $.agent.list()).map(toRow)
  const previous = await read($, agents)
  if (JSON.stringify(previous) === JSON.stringify(rows)) return
  await update($, agents, () => rows)
  await refreshStatus($)
}

async function saveDiff($: EngineInterface) {
  const snapshot = await readGitDiff($)
  const previous = await read($, diff)
  if (JSON.stringify(previous) === JSON.stringify(snapshot)) return
  await update($, diff, () => snapshot)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const usage = await $.session.usage()
    await saveMeter($, usage.context, usage.cost)
    await saveAgents($)
    await saveDiff($)
    $.clock.every(AGENT_POLL_MS, () => void saveAgents($))
    await $.command.register({
      name: 'session-meter',
      description: '세션 ID, 비용, 토큰, 컨텍스트, 에이전트 목록 pane 열기',
    })
    await $.command.register({
      name: 'session-diff',
      description: '변경한 파일과 diff pane 열기',
    })
    void $.ui.open(PANE_OPTIONS)

    return result
  })

  on('command.run', { command: 'session-meter' }, async $ => {
    await $.ui.open(PANE_OPTIONS)

    return { text: 'Session meter pane opened.' }
  })

  on('command.run', { command: 'session-diff' }, async $ => {
    await saveDiff($)
    await $.ui.open(DIFF_PANE_OPTIONS)

    return { text: 'Changes pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    if (FILE_CHANGING_TOOLS.includes(e.tool)) await saveDiff($)

    return ran
  })

  on('session.measure', async ($, e, next) => {
    await saveMeter($, e.context, e.cost)

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Text } = $.ui.resolve(e)
    const m = await read($, meter)
    const list = await read($, agents)
    const { files } = await read($, diff)
    if (!m) return <Text dimColor>측정 대기 중</Text>

    const percent = m.percent ?? 0
    const shown = list.slice(0, MAX_AGENT_ROWS)

    return (
      <Box flexDirection="column">
        <Text>Session  {m.sessionId}</Text>
        <Text>Cost     {formatCost(m.costUsd)} (estimate)</Text>
        <Text>Tokens   {formatTokens(m.tokens)} / {formatTokens(m.window)}</Text>
        <Text color={contextColor(percent)}>Context  {percent}%</Text>
        <Button key="open-diff" hotkey="d" onPress={() => void $.ui.open(DIFF_PANE_OPTIONS)}>
          Changes  {files.length} files <Text color="green">+{sum(files, 'additions')}</Text> <Text color="red">-{sum(files, 'deletions')}</Text>
        </Button>
        <Text bold>Agents ({list.length})</Text>
        {list.length === 0 && <Text dimColor>실행한 에이전트 없음</Text>}
        {shown.map(agent => (
          <Text dimColor={!ACTIVE_STATUSES.includes(agent.status)}>
            {STATUS_MARK[agent.status] ?? '?'} {agent.label} [{agent.type}] {formatTokens(agent.tokens)} {formatCost(agent.costUsd)}
          </Text>
        ))}
        {list.length > shown.length && <Text dimColor>외 {list.length - shown.length}개</Text>}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: DIFF_PANE }, async ($, e) => {
    const { Box, Button, Code, Text } = $.ui.resolve(e)
    const { isGitRepo, files } = await read($, diff)
    if (!isGitRepo) return <Text dimColor>git 저장소가 아니라 diff를 표시하지 않습니다</Text>

    const chosen = await read($, selectedPath)
    const selected = files.find(f => f.path === chosen) ?? files[0]

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text bold>{files.length} files changed</Text>
          <Text color="green">+{sum(files, 'additions')}</Text>
          <Text color="red">-{sum(files, 'deletions')}</Text>
          <Button key="refresh" hotkey="r" onPress={() => void saveDiff($)}>새로고침</Button>
        </Box>
        {files.length === 0 && <Text dimColor>HEAD 대비 변경 없음</Text>}
        {files.map(file => (
          <Button key={`file:${file.path}`} onPress={() => void update($, selectedPath, () => file.path)}>
            <Text color={FILE_COLOR[file.status]}>{FILE_MARK[file.status]}</Text> {file === selected ? '▸ ' : '  '}{file.path}{' '}
            <Text color="green">+{file.additions}</Text> <Text color="red">-{file.deletions}</Text>
          </Button>
        ))}
        {selected && <Text bold>{selected.path}</Text>}
        {selected?.isBinary && <Text dimColor>바이너리 파일</Text>}
        {selected && selected.patch !== '' && <Code source={selected.patch} path={selected.path} format="diff" />}
        {selected?.isTruncated && <Text dimColor>diff가 길어 앞부분만 표시합니다</Text>}
      </Box>
    )
  })
}
