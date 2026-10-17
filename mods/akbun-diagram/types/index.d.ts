export type Node = { id: string; label: string; kind: 'file' | 'component' | 'step'; now: boolean }
export type Edge = { from: string; to: string; label: string }
export type WorkMap = { title: string; nodes: Node[]; edges: Edge[]; turn: number }
export type Pin = { code: string; title: string; turn: number }

declare module 'claude-code' {
  interface PluginState {
    'akbun-diagram': { map: WorkMap | null; pins: Pin[]; touched: string[]; note: string }
  }
}
