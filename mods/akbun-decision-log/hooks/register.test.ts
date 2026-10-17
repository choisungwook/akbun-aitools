import type { RenderElement } from 'claude-code'
import type { TestBody } from 'claude-code/testing'
import { expect, mock, test } from 'claude-code/testing'

import { looksLikeQuestion, parseQuestion } from './register'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const BAND = { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80, scroll: { offset: 0, bodyRows: 3 }, view: {} }
const PANE = { title: 'Decision', isFocused: false, bodyColumns: 80, placement: 'dock' as const, scroll: { offset: 0, bodyRows: 40 }, view: {} }
const ANSWER = '저장 방식은 세 가지다.\n\n1. JSON 파일\n2. SQLite\n3. Redis\n\n어느 것을 쓸까요?'
const EXPLAIN =
  '{"title": "저장소 선택", "slug": "storage-choice", "scope": "akbun-md-to-notion", "question": "어느 저장 방식을 쓸까?", "context": "단일 사용자 CLI다.", ' +
  '"options": [{"label": "JSON 파일", "detail": "파일 하나에 저장", "leadsTo": "직렬화 코드 작성", "pros": ["의존성 없음"], "cons": ["동시 쓰기 불가"]}, ' +
  '{"label": "SQLite", "detail": "내장 DB 파일", "leadsTo": "스키마 작성", "pros": ["쿼리 가능", "파일 하나"], "cons": ["드라이버 필요"]}, ' +
  '{"label": "Redis", "detail": "외부 서버", "leadsTo": "서버 운영", "pros": ["빠름"], "cons": ["서버가 필요"]}], ' +
  '"recommendation": {"label": "SQLite", "why": "파일 하나로 끝나고 쿼리가 된다."}}'

function world(on: Parameters<TestBody>[1], written: Record<string, string>, complete: (prompt: string) => string, counts = { fork: 0 }) {
  mock.clock(on, { now: 1_760_000_000_000 })
  mock.env(on, { AKBUN_DECISION_WAIT: '1' })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('session.id', () => ({ value: 'sess-1' }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('fs.exists', (_, e) => ({ value: e.path === '/repo/docs/adr' || e.path === '/repo/docs/adr/README.md' }))
  on('fs.list', () => ({ value: [{ name: '0006-old.md', kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false }, { name: 'README.md', kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false }] }))
  on('fs.read', () => ({ value: '# 결정 기록\n\n| 번호 | 범위 | 결정 |\n|---|---|---|\n| [0006](0006-old.md) | x | y |\n' }))
  on('fs.write', (_, e) => {
    written[e.path] = e.text

    return { value: undefined }
  })
  on('model.complete', (_, e) => ({ value: { isAnswered: true as const, text: complete(typeof e.prompt === 'string' ? e.prompt : ''), usage: USAGE } }))
  on('model.fork', () => {
    counts.fork += 1

    return { value: { isAnswered: true as const, text: EXPLAIN, usage: USAGE } }
  })
  on('prompt.submit', (_, e) => ({ text: e.text }))
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('ui.render', () => h('Text', { dimColor: true }, '-') as RenderElement)
}

const gateThenPick = (pick: string) => (prompt: string) => (prompt.startsWith('질문:') ? pick : 'YES')

test('looksLikeQuestion 은 물음표나 선택지 목록으로 끝나는 답만 잡는다', async () => {
  expect(looksLikeQuestion(ANSWER)).toBe(true)
  expect(looksLikeQuestion('A. 파일\nB. DB\n어느 쪽을 선택할까')).toBe(true)
  expect(looksLikeQuestion('파일을 고쳤다. 테스트도 통과했다.')).toBe(false)
  expect(parseQuestion('없음')).toBeNull()
  expect(parseQuestion(EXPLAIN)?.options.length).toBe(3)
})

test('질문으로 끝난 턴 뒤 pane 에 선택지가 뜨고, 버튼으로 고른 안이 ADR 과 색인 행으로 써진다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written, gateThenPick('NONE'))

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: ANSWER, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })

  const pane = await $.ui.mount({ plugin: 'akbun-decision-log', surface: 'terminal', component: 'Pane', requestId: 'decision', props: PANE })
  expect(await pane.find({ type: 'Text', text: /어느 저장 방식을 쓸까/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /B {2}SQLite {3}★ 추천/ })).toBeDefined()
  expect(await pane.find({ type: 'Text', text: /- 서버가 필요/ })).toBeDefined()

  await $.ui.press({ plugin: 'akbun-decision-log', key: 'record-b' })
  expect(await pane.find({ type: 'Text', text: /기록됨: docs\/adr\/0007-storage-choice-sqlite\.md/ })).toBeDefined()
  await pane.unmount()

  const adr = written['/repo/docs/adr/0007-storage-choice-sqlite.md'] ?? ''
  expect(adr).toStartWith('# 저장소 선택: SQLite')
  expect(adr).toContain('Scope: akbun-md-to-notion')
  expect(adr).toContain('## Reason\n\n- 쿼리 가능\n- 파일 하나\n- 파일 하나로 끝나고 쿼리가 된다.')
  expect(adr).toContain('## Rejected alternatives\n\n- JSON 파일: 동시 쓰기 불가\n- Redis: 서버가 필요')
  expect(adr).toContain('- 2025-10-09 Claude Code 세션 sess-1')
  expect(written['/repo/docs/adr/README.md'] ?? '').toEndWith('| [0007](0007-storage-choice-sqlite.md) | akbun-md-to-notion | 저장소 선택: SQLite |\n')
})

