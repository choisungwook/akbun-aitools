import type { RenderElement } from 'claude-code'
import type { TestBody } from 'claude-code/testing'
import { expect, mock, test } from 'claude-code/testing'

import { findMermaid, layers, parseMap, toMermaid } from './register'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const PANE = { title: 'Diagrams', isFocused: false, bodyColumns: 80, placement: 'dock' as const, scroll: { offset: 0, bodyRows: 40 }, view: {} }
const MAP =
  '{"title":"자막 변환 흐름","nodes":[{"id":"sh","label":"fetch_transcript.sh","kind":"file","now":false},{"id":"clean","label":"clean_vtt.py","kind":"file","now":false},' +
  '{"id":"md","label":"Markdown 대본","kind":"component","now":false},{"id":"test","label":"테스트 실행","kind":"step","now":true}],' +
  '"edges":[{"from":"sh","to":"clean","label":"vtt"},{"from":"clean","to":"md","label":""},{"from":"sh","to":"test","label":""}]}'

function world(on: Parameters<TestBody>[1], written: Record<string, string>, copied: string[], counts = { complete: 0, fork: 0 }, gate = 'YES') {
  mock.clock(on, { now: 1_760_000_000_000 })
  mock.env(on, { AKBUN_DIAGRAM_WAIT: '1' })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('fs.write', (_, e) => {
    written[e.path] = e.text

    return { value: undefined }
  })
  on('model.complete', () => {
    counts.complete += 1

    return { value: { isAnswered: true as const, text: gate, usage: USAGE } }
  })
  on('model.fork', () => {
    counts.fork += 1

    return { value: { isAnswered: true as const, text: MAP, usage: USAGE } }
  })
  on('ui.copy', (_, e) => {
    copied.push(e.text)

    return { value: { isCopied: true as const } }
  })
  on('tool.call', () => ({ result: 'ok' }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('ui.render', () => h('Text', { dimColor: true }, '-') as RenderElement)
}

const END = { durationMs: 1, isAborted: false, reason: 'answer' as const }

test('parseMap 은 노드 종류를 정리하고 layers 는 간선 방향대로 층을 나누고 toMermaid 는 모양을 살린다', async () => {
  const m = parseMap(MAP, 1)
  expect(m?.nodes.length).toBe(4)
  expect(layers(m!).map(r => r.map(n => n.id))).toEqual([['sh'], ['clean', 'test'], ['md']])
  expect(toMermaid(m!)).toBe('flowchart TD\n  sh[fetch_transcript.sh]\n  clean[clean_vtt.py]\n  md(Markdown 대본)\n  test[[테스트 실행]]\n  sh -->|vtt| clean\n  clean --> md\n  sh --> test')
  expect(findMermaid('글\n```mermaid\nflowchart LR\n  A --> B\n```\n끝')).toEqual(['flowchart LR\n  A --> B'])
  expect(parseMap('{"nodes": []}', 1)).toBeNull()
})

test('/diagram force 는 게이트 없이 fork 로 지도를 받아 pane 에 상자와 간선으로 그린다', async ($, on) => {
  const counts = { complete: 0, fork: 0 }
  world(on, {}, [], counts)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'diagram', args: 'force', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('지도 그림')
  expect(counts).toEqual({ complete: 0, fork: 1 })

  const pane = await $.ui.mount({ plugin: 'akbun-diagram', surface: 'terminal', component: 'Pane', requestId: 'diagrams', props: PANE })
  expect(await pane.find({ type: 'Text', text: /자막 변환 흐름/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /▶ 테스트 실행/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /fetch_transcript\.sh → clean_vtt\.py \(vtt\)/ })).toBeDefined()
  await pane.unmount()
})

test('답에 mermaid 블록이 있으면 pane 에 고정되고, 3턴마다 게이트가 돌아 YES 면 fork 가 지도를 그린다', async ($, on) => {
  const counts = { complete: 0, fork: 0 }
  world(on, {}, [], counts)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ ...END, answer: '구조는 이렇다.\n```mermaid\nflowchart LR\n  A[yt-dlp] --> B[cleaned]\n```', turnId: 't1' })
  await $.turn.complete({ ...END, answer: '고쳤다.', turnId: 't2' })
  expect(counts.fork).toBe(0)
  await $.turn.complete({ ...END, answer: '테스트 통과.', turnId: 't3' })
  expect(counts).toEqual({ complete: 0, fork: 1 })

  await $.tool.call({ tool: 'Write', tool_use_id: 'w1', file_path: '/repo/new.ts', content: 'x' })
  for (const id of ['t4', 't5', 't6']) await $.turn.complete({ ...END, answer: '계속.', turnId: id })
  expect(counts).toEqual({ complete: 1, fork: 2 })

  const pane = await $.ui.mount({ plugin: 'akbun-diagram', surface: 'terminal', component: 'Pane', requestId: 'diagrams', props: PANE })
  expect(await pane.find({ type: 'Text', text: /고정: flowchart LR/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /A\[yt-dlp\] --> B\[cleaned\]/ })).toBeDefined()
  await pane.unmount()
})

test('게이트가 NO 면 지도를 유지하고 fork 를 부르지 않는다', async ($, on) => {
  const counts = { complete: 0, fork: 0 }
  world(on, {}, [], counts, 'NO')

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'diagram', args: 'force', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  const r = await $.command.run({ command: 'diagram', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('지도 유지')
  expect(counts).toEqual({ complete: 1, fork: 1 })
})

test('/diagram save 는 지도를 Mermaid 로 docs/diagrams/ 에 쓰고 클립보드에 복사한다', async ($, on) => {
  const written: Record<string, string> = {}
  const copied: string[] = []
  world(on, written, copied)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.command.run({ command: 'diagram', args: 'force', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  const r = await $.command.run({ command: 'diagram', args: 'save', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('docs/diagrams/2025-10-09-work-map.md 저장, 클립보드 복사')
  expect(written['/repo/docs/diagrams/2025-10-09-work-map.md'] ?? '').toContain('```mermaid\nflowchart TD\n  sh[fetch_transcript.sh]')
  expect(copied[0] ?? '').toStartWith('```mermaid')
})
