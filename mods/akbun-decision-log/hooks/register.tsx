import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Option, Question } from '../types'

const PLUGIN = 'akbun-decision-log'
const PANE = 'decision'
const ADR_DIR = 'docs/adr'

const current = atom({ plugin: 'akbun-decision-log', key: 'current' } as const, null)
const dismissed = atom({ plugin: 'akbun-decision-log', key: 'dismissed' } as const, null)

const SHAPE =
  '{"title": "<결정 주제 한 줄, 예: 저장소 선택>", "slug": "<영문 소문자-하이픈 5단어 이내>", "scope": "<영향 범위: plugin/skill/디렉터리 이름, 저장소 전체면 repo>", ' +
  '"question": "<질문 한 줄>", "context": "<결정에 필요한 배경 1~2문장>", ' +
  '"options": [{"label": "<2~5단어>", "detail": "<무엇인지>", "leadsTo": "<고르면 다음에 일어나는 일>", "pros": ["<짧게>"], "cons": ["<짧게>"]}], ' +
  '"recommendation": {"label": "<옵션 label 하나>", "why": "<한 문장>"}}'

const EXPLAIN_PROMPT =
  `[${PLUGIN}] 이 메시지는 플러그인이 보낸 것이다. 네 마지막 답변은 사용자에게 질문으로 끝났다. 그 질문에 답하지 말고 도구도 쓰지 말고, 사용자가 답을 고르도록 선택지를 정리해라. ` +
  `네가 제시한 선택지를 그대로 쓰고, 제시한 것이 없으면 사용자가 고를 만한 답 2~4개를 만든다. pros와 cons는 각각 2개 이내. ` +
  `JSON 객체 하나만 답한다(코드 펜스 없이): ${SHAPE}`

const DRAFT_PROMPT = (hint: string) =>
  `[${PLUGIN}] 이 메시지는 플러그인이 보낸 것이다. 도구를 쓰지 말고 텍스트로만 답한다. 지금까지의 대화에서 다음 결정을 정리해라: "${hint}". ` +
  `options의 첫 원소가 고른 안이고 나머지는 버린 대안이다. 대화에 근거가 없으면 지어내지 말고 hint만으로 쓴다. JSON 객체 하나만 답한다: ${SHAPE}`

