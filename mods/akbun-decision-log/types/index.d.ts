export type Option = {
  label: string
  detail: string
  leadsTo: string
  pros: string[]
  cons: string[]
  mine?: boolean
}

export type Question = {
  id: string
  at: number
  status: 'thinking' | 'ready' | 'failed'
  reason?: string
  title: string
  slug: string
  scope: string
  question: string
  context: string
  options: Option[]
  recommendation: { label: string; why: string } | null
  chosen: number | null
  written: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'akbun-decision-log': { current: Question | null; dismissed: string | null }
  }
}
