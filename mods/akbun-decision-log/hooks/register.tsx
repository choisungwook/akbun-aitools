import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Decision } from '../types'

const PLUGIN = 'akbun-decision-log'
const ADR_DIR = 'docs/adr'

const pending = atom({ plugin: 'akbun-decision-log', key: 'pending' } as const, null)

const DETECT_SYSTEM = `너는 Claude Code 세션 한 턴을 읽고 "되돌리기 어려운 결정"이 내려졌는지 판단하는 분류기다.
결정의 조건: (1) 대안이 2개 이상 거론됐고 (2) 그중 하나를 골랐고 (3) 고른 이유가 드러난다.
단순 구현, 버그 수정, 질문과 답, 작은 네이밍 선택은 결정이 아니다.
결정이면 JSON 객체 하나만 출력한다:
{"title": "<결정을 한 문장으로>", "slug": "<영문 소문자-하이픈 5단어 이내>", "scope": "<영향 범위: plugin/skill/디렉터리 이름>", "decision": "<무엇을 골랐나 1~2문장>", "reason": "<왜 1~3문장>", "rejected": ["<버린 대안과 이유>", "..."]}
결정이 아니면 NONE 만 출력한다. 설명을 붙이지 않는다.`

const DRAFT_PROMPT = (hint: string) => `[${PLUGIN}] 지금까지의 대화에서 다음 결정을 결정 기록(ADR)으로 정리해라: "${hint}".
대화에 근거가 없으면 지어내지 말고 hint만으로 쓴다.
JSON 객체 하나만 출력한다:
{"title": "<결정을 한 문장으로>", "slug": "<영문 소문자-하이픈 5단어 이내>", "scope": "<영향 범위>", "decision": "<무엇을 골랐나 1~2문장>", "reason": "<왜 1~3문장>", "rejected": ["<버린 대안과 이유>"]}`

function parseDecision(text: string): Decision | null {
  const start = text.indexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end <= start) return null
  try {
    const d = JSON.parse(text.slice(start, end + 1)) as Partial<Decision>
    if (typeof d.title !== 'string' || typeof d.decision !== 'string') return null

    return {
      title: d.title.trim(),
      slug: String(d.slug ?? 'decision').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'decision',
      scope: String(d.scope ?? '').trim(),
      decision: d.decision.trim(),
      reason: String(d.reason ?? '').trim(),
      rejected: Array.isArray(d.rejected) ? d.rejected.map(String) : [],
    }
  } catch {
    return null
  }
}

async function nextNumber($: EngineInterface, dir: string): Promise<string> {
  const entries = (await $.fs.exists(dir)) ? await $.fs.list(dir) : []
  let max = 0
  for (const e of entries) {
    const m = /^(\d{4})-/.exec(e.name)
    if (m) max = Math.max(max, Number(m[1]))
  }

  return String(max + 1).padStart(4, '0')
}

function render(d: Decision, date: string, sessionId: string): string {
  const rejected = d.rejected.length > 0 ? d.rejected.map(r => `- ${r}`).join('\n') : '- 없음'

  return [
    `# ${d.title}`,
    '',
    `Scope: ${d.scope || '미지정'}`,
    '',
    '## Decision',
    '',
    d.decision,
    '',
    '## Reason',
    '',
    d.reason || '(이유 미기록)',
    '',
    '## Rejected alternatives',
    '',
    rejected,
    '',
    '## Source',
    '',
    `- ${date} Claude Code 세션 ${sessionId}`,
    '',
  ].join('\n')
}

async function writeAdr($: EngineInterface, d: Decision): Promise<string> {
  const root = await $.session.root()
  const dir = `${root}/${ADR_DIR}`
  const number = await nextNumber($, dir)
  const file = `${number}-${d.slug}.md`
  const date = new Date(await $.clock.now()).toISOString().slice(0, 10)

  await $.fs.write(`${dir}/${file}`, render(d, date, await $.session.id()))

  const index = `${dir}/README.md`
  if (await $.fs.exists(index)) {
    const text = await $.fs.read(index)
    const row = `| [${number}](${file}) | ${d.scope || '-'} | ${d.title} |`
    await $.fs.write(index, text.replace(/\s*$/, '') + '\n' + row + '\n')
  }

  return `${ADR_DIR}/${file}`
}

export const register: Register = on => {
  let userTexts: string[] = []

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'decision',
      description: '대화 맥락으로 결정 기록(ADR)을 docs/adr/에 작성. list 는 기존 기록 목록',
      argumentHint: '<결정 한 줄> | list',
    })

    return next(e)
  })

  on('prompt.submit', ($, e, next) => {
    if (!e.text.startsWith('/') && !e.text.startsWith('[')) userTexts = [...userTexts, e.text]

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || e.reason !== 'answer') return result

    const texts = userTexts
    userTexts = []
    if (texts.length === 0) return result

    const r = await $.model.complete({
      model: 'haiku',
      system: DETECT_SYSTEM,
      prompt: `사용자:\n${texts.join('\n---\n').slice(0, 6000)}\n\n어시스턴트 답변:\n${e.answer.slice(0, 6000)}`,
      maxTokens: 600,
    })
    if (!r.isAnswered) return result

    const found = parseDecision(r.text)
    if (found) await update($, pending, () => found)

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const d = await read($, pending)
    if (e.props.hasSurvey || d === null) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text dimColor>결정 감지: </Text>
        <Text>{d.title.slice(0, 60)}</Text>
        <Text> </Text>
        <Button
          key="record"
          label="기록"
          onPress={async () => {
            await update($, pending, () => null)
            const path = await writeAdr($, d)
            $.ui.toast(`${PLUGIN}: ${path} 작성`)
          }}
        />
        <Text> </Text>
        <Button key="dismiss" label="무시" onPress={() => update($, pending, () => null)} />
      </Box>
    )
  })

  on('command.run', { command: 'decision' }, async ($, e) => {
    const hint = e.args.trim()
    const root = await $.session.root()

    if (hint === 'list') {
      const dir = `${root}/${ADR_DIR}`
      const names = (await $.fs.exists(dir)) ? (await $.fs.list(dir)).map(f => f.name).filter(n => /^\d{4}-/.test(n)).sort() : []

      return { text: names.length > 0 ? names.join('\n') : `${PLUGIN}: ${ADR_DIR} 에 기록이 없다.` }
    }

    if (hint.length === 0) {
      const d = await read($, pending)
      if (d === null) return { text: `${PLUGIN}: 결정 한 줄을 인자로 주거나, 감지된 결정이 있을 때 다시 실행해라.` }
      await update($, pending, () => null)

      return { text: `${PLUGIN}: ${await writeAdr($, d)} 작성` }
    }

    const r = await $.model.fork({ prompt: DRAFT_PROMPT(hint) })
    const d = r.isAnswered ? parseDecision(r.text) : null
    if (d === null) {
      return { text: `${PLUGIN}: 초안 생성 실패 (${r.isAnswered ? 'JSON 아님' : r.reason})` }
    }
    await update($, pending, () => null)

    return { text: `${PLUGIN}: ${await writeAdr($, d)} 작성\n\n${d.title}\n${d.decision}` }
  })
}
