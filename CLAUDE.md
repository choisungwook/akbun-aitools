# For Claude

AI도구를 관리합니다.

## don't do it

- 아첨 하지 마세요. ex: 좋은 질문입니다.
- 읽었던 파일을 다시 읽지마세요. 단, sha256 값이 바뀌면 다시 읽으세요

## Tools Validation

1. 모든 리소스(skills, agents, hooks 등) 이름은 `akbun-` prefix 사용
2. 부정어 검사 및 수정 — [docs/negative-instruction-detection.md](docs/negative-instruction-detection.md)