// 모델 호출 없는 1차 검사: 답변 끝이 질문인가, 또는 번호·글자 선택지가 2개 이상인가.
export function looksLikeQuestion(answer: string): boolean {
  const tail = answer.trim().slice(-1500)
  const paragraphs = tail.split(/\n\s*\n/)
  const last = (paragraphs[paragraphs.length - 1] ?? '').trim()
  if (/[?？]\s*(\*\*|_|`)?\s*$/.test(last)) return true
  const options = tail.match(/^\s*(\d+[.)]|[A-D][.):]|[-*]\s+\*\*)/gm) ?? []

  return options.length >= 2 && /(어느|어떤|고르|선택|원하|할까요|할까|which|prefer|choose|pick|should I)/i.test(tail)
}

export function parseQuestion(text: string): Omit<Question, 'id' | 'at' | 'status' | 'chosen' | 'written'> | null {
  const start = text.indexOf('{')
  const end = text.lastIndexOf('}')
  if (start < 0 || end <= start) return null
  try {
    const d = JSON.parse(text.slice(start, end + 1)) as Record<string, unknown>
    if (!Array.isArray(d.options) || d.options.length === 0) return null
    const options: Option[] = d.options
      .filter((o): o is Record<string, unknown> => typeof o === 'object' && o !== null && typeof o.label === 'string')
      .map(o => ({
        label: String(o.label).trim(),
        detail: String(o.detail ?? '').trim(),
        leadsTo: String(o.leadsTo ?? '').trim(),
        pros: Array.isArray(o.pros) ? o.pros.map(String) : [],
        cons: Array.isArray(o.cons) ? o.cons.map(String) : [],
      }))
    if (options.length === 0) return null
    const rec = d.recommendation as Record<string, unknown> | undefined
    const title = String(d.title ?? d.question ?? '결정').trim()

    return {
      title,
      slug: slugOf(String(d.slug ?? title)),
      scope: String(d.scope ?? '').trim(),
      question: String(d.question ?? '').trim(),
      context: String(d.context ?? '').trim(),
      options,
      recommendation: rec && typeof rec.label === 'string' ? { label: rec.label.trim(), why: String(rec.why ?? '').trim() } : null,
    }
  } catch {
    return null
  }
}

function slugOf(text: string): string {
  const ascii = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

  return ascii.length > 0 ? ascii.slice(0, 50) : 'decision'
}

const letter = (i: number) => String.fromCharCode(65 + i)

async function nextNumber($: EngineInterface, dir: string): Promise<string> {
  const entries = await $.fs.list(dir).catch(() => [])
  let max = 0
  for (const e of entries) {
    const m = /^(\d{4})-/.exec(e.name)
    if (m) max = Math.max(max, Number(m[1]))
  }

  return String(max + 1).padStart(4, '0')
}

export function renderAdr(q: Question, chosen: number, date: string, sessionId: string): string {
  const pick = q.options[chosen]
  if (!pick) return ''
  const rejected = q.options
    .filter((_, i) => i !== chosen)
    .map(o => `- ${o.label}${o.cons.length > 0 ? `: ${o.cons.join(', ')}` : o.detail ? `: ${o.detail}` : ''}`)
  const reasons = [...pick.pros, ...(q.recommendation && q.recommendation.label === pick.label ? [q.recommendation.why] : [])].filter(Boolean)

  return [
    `# ${q.title}: ${pick.label}`,
    '',
    `Scope: ${q.scope || '미지정'}`,
    '',
    '## Decision',
    '',
    pick.detail || pick.label,
    ...(pick.leadsTo ? ['', pick.leadsTo] : []),
    '',
    '## Reason',
    '',
    reasons.length > 0 ? reasons.map(r => `- ${r}`).join('\n') : '- (이유 미기록)',
    '',
    '## Rejected alternatives',
    '',
    rejected.length > 0 ? rejected.join('\n') : '- 없음',
    '',
    '## Source',
    '',
    `- ${date} Claude Code 세션 ${sessionId}`,
    ...(q.question ? [`- 질문: ${q.question}`] : []),
    '',
  ].join('\n')
}

async function writeAdr($: EngineInterface, q: Question, chosen: number): Promise<string> {
  const root = await $.session.root()
  const dir = `${root}/${ADR_DIR}`
  const number = await nextNumber($, dir)
  const pick = q.options[chosen]
  const file = `${number}-${slugOf(`${q.slug}-${pick?.label ?? ''}`)}.md`
  const date = new Date(await $.clock.now()).toISOString().slice(0, 10)

  await $.fs.write(`${dir}/${file}`, renderAdr(q, chosen, date, await $.session.id()))

  const index = `${dir}/README.md`
  if (await $.fs.exists(index)) {
    const text = await $.fs.read(index)
    const row = `| [${number}](${file}) | ${q.scope || '-'} | ${q.title}: ${pick?.label ?? ''} |`
    await $.fs.write(index, text.replace(/\s*$/, '') + '\n' + row + '\n')
  }

  return `${ADR_DIR}/${file}`
}

async function record($: EngineInterface, q: Question, chosen: number, own?: string) {
  let target = q
  let index = chosen
  if (own !== undefined) {
    const found = q.options.findIndex(o => o.label.toLowerCase() === own.toLowerCase())
    if (found >= 0) index = found
    else {
      target = { ...q, options: [...q.options, { label: own, detail: own, leadsTo: '', pros: [], cons: [], mine: true }] }
      index = target.options.length - 1
    }
  }
  const path = await writeAdr($, target, index)
  await update($, current, () => ({ ...target, chosen: index, written: path }))
  $.ui.toast(`${PLUGIN}: ${path} 작성`)

  return path
}

async function openPane($: EngineInterface, asked: boolean) {
  const opened = await $.ui.open(asked ? { id: PANE, title: 'Decision', focus: true, closeOnEscape: true, rows: 30 } : { id: PANE, title: 'Decision' })
  if (!opened.isPlaced && !asked) $.ui.toast(`${PLUGIN}: /decision 으로 pane을 연다`)
}

async function explain($: EngineInterface, answer: string) {
  const id = crypto.randomUUID()
  const blank: Question = {
    id,
    at: Date.now(),
    status: 'thinking',
    title: '',
    slug: 'decision',
    scope: '',
    question: answer.trim().split('\n').at(-1) ?? '',
    context: '',
    options: [],
    recommendation: null,
    chosen: null,
    written: null,
  }
  await update($, current, () => blank)
  await openPane($, false)

  const r = await $.model.fork({ prompt: EXPLAIN_PROMPT })
  const parsed = r.isAnswered ? parseQuestion(r.text) : null
  await update($, current, q =>
    q?.id !== id
      ? q
      : parsed
        ? { ...q, ...parsed, status: 'ready' as const }
        : { ...q, status: 'failed' as const, reason: r.isAnswered ? 'fork가 JSON으로 답하지 않음' : r.reason },
  )
}

// 사용자가 프롬프트로 답하면 어느 선택지인지 haiku가 고른다. A-H, OTHER, NONE 중 하나.
async function classifyAnswer($: EngineInterface, q: Question, text: string): Promise<number | 'other' | null> {
  const list = q.options.map((o, i) => `${letter(i)}. ${o.label}${o.detail ? ` (${o.detail})` : ''}`).join('\n')
  const r = await $.model.complete({
    model: 'haiku',
    system: '질문에 대한 사용자의 답이 어느 선택지인지 고른다. 선택지 글자 하나(A, B, ...)만 답한다. 선택지에 없는 다른 답을 골랐으면 OTHER, 아직 고르지 않았거나 다른 이야기면 NONE.',
    prompt: `질문: ${q.question}\n선택지:\n${list}\n\n사용자 답: ${text.slice(0, 1500)}`,
    maxTokens: 5,
    timeoutMs: 20000,
  })
  if (!r.isAnswered) return null
  const word = r.text.trim().toUpperCase()
  if (word.startsWith('OTHER')) return 'other'
  const i = word.charCodeAt(0) - 65

  return i >= 0 && i < q.options.length && /^[A-H]/.test(word) ? i : null
}

export const register: Register = on => {
  let isHeadless = false
  let answered: string | null = null

  on('session.start', async ($, e, next) => {
    isHeadless = e.isInteractive === false
    if (isHeadless) return next(e)
    await $.command.register({
      name: 'decision',
      description: '결정 pane을 연다. a~h 는 그 선택지로 ADR 기록, other <답> 은 직접 쓴 답으로 기록, list 는 기록 목록, <한 줄> 은 대화로 초안',
      argumentHint: '[a-h | other <답> | list | <결정 한 줄>]',
    })

    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    const q = await read($, current)
    if (q !== null && q.status === 'ready' && q.chosen === null && !e.text.startsWith('/')) answered = e.text

    return next(e)
  }).catch(($, e, next) => (next.called ? next(e) : next(e)))

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined || e.reason !== 'answer') return result
    const wait = (await $.env.get('AKBUN_DECISION_WAIT')) === '1'
    if (isHeadless && !wait) return result

    const q = await read($, current)
    const text = answered
    answered = null
    if (q !== null && q.status === 'ready' && q.chosen === null && text !== null) {
      const picked = await classifyAnswer($, q, text)
      if (picked === 'other') {
        await update($, current, cur => (cur?.id === q.id ? { ...cur, options: [...cur.options, { label: text.slice(0, 60), detail: text, leadsTo: '', pros: [], cons: [], mine: true }], chosen: cur.options.length } : cur))
        await update($, dismissed, () => null)

        return result
      }
      if (picked !== null) {
        await update($, current, cur => (cur?.id === q.id ? { ...cur, chosen: picked } : cur))
        await update($, dismissed, () => null)

        return result
      }
    }

    if (!looksLikeQuestion(e.answer)) return result
    const gate = await $.model.complete({
      model: 'haiku',
      system: 'AI 코딩 어시스턴트 답변의 끝을 읽는다. 작업을 이어가기 전에 사용자가 무엇을 결정하거나 고르거나 알려 줘야 하면 YES, 수사적 질문이나 "더 필요한 것 있나요?" 같은 인사, 보고만 하는 답이면 NO. YES 또는 NO만 답한다.',
      prompt: e.answer.trim().slice(-2000),
      maxTokens: 5,
      timeoutMs: 20000,
    })
    if (!(gate.isAnswered && /^\s*yes/i.test(gate.text))) return result

    const work = explain($, e.answer).catch(() => undefined)
    if (wait) await work

    return result
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const q = await read($, current)
    if (e.props.hasSurvey || q === null || q.status !== 'ready' || q.chosen === null || q.written !== null) return next(e)
    if (q.id === (await read($, dismissed))) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const pick = q.options[q.chosen]

    return (
      <Box>
        <Text dimColor>결정 감지: </Text>
        <Text>{`${letter(q.chosen)} ${pick?.label ?? ''}`.slice(0, 50)} </Text>
        <Button key="record" label="ADR 기록" onPress={() => record($, q, q.chosen ?? 0)} />
        <Text> </Text>
        <Button key="open" label="열기" onPress={() => openPane($, true)} />
        <Text> </Text>
        <Button key="dismiss" label="무시" onPress={() => update($, dismissed, () => q.id)} />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const elements = $.ui.resolve(e)
    const { Box, Button, Text } = elements
    const Input = 'Input' in elements ? elements.Input : null
    const q = await read($, current)
    if (q === null) return <Text dimColor>Claude가 선택지를 묻는 답을 하면 여기에 정리된다.</Text>
    if (q.status === 'thinking') return <Text color="yellow">대화를 읽어 선택지를 정리하는 중…</Text>
    if (q.status === 'failed') return <Text color="red">정리 실패: {q.reason}</Text>

    const pick = q.recommendation?.label ?? ''

    return (
      <Box flexDirection="column">
        <Box borderStyle="double" borderColor="cyan" paddingX={1} flexDirection="column">
          <Text bold color="cyan">{q.question || q.title}</Text>
          {q.context ? <Text dimColor>{q.context}</Text> : null}
        </Box>
        {q.options.map((o, i) => {
          const isPick = o.label === pick && !o.mine
          const isChosen = q.chosen === i
          const color = isChosen ? 'magenta' : isPick ? 'green' : o.mine ? 'yellow' : 'gray'

          return (
            <Box flexDirection="column">
              <Text dimColor>{'  │'}</Text>
              <Box borderStyle={isPick || isChosen ? 'bold' : 'round'} borderColor={color} paddingX={1} flexDirection="column">
                <Text bold color={color === 'gray' ? 'white' : color}>
                  {`${letter(i)}  ${o.label}${isPick ? '   ★ 추천' : ''}${o.mine ? '   ✎ 직접 쓴 답' : ''}${isChosen ? '   ● 선택됨' : ''}`}
                </Text>
                {o.detail ? <Text>{o.detail}</Text> : null}
                {o.leadsTo ? <Text color="blue">{`→ ${o.leadsTo}`}</Text> : null}
                {o.pros.map(p => <Text color="green">{`+ ${p}`}</Text>)}
                {o.cons.map(c => <Text color="red">{`- ${c}`}</Text>)}
                {q.written === null ? <Button key={`record-${letter(i).toLowerCase()}`} label="이 안으로 ADR 기록" onPress={() => record($, q, i)} /> : null}
              </Box>
            </Box>
          )
        })}
        {q.written === null && Input !== null ? (
          <Box flexDirection="column">
            <Text dimColor>{'  │'}</Text>
            <Box borderStyle="round" borderColor="gray" borderDimColor paddingX={1} flexDirection="column">
              <Text dimColor bold>{`${letter(q.options.length)}  직접 쓴 답`}</Text>
              <Input key="other" placeholder="고른 안을 한 줄로" submitLabel="ADR 기록" onSubmit={(value: string) => (value.trim() ? record($, q, -1, value.trim()) : undefined)} />
            </Box>
          </Box>
        ) : null}
        {pick ? <Text color="green">{`★ ${pick}: ${q.recommendation?.why ?? ''}`}</Text> : null}
        {q.written !== null ? <Text color="magenta">{`기록됨: ${q.written}`}</Text> : null}
        <Box gap={2} marginTop={1}>
          <Button key="close" label="닫기" onPress={() => $.ui.close({ id: PANE })} />
        </Box>
      </Box>
    )
  })

  on('command.run', { command: 'decision' }, async ($, e) => {
    const raw = e.args.trim()
    const arg = raw.toLowerCase()
    const root = await $.session.root()

    if (arg === 'list') {
      const names = (await $.fs.list(`${root}/${ADR_DIR}`).catch(() => [])).map(f => f.name).filter(n => /^\d{4}-/.test(n)).sort()

      return { text: names.length > 0 ? names.join('\n') : `${PLUGIN}: ${ADR_DIR} 에 기록이 없다.` }
    }

    const q = await read($, current)
    if (arg.length === 0) {
      await openPane($, true)

      return { text: q === null ? `${PLUGIN}: 아직 정리된 질문이 없다. 결정 한 줄을 인자로 주면 대화로 초안을 만든다.` : 'Decision pane 열림' }
    }

    if (q !== null && q.status === 'ready') {
      if (/^[a-h]$/.test(arg)) {
        const i = arg.charCodeAt(0) - 97
        if (i >= q.options.length) return { text: `${PLUGIN}: 선택지 ${letter(i)}가 없다.` }

        return { text: `${PLUGIN}: ${await record($, q, i)} 작성` }
      }
      if (/^other\s+\S/.test(arg)) return { text: `${PLUGIN}: ${await record($, q, -1, raw.replace(/^other\s+/i, ''))} 작성` }
    }

    const r = await $.model.fork({ prompt: DRAFT_PROMPT(raw) })
    const parsed = r.isAnswered ? parseQuestion(r.text) : null
    if (parsed === null) return { text: `${PLUGIN}: 초안 생성 실패 (${r.isAnswered ? 'JSON 아님' : r.reason})` }
    const draft: Question = { id: crypto.randomUUID(), at: Date.now(), status: 'ready', ...parsed, chosen: null, written: null }
    const path = await record($, draft, 0)
    await openPane($, true)

    return { text: `${PLUGIN}: ${path} 작성\n\n${draft.title}: ${draft.options[0]?.label ?? ''}\n${draft.options[0]?.detail ?? ''}` }
  })
}
