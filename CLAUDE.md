# For Claude

AI도구를 관리합니다.

## don't do it

- 아첨 하지 마세요. ex: 좋은 질문입니다.
- 읽었던 파일을 다시 읽지마세요. 단, sha256 값이 바뀌면 다시 읽으세요
- 답변을 생각하기 위한 시간을 버는 말은 짧게 변경하세요. "생각중.."

## Tools Validation

1. akbun이 직접 만든 리소스 이름은 `akbun-` prefix 사용 (`learning-*` 아래 학습용 skill은 예외 가능)
2. 부정어 검사 및 수정 — [docs/negative-instruction-detection.md](docs/negative-instruction-detection.md)
3. 배포용 plugin 리소스는 `plugins/<plugin-name>/...` 아래에서 관리
