export type Candidate = { rule: string; source: string }

declare module 'claude-code' {
  interface PluginState {
    'akbun-memory-sync': { pending: Candidate[] }
  }
}
