export type Meter = {
  sessionId: string
  costUsd?: number
  tokens?: number
  window: number
  percent?: number
}

export type AgentRow = {
  id: string
  label: string
  type: string
  status: string
  tokens: number
  costUsd?: number
}

declare module 'claude-code' {
  interface PluginState {
    'akbun-session-meter': {
      meter: Shaped<Meter | null>
      agents: Shaped<AgentRow[]>
    }
  }
}
