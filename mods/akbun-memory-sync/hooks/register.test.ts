import { expect, mock, test } from 'claude-code/testing'

const USAGE = { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 }
const BAND = { hasSurvey: false, isWorking: false, maxRows: 3, bodyColumns: 80, scroll: { offset: 0, bodyRows: 3 }, view: {} }

function world(on: Parameters<Parameters<typeof test>[1]>[1], submitted: string[]) {
  mock.store(on)
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.root', () => ({ value: '/repo' }))
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('fs.exists', (_, e) => ({ value: ['/repo/AGENTS.md', '/repo/docs/rules.md'].includes(e.path) }))
  on('fs.read', () => ({ value: '규칙은 `docs/rules.md`도 본다. `missing.md`는 없다.' }))
  on('model.complete', () => ({ value: {
    isAnswered: true as const,
    text: '[{"rule": "커밋 메시지는 한국어로 쓴다", "source": "앞으로 커밋 메시지는 한국어로"}]',
    usage: USAGE,
  } }))
  on('prompt.submit', (_, e) => {
    submitted.push(e.text)

    return { text: e.text }
  })
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.compose', () => ({ sections: [] }))
}

test('규칙이 담긴 턴이 끝나면 띠에 후보가 뜨고 반영을 누르면 AGENTS.md와 참조 문서를 고치는 턴이 큐에 들어간다', async ($, on) => {
  const submitted: string[] = []
  world(on, submitted)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  await $.prompt.submit({ text: '앞으로 커밋 메시지는 한국어로 써', wait: false, origin: { kind: 'composer' } })
  await $.turn.complete({ answer: '알겠다', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' })

  const ui = await $.ui.mount({ plugin: 'akbun-memory-sync', surface: 'terminal', component: 'AbovePrompt', props: BAND })
  expect(await ui.find({ type: 'Text', text: /커밋 메시지는 한국어로/ })).toBeDefined()

  await $.ui.press({ plugin: 'akbun-memory-sync', key: 'apply' })
  const last = submitted[submitted.length - 1] ?? ''
  expect(last).toContain('[akbun-memory-sync]')
  expect(last).toContain('- AGENTS.md')
  expect(last).toContain('- docs/rules.md')
  expect(last).toContain('커밋 메시지는 한국어로 쓴다')
  await ui.unmount()
})

test('prompt.compose 에 메모리 파일 위치를 알리는 섹션이 붙는다', async ($, on) => {
  world(on, [])

  const composed = await $.prompt.compose({ model: 'm', promptModel: 'm', surfaces: ['terminal'], tools: [], outputStyle: null, traits: [] })
  const section = composed.sections.find(s => s.id === 'akbun-memory-sync:memory-files')
  expect(section?.text ?? '').toContain('AGENTS.md')
  expect(section?.text ?? '').toContain('docs/rules.md')
})

test('/memory-sync auto on 뒤에는 띠 없이 바로 반영 턴이 큐에 들어간다', async ($, on) => {
  const submitted: string[] = []
  world(on, submitted)

  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  const r = await $.command.run({ command: 'memory-sync', args: 'auto on', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 80 } })
  expect(r.text ?? '').toContain('켬')

  await $.prompt.submit({ text: '다시는 README를 자동으로 고치지 마', wait: false, origin: { kind: 'composer' } })
  await $.turn.complete({ answer: '알겠다', durationMs: 1, isAborted: false, turnId: 't2', reason: 'answer' })
  expect(submitted.some(t => t.startsWith('[akbun-memory-sync]'))).toBe(true)
})
