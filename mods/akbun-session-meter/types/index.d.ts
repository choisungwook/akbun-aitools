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

export type DiffFile = {
  path: string
  status: 'added' | 'modified' | 'deleted'
  additions: number
  deletions: number
  isBinary: boolean
  isTruncated: boolean
  patch: string
}

export type DiffSnapshot = {
  isGitRepo: boolean
  files: DiffFile[]
  hiddenCount: number
  isOutputTruncated: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'akbun-session-meter': {
      meter: Shaped<Meter | null>
      agents: Shaped<AgentRow[]>
      diff: Shaped<DiffSnapshot>
      selectedPath: Shaped<string | null>
    }
  }
}
