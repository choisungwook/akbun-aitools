import { atom, read, update } from 'claude-code'
import type { AgentInfo, EngineInterface, Register, SessionContextUsage, SessionCost } from 'claude-code'

import type { AgentRow, Meter } from '../types'

const PANE = 'session-meter'
const PANE_OPTIONS = { id: PANE, title: 'Session meter', placement: 'widget', rows: 12, columns: 48 } as const
const AGENT_POLL_MS = 2000
const MAX_AGENT_ROWS = 8

const meter = atom({ plugin: 'akbun-session-meter', key: 'meter' } as const, null, { shape: 'meter-1' })
const agents = atom({ plugin: 'akbun-session-meter', key: 'agents' } as const, [], { shape: 'agents-1' })

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

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    const usage = await $.session.usage()
    await saveMeter($, usage.context, usage.cost)
    await saveAgents($)
    $.clock.every(AGENT_POLL_MS, () => void saveAgents($))
    await $.command.register({
      name: 'session-meter',
      description: '세션 ID, 비용, 토큰, 컨텍스트, 에이전트 목록 pane 열기',
    })
    void $.ui.open(PANE_OPTIONS)

    return result
  })

  on('command.run', { command: 'session-meter' }, async $ => {
    await $.ui.open(PANE_OPTIONS)

    return { text: 'Session meter pane opened.' }
  })

  on('session.measure', async ($, e, next) => {
    await saveMeter($, e.context, e.cost)

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const m = await read($, meter)
    const list = await read($, agents)
    if (!m) return <Text dimColor>측정 대기 중</Text>

    const percent = m.percent ?? 0
    const shown = list.slice(0, MAX_AGENT_ROWS)

    return (
      <Box flexDirection="column">
        <Text>Session  {m.sessionId}</Text>
        <Text>Cost     {formatCost(m.costUsd)} (estimate)</Text>
        <Text>Tokens   {formatTokens(m.tokens)} / {formatTokens(m.window)}</Text>
        <Text color={contextColor(percent)}>Context  {percent}%</Text>
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
}