test('사용자가 프롬프트로 답하면 haiku 가 고른 선택지를 띠에 띄우고 ADR 기록 버튼이 파일을 쓴다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written, gateThenPick('A'))

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: ANSWER, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  await $.prompt.submit({ text: 'JSON 파일로 가자', wait: false, origin: { kind: 'composer' } })
  await $.turn.complete({ answer: 'JSON 파일로 구현한다.', durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer' })

  const band = await $.ui.mount({ plugin: 'akbun-decision-log', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await band.find({ type: 'Text', text: /A JSON 파일/ })).toBeDefined()
  await $.ui.press({ plugin: 'akbun-decision-log', key: 'record' })
  await band.unmount()

  expect(Object.keys(written)).toContain('/repo/docs/adr/0007-storage-choice-json.md')
  expect(written['/repo/docs/adr/0007-storage-choice-json.md'] ?? '').toContain('- SQLite: 드라이버 필요')
})

test('/decision other <답> 은 직접 쓴 답을 결정으로, 나머지를 버린 대안으로 기록한다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written, gateThenPick('NONE'))

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: ANSWER, durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  const r = await $.command.run({ command: 'decision', args: 'other DuckDB', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('docs/adr/0007-storage-choice-duckdb.md')
  const adr = written['/repo/docs/adr/0007-storage-choice-duckdb.md'] ?? ''
  expect(adr).toStartWith('# 저장소 선택: DuckDB')
  expect(adr).toContain('- SQLite: 드라이버 필요')
})

test('/decision <한 줄> 은 정리된 질문이 없어도 대화를 fork 해 ADR 을 쓰고, list 는 번호 파일만 나열한다', async ($, on) => {
  const written: Record<string, string> = {}
  world(on, written, () => 'NO')

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'decision', args: 'SQLite 우선', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('docs/adr/0007-storage-choice-json.md')
  expect(Object.keys(written)).toContain('/repo/docs/adr/0007-storage-choice-json.md')

  const list = await $.command.run({ command: 'decision', args: 'list', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(list.text).toBe('0006-old.md')
})

test('haiku 게이트가 NO 면 fork 도 pane 내용도 없다', async ($, on) => {
  const counts = { fork: 0 }
  world(on, {}, () => 'NO', counts)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.turn.complete({ answer: '더 필요한 것이 있나요?', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })
  expect(counts.fork).toBe(0)
})
