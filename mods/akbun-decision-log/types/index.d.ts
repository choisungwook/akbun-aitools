export type Decision = {
  title: string
  slug: string
  scope: string
  decision: string
  reason: string
  rejected: string[]
}

declare module 'claude-code' {
  interface PluginState {
    'akbun-decision-log': { pending: Decision | null }
  }
}
