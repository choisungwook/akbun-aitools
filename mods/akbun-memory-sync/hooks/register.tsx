import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Candidate } from '../types'

const PLUGIN = 'akbun-memory-sync'
const AUTO_KEY = 'auto'
const MAX_REFERENCED = 10

const pending = atom({ plugin: 'akbun-memory-sync', key: 'pending' } as const, [])

const EXTRACT_SYSTEM = `너는 Claude Code 세션에서 사용자가 말한 내용 중 "앞으로도 지켜야 할 규칙"만 골라내는 분류기다.
규칙이란 이번 작업 하나에만 적용되는 요청이 아니라, 다음 세션에서도 같은 상황에 반복 적용되는 지시다.
예: "앞으로 커밋 메시지는 한국어로", "이 저장소에서는 테스트를 먼저 돌려", "다시는 README를 자동으로 고치지 마".
예가 아닌 것: "이 파일 고쳐줘", "지금 테스트 돌려봐", 질문, 감탄.
출력은 JSON 배열만. 각 원소는 {"rule": "<한 문장, 명령형>", "source": "<근거가 된 사용자 문장 일부>"}.
규칙이 없으면 [] 만 출력한다. 설명을 붙이지 않는다.`

async function memoryFiles($: EngineInterface): Promise<string[]> {
  const root = await $.session.root()
  const primary = (await $.fs.exists(`${root}/AGENTS.md`)) ? 'AGENTS.md' : 'CLAUDE.md'
  if (!(await $.fs.exists(`${root}/${primary}`))) return []

  const text = await $.fs.read(`${root}/${primary}`)
  const found = new Set<string>()
  for (const m of text.matchAll(/`([\w./-]+\.md)`|\]\(([\w./-]+\.md)\)/g)) {
    const path = (m[1] ?? m[2] ?? '').replace(/^\.\//, '')
    if (path && path !== primary && !path.includes('..')) found.add(path)
  }

  const referenced: string[] = []
  for (const path of found) {
    if (referenced.length >= MAX_REFERENCED) break
    if (await $.fs.exists(`${root}/${path}`)) referenced.push(path)
  }

  return [primary, ...referenced]
}

function parseCandidates(text: string): Candidate[] {
  const start = text.indexOf('[')
  const end = text.lastIndexOf(']')
  if (start < 0 || end <= start) return []
  try {
    const list = JSON.parse(text.slice(start, end + 1)) as unknown
    if (!Array.isArray(list)) return []
    return list
      .filter((c): c is Candidate => typeof c === 'object' && c !== null && typeof (c as Candidate).rule === 'string')
      .map(c => ({ rule: c.rule.trim(), source: String(c.source ?? '').trim() }))
      .filter(c => c.rule.length > 0)
  } catch {
    return []
  }
}

async function extract($: EngineInterface, userTexts: string[]): Promise<Candidate[]> {
  const joined = userTexts.join('\n---\n').slice(0, 12000)
  if (joined.trim().length === 0) return []

  const r = await $.model.complete({
    model: 'haiku',
    system: EXTRACT_SYSTEM,
    prompt: `사용자 발화:\n${joined}`,
    maxTokens: 800,
  })

  return r.isAnswered ? parseCandidates(r.text) : []
}

function applyPrompt(files: string[], list: Candidate[]): string {
  const rules = list.map(c => `- ${c.rule}${c.source ? ` (근거: "${c.source}")` : ''}`).join('\n')
  const targets = files.map(f => `- ${f}`).join('\n')

  return [
    `[${PLUGIN}] 이번 세션 사용자 지시에서 뽑은 규칙 후보다. 메모리 파일에 반영해라.`,
    '규칙:',
    '- 규칙마다 아래 메모리 파일 중 가장 맞는 자리에 넣는다. 첫 파일이 원본이고 나머지는 그 파일이 참조하는 문서다.',
    '- 같은 뜻의 규칙이 이미 있으면 추가하지 않고 "이미 있음"으로 보고한다.',
    '- 기존 문체와 섹션 구조를 따르고, 새 파일이나 새 섹션은 만들지 않는다.',
    '- 끝나면 고친 파일과 추가한 줄만 짧게 보고한다.',
    '',
    '메모리 파일:',
    targets,
    '',
    '규칙 후보:',
    rules,
  ].join('\n')
}

