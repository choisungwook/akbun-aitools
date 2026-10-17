export type Change = { file: string; added: number; removed: number }

export type Run = {
  id: string
  at: number
  status: 'judging' | 'skipped' | 'forking' | 'done' | 'failed' | 'undone'
  reason?: string
  changes: Change[]
  before?: Record<string, string>
}

declare module 'claude-code' {
  interface PluginState {
    'akbun-memory-sync': { runs: Run[]; dismissed: string | null }
  }
}
