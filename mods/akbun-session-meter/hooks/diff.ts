import type { EngineInterface } from 'claude-code'

import type { DiffFile, DiffSnapshot } from '../types'

const MAX_FILES = 50
const MAX_PATCH_LINES = 400

// git diff 출력 하나(파일 1개)에서 경로·상태·증감·hunk를 꺼낸다
export function parseFileDiff(block: string): DiffFile | null {
  const lines = block.split('\n')
  const header = lines[0]?.match(/^diff --git a\/(.+) b\/(.+)$/)
  if (!header) return null

  const path = header[2] ?? header[1] ?? ''
  const status = lines.some(l => l.startsWith('new file mode'))
    ? 'added'
    : lines.some(l => l.startsWith('deleted file mode'))
      ? 'deleted'
      : 'modified'
  const hunkStart = lines.findIndex(l => l.startsWith('@@'))
  const hunks = hunkStart === -1 ? [] : lines.slice(hunkStart).filter(l => l !== '\\ No newline at end of file')
  const additions = hunks.filter(l => l.startsWith('+')).length
  const deletions = hunks.filter(l => l.startsWith('-')).length
  const isTruncated = hunks.length > MAX_PATCH_LINES

  return {
    path,
    status,
    additions,
    deletions,
    isBinary: hunkStart === -1 && lines.some(l => l.startsWith('Binary files')),
    isTruncated,
    patch: cutAtHunk(hunks, MAX_PATCH_LINES).join('\n'),
  }
}

// hunk 중간에서 자르면 Code diff가 파싱하지 못하므로 마지막 온전한 hunk까지만 남긴다
function cutAtHunk(hunks: string[], limit: number) {
  if (hunks.length <= limit) return hunks
  const lastHeader = hunks.slice(0, limit + 1).findLastIndex(l => l.startsWith('@@'))
  return lastHeader > 0 ? hunks.slice(0, lastHeader) : hunks.slice(0, 0)
}

export function parseGitDiff(output: string): DiffFile[] {
  return output
    .split(/^(?=diff --git )/m)
    .map(parseFileDiff)
    .filter((file): file is DiffFile => file !== null)
}

export async function readGitDiff($: EngineInterface): Promise<DiffSnapshot> {
  const top = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  if (top.exitCode !== 0) return { isGitRepo: false, files: [] }
  const cwd = top.stdout.trim()

  const tracked = await $.process.run(['git', 'diff', 'HEAD', '--no-color', '--no-ext-diff'], { cwd })
  const files = parseGitDiff(tracked.stdout)

  const untracked = await $.process.run(['git', 'ls-files', '--others', '--exclude-standard', '-z'], { cwd })
  const newPaths = untracked.stdout.split('\0').filter(Boolean).slice(0, MAX_FILES)
  for (const path of newPaths) {
    const added = await $.process.run(['git', 'diff', '--no-color', '--no-index', '--', '/dev/null', path], { cwd })
    const file = parseFileDiff(added.stdout.replace(/^diff --git a\/dev\/null b\//, `diff --git a/${path} b/`))
    if (file) files.push({ ...file, path, status: 'added' })
  }

  return { isGitRepo: true, files: files.slice(0, MAX_FILES) }
}
