import type { RenderElement } from 'claude-code'
import type { TestBody } from 'claude-code/testing'
import { expect, mock, test } from 'claude-code/testing'

import { insertIntoSection, lastExchange, lineDiff, outline, parseEdits } from './register'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const BAND = { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80, scroll: { offset: 0, bodyRows: 3 }, view: {} }
const PANE = { title: 'Memory', isFocused: false, bodyColumns: 80, placement: 'dock' as const, scroll: { offset: 0, bodyRows: 20 }, view: {} }

const AGENTS = '# AGENTS.md\n\n## 읽는 순서\n\n1. 이 파일.\n\n## 플러그인 변경 규칙\n\n- 버전을 올린다.\n- `docs/rules.md`도 본다.\n\n## 완료 전 확인\n\n- 표를 갱신했는가?\n'
const RULES = '# 규칙\n\n## 커밋\n\n- 작게 나눈다.\n'
const FORK_REPLY = '{"edits": [{"file": "AGENTS.md", "section": "## 플러그인 변경 규칙", "lines": ["- 커밋 메시지는 한국어로 쓴다."]}]}'

function world(on: Parameters<TestBody>[1], files: Record<string, string>, verdict = 'UPDATE: 커밋 메시지는 한국어로', counts = { command: 0 }) {
  mock.env(on, { AKBUN_MEMORY_SYNC_WAIT: '1' })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('command.register', (_, e) => {
    counts.command += 1

    return { value: { command: e.name } }
  })
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('fs.exists', (_, e) => ({ value: e.path.replace('/repo/', '') in files }))
  on('fs.read', (_, e) => ({ value: files[e.path.replace('/repo/', '')] ?? '' }))
  on('fs.write', (_, e) => {
    files[e.path.replace('/repo/', '')] = e.text

    return { value: undefined }
  })
  on('session.messages', () => ({ value: [
    { role: 'user' as const, text: '앞으로 커밋 메시지는 한국어로 써', toolUses: [] },
    { role: 'assistant' as const, text: '알겠다.', toolUses: [] },
  ] }))
  on('model.complete', () => ({ value: { isAnswered: true as const, text: verdict, usage: USAGE } }))
  on('model.fork', () => ({ value: { isAnswered: true as const, text: FORK_REPLY, usage: USAGE } }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.compose', () => ({ sections: [] }))
  on('ui.render', () => h('Text', { dimColor: true }, '-') as RenderElement)
}

test('insertIntoSection 은 섹션 끝에 줄을 붙이고 같은 줄은 건너뛴다', async () => {
  const once = insertIntoSection(AGENTS, '## 플러그인 변경 규칙', ['- 커밋 메시지는 한국어로 쓴다.'])
  expect(once ?? '').toContain('- `docs/rules.md`도 본다.\n- 커밋 메시지는 한국어로 쓴다.\n\n## 완료 전 확인')
  expect(insertIntoSection(once ?? '', '## 플러그인 변경 규칙', ['- 커밋 메시지는 한국어로 쓴다.'])).toBe(once)
  expect(insertIntoSection(AGENTS, '## 없는 섹션', ['- x'])).toBeNull()
  expect(insertIntoSection(RULES, '## 커밋', ['- 한국어로 쓴다.']) ?? '').toEndWith('- 작게 나눈다.\n- 한국어로 쓴다.\n')
})

test('parseEdits 는 허용된 파일만 남기고 outline 은 제목 줄만 뽑는다', async () => {
  const edits = parseEdits('설명 {"edits": [{"file": "./AGENTS.md", "section": " ## 읽는 순서 ", "lines": ["- a", ""]}, {"file": "/etc/x.md", "section": "## x", "lines": ["- b"]}]}', ['AGENTS.md'])
  expect(edits).toEqual([{ file: 'AGENTS.md', section: '## 읽는 순서', lines: ['- a'] }])
  expect(outline(AGENTS)).toEqual(['# AGENTS.md', '## 읽는 순서', '## 플러그인 변경 규칙', '## 완료 전 확인'])
  expect(lineDiff('a\nb', 'a\nb\nc')).toEqual({ added: 1, removed: 0 })
  expect(lastExchange([
    { role: 'user', text: 'old', toolUses: [] },
    { role: 'assistant', text: 'x', toolUses: [] },
    { role: 'user', text: '기억해', toolUses: [] },
    { role: 'assistant', text: '응', toolUses: [{ tool_use_id: 't', tool: 'Read', input: {} }] },
  ])).toBe('USER: 기억해\nASSISTANT: 응\nTOOL: Read')
})

test('규칙을 말한 턴이 끝나면 fork 가 고른 섹션에 줄이 들어가고 띠와 pane 에 +1 이 뜬다', async ($, on) => {
  const files: Record<string, string> = { 'AGENTS.md': AGENTS, 'docs/rules.md': RULES }
  world(on, files)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: '알겠다.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })

  expect(files['AGENTS.md']).toContain('- 커밋 메시지는 한국어로 쓴다.\n\n## 완료 전 확인')
  expect(files['docs/rules.md']).toBe(RULES)

  const band = await $.ui.mount({ plugin: 'akbun-memory-sync', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await band.find({ type: 'Text', text: /AGENTS\.md/ })).toBeDefined()
  expect(await band.find({ type: 'Text', text: /\+1/ })).toBeDefined()
  await band.unmount()

  const pane = await $.ui.mount({ plugin: 'akbun-memory-sync', surface: 'terminal', component: 'Pane', requestId: 'memory', props: PANE })
  expect(await pane.find({ type: 'Text', text: /메모리 파일 1개 변경/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /~ AGENTS\.md/ })).toBeDefined()
  await pane.unmount()
})

test('되돌리기 를 누르면 반영 전 내용으로 돌아간다', async ($, on) => {
  const files: Record<string, string> = { 'AGENTS.md': AGENTS }
  world(on, files)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: '알겠다.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  expect(files['AGENTS.md']).not.toBe(AGENTS)

  const band = await $.ui.mount({ plugin: 'akbun-memory-sync', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  await $.ui.press({ plugin: 'akbun-memory-sync', key: 'undo' })
  expect(files['AGENTS.md']).toBe(AGENTS)
  expect(await band.find({ type: 'Text', text: /되돌림/ })).toBeDefined()
  await band.unmount()
})

test('haiku 가 SKIP 이면 파일을 건드리지 않고 띠도 없다', async ($, on) => {
  const files: Record<string, string> = { 'AGENTS.md': AGENTS }
  world(on, files, 'SKIP')

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: '고쳤다.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  expect(files['AGENTS.md']).toBe(AGENTS)

  const band = await $.ui.mount({ plugin: 'akbun-memory-sync', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await band.find({ type: 'Text', text: /메모리/ })).toBeUndefined()
  await band.unmount()
})

test('prompt.compose 에 메모리 파일 위치와 인계 문단이 붙는다', async ($, on) => {
  world(on, { 'AGENTS.md': AGENTS, 'docs/rules.md': RULES })

  const composed = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: ['terminal'], tools: [], outputStyle: null, traits: [] })
  const section = composed.sections.find(s => s.id === 'akbun-memory-sync:handoff')
  expect(section?.text ?? '').toContain('AGENTS.md')
  expect(section?.text ?? '').toContain('docs/rules.md')
})

test('headless 세션에는 명령과 pane 이 없지만 반영은 돈다', async ($, on) => {
  const files: Record<string, string> = { 'AGENTS.md': AGENTS }
  const counts = { command: 0 }
  world(on, files, undefined, counts)

  await $.session.start({ cwd: '/repo', surface: null, isInteractive: false })
  expect(counts.command).toBe(0)
  await $.turn.complete({ answer: '알겠다.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  expect(files['AGENTS.md']).toContain('커밋 메시지는 한국어로 쓴다.')
})
