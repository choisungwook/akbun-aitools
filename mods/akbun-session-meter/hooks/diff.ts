import type { EngineInterface } from 'claude-code'

import type { DiffFile, DiffSnapshot } from '../types'

const MAX_FILES = 50
const MAX_PATCH_LINES = 400
const EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
// 한글 경로를 따옴표·8진수로 바꾸지 않게 하고, rename은 삭제+추가로 나눠 경로를 단순하게 둔다
const GIT = ['git', '-c', 'core.quotePath=false']
const DIFF_FLAGS = ['--no-color', '--no-ext-diff', '--no-renames']

// Code의 source는 tab·newline 외 제어 문자를 받지 않는다
const clean = (line: string) => line.replace(/\r$/, '').replace(/[\u0000-\u0008\u000b-\u001f\u007f]/g, '')

// rename을 끈 diff는 a/와 b/ 경로가 같으므로 헤더 길이로 경로를 자른다. 경로에 ' b/'가 있어도 맞다
function pathFromHeader(header: string) {
  const body = header.slice('diff --git a/'.length)
  const pathLength = (body.length - ' b/'.length) / 2
  return Number.isInteger(pathLength) && pathLength > 0 ? body.slice(0, pathLength) : null
}

// 공백이 든 경로는 ---/+++ 줄 끝에 tab이 붙는다
function pathFromMarkers(lines: string[]) {
  const added = lines.find(l => l.startsWith('+++ b/'))
  if (added) return added.slice('+++ b/'.length).replace(/\t$/, '')
  const removed = lines.find(l => l.startsWith('--- a/'))
  return removed ? removed.slice('--- a/'.length).replace(/\t$/, '') : null
}

// 잘린 hunk의 @@ 줄 수를 남긴 줄에 맞춰 다시 써서 Code diff가 파싱할 수 있게 한다
function fixLastHunkHeader(lines: string[]) {
  const headerIndex = lines.findLastIndex(l => l.startsWith('@@'))
  if (headerIndex === -1) return lines
  const match = lines[headerIndex]?.match(/^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)$/)
  if (!match) return lines
  const body = lines.slice(headerIndex + 1)
  const oldCount = body.filter(l => l.startsWith(' ') || l.startsWith('-')).length
  const newCount = body.filter(l => l.startsWith(' ') || l.startsWith('+')).length
  const header = `@@ -${match[1]},${oldCount} +${match[2]},${newCount} @@${match[3] ?? ''}`
  return [...lines.slice(0, headerIndex), header, ...body]
}

export function parseFileDiff(block: string): DiffFile | null {
  const lines = block.split('\n').map(clean)
  const header = lines[0] ?? ''
  if (!header.startsWith('diff --git ')) return null

  const path = pathFromMarkers(lines) ?? pathFromHeader(header)
  if (!path) return null

  const status = lines.some(l => l.startsWith('new file mode'))
    ? 'added'
    : lines.some(l => l.startsWith('deleted file mode'))
      ? 'deleted'
      : 'modified'
  const hunkStart = lines.findIndex(l => l.startsWith('@@'))
  const hunks = hunkStart === -1 ? [] : lines.slice(hunkStart).filter(l => l !== '\\ No newline at end of file' && l !== '')
  const isTruncated = hunks.length > MAX_PATCH_LINES

  return {
    path,
    status,
    additions: hunks.filter(l => l.startsWith('+')).length,
    deletions: hunks.filter(l => l.startsWith('-')).length,
    isBinary: hunkStart === -1 && lines.some(l => l.startsWith('Binary files')),
    isTruncated,
    patch: (isTruncated ? fixLastHunkHeader(hunks.slice(0, MAX_PATCH_LINES)) : hunks).join('\n'),
  }
}

export function parseGitDiff(output: string): DiffFile[] {
  return output
    .split(/^(?=diff --git )/m)
    .map(parseFileDiff)
    .filter((file): file is DiffFile => file !== null)
}

export async function readGitDiff($: EngineInterface): Promise<DiffSnapshot> {
  const top = await $.process.run([...GIT, 'rev-parse', '--show-toplevel'])
  if (top.exitCode !== 0) return { isGitRepo: false, files: [], hiddenCount: 0, isOutputTruncated: false }
  const cwd = top.stdout.trim()

  // 커밋이 없는 저장소는 HEAD가 없으므로 빈 tree와 비교한다
  const head = await $.process.run([...GIT, 'rev-parse', '--verify', '-q', 'HEAD'], { cwd })
  const base = head.exitCode === 0 ? 'HEAD' : EMPTY_TREE

  const tracked = await $.process.run([...GIT, 'diff', ...DIFF_FLAGS, base], { cwd })
  const files = tracked.exitCode === 0 ? parseGitDiff(tracked.stdout) : []

  const untracked = await $.process.run([...GIT, 'ls-files', '--others', '--exclude-standard', '-z'], { cwd })
  const newPaths = untracked.stdout.split('\0').filter(Boolean)
  const roomForNew = Math.max(0, MAX_FILES - files.length)
  for (const path of newPaths.slice(0, roomForNew)) {
    const added = await $.process.run([...GIT, 'diff', ...DIFF_FLAGS, '--no-index', '--', '/dev/null', path], { cwd })
    const file = parseFileDiff(added.stdout)
    if (file) files.push({ ...file, path, status: 'added' })
  }

  const totalCount = files.length + Math.max(0, newPaths.length - roomForNew)
  return {
    isGitRepo: true,
    files: files.slice(0, MAX_FILES),
    hiddenCount: Math.max(0, totalCount - MAX_FILES),
    isOutputTruncated: tracked.isStdoutTruncated === true,
  }
}
