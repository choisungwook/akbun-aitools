export type Diagram = { path: string; title: string; lines: string[] }

declare module 'claude-code' {
  interface PluginState {
    'akbun-diagram': { last: Diagram | null; touched: string[] }
  }
}