export const register: Register = on => {
  let userTexts: string[] = []

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'memory-sync',
      description: '세션 전체에서 규칙 후보를 뽑아 AGENTS.md와 참조 문서에 반영. auto on|off|status',
      argumentHint: '[auto on|off|status]',
    })

    return next(e)
  })

  on('prompt.compose', async ($, e, next) => {
    const result = await next(e)
    const files = await memoryFiles($)
    if (files.length === 0) return result

    const section = {
      id: `${PLUGIN}:memory-files`,
      scope: 'session' as const,
      text: `이 저장소의 메모리(규칙) 원본은 ${files[0]}이고, 그 파일이 참조하는 문서는 ${files.slice(1).join(', ') || '없음'}이다. 사용자가 "기억해", "앞으로는", "다시는" 같은 반복 규칙을 말하면 별도 메모리 파일이 아니라 이 파일들 중 맞는 곳에 남긴다.`,
    }

    return { sections: [...result.sections, section] }
  })

  on('prompt.submit', ($, e, next) => {
    if (e.text.startsWith('/') || e.text.startsWith(`[${PLUGIN}]`)) return next(e)
    userTexts = [...userTexts, e.text]

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || e.reason !== 'answer' || userTexts.length === 0) return result

    const texts = userTexts
    userTexts = []
    const found = await extract($, texts)
    if (found.length === 0) return result

    const files = await memoryFiles($)
    if (files.length === 0) return result

    if ((await $.store.get(AUTO_KEY)) === true) {
      await $.prompt.submit({ text: applyPrompt(files, found) })
      $.ui.toast(`${PLUGIN}: 규칙 ${found.length}개를 ${files[0]}에 반영 중`)
    } else {
      await update($, pending, list => [...list, ...found].slice(-10))
    }

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const list = await read($, pending)
    if (e.props.hasSurvey || list.length === 0) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const first = list[0]

    return (
      <Box>
        <Text dimColor>메모리 후보 {list.length}개: </Text>
        <Text>{first?.rule.slice(0, 60)}</Text>
        <Text> </Text>
        <Button
          key="apply"
          label="반영"
          onPress={async () => {
            const files = await memoryFiles($)
            await update($, pending, () => [])
            await $.prompt.submit({ text: applyPrompt(files, list) })
          }}
        />
        <Text> </Text>
        <Button key="dismiss" label="무시" onPress={() => update($, pending, () => [])} />
      </Box>
    )
  })

  on('command.run', { command: 'memory-sync' }, async ($, e) => {
    const args = e.args.trim()

    if (args === 'auto on' || args === 'auto off') {
      await $.store.set(AUTO_KEY, args === 'auto on')

      return { text: `${PLUGIN}: 자동 반영 ${args === 'auto on' ? '켬' : '끔'}` }
    }
    if (args === 'auto status' || args === 'status') {
      const files = await memoryFiles($)

      return {
        text: `${PLUGIN}: 자동 반영 ${(await $.store.get(AUTO_KEY)) === true ? '켜짐' : '꺼짐'}, 메모리 파일: ${files.join(', ') || '없음'}`,
      }
    }

    const files = await memoryFiles($)
    if (files.length === 0) return { text: `${PLUGIN}: 작업 디렉터리에 AGENTS.md나 CLAUDE.md가 없다.` }

    const rows = await $.session.messages()
    const texts = rows.filter(r => r.role === 'user' && !r.text.startsWith('/')).map(r => r.text)
    const found = await extract($, texts)
    if (found.length === 0) return { text: `${PLUGIN}: 세션에서 반복 규칙을 찾지 못했다.` }

    await update($, pending, () => [])
    await $.prompt.submit({ text: applyPrompt(files, found) })

    return { text: `${PLUGIN}: 규칙 후보 ${found.length}개를 ${files[0]}에 반영하는 턴을 큐에 넣었다.` }
  })
}
