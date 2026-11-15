# storyboard.json 형식과 검사

`dami_storyboard.py check`가 원본이다. 이 표의 숫자는 스크립트 상수와 같은 값이고, 어긋나면 스크립트가 맞다. 형식 예시는 [example/storyboard.json](example/storyboard.json)이다.

## 최상위 키

| 키 | 값 |
|---|---|
| `title` | 영상 제목(가제) |
| `genre` | [genres.jsonl](genres.jsonl)의 `id` |
| `message` | 핵심 메시지 한 문장 |
| `audience` | 누가 보나 |
| `intent` | 이 영상을 이렇게 구성한 의도 |
| `source_summary` | 입력(아이디어·글귀)을 요약한 2~4문장 |
| `answer_cut` | 훅이 건 약속이 화면에서 실제로 이루어지는 컷 번호(정수). 원리를 말로 설명하는 컷이 아니라 결과가 눈에 보이는 컷이다 |
| `reaction` | `{"cut", "text"}`. 시청자가 자기 경험을 말하거나 공유하고 싶게 만드는 공감 요소나 질문이 들어가는 컷 번호와 그 내용. 그 컷의 `narration`·`desc`·`overlay` 중 하나에 실제로 들어 있어야 한다 |
| `parts` | `[{"id", "title"}]`. 순서가 영상 순서. `id`는 중복 없이, 1~8개 |
| `music` | BGM 배열. 빈 배열 허용. 한 줄은 `id`(중복 없이), `from_cut`·`to_cut`(컷 번호, 둘 다 포함)과 [sound.md](sound.md)의 서술 키 |
| `cuts` | 컷 배열. 번호는 배열 순서(1부터) |

## 컷 키

| 키 | 값 |
|---|---|
| `part` | `parts`의 `id` |
| `dur` | 길이(초, 소수 허용). 시작 시각은 앞 컷 `dur`의 합이고 spec에 쓰지 않는다 |
| `shot` | [shots.jsonl](shots.jsonl)의 `id` |
| `move` | [moves.jsonl](moves.jsonl)의 `id` |
| `move_note` | 선택. 수치 메모(`100→140%, 0.3초`) |
| `source` | `화면 녹화`, `촬영`, `모션그래픽`, `사진·자료` 중 하나 |
| `sketch` | 스케치 영어 설명. [sketch.md](sketch.md) |
| `desc` | 화면에 무엇이 보이나 |
| `intent` | 왜 이렇게 그렸나 |
| `narration` | 이 컷에서 말할 대본. 없으면 빈 문자열 |
| `voice` | `live`, `adr`, `none` |
| `adr_reason` | `adr`이면 필수 |
| `overlay` | 선택. 위에 얹는 모션그래픽·자막 설명 |
| `sfx` | 선택. 효과음 서술 문자열 배열 |

## 검사 규칙

경계는 모두 포함이다. 실패 이유는 전부 모아 한 번에 출력하고 종료 코드는 1이다.

| 대상 | 규칙 |
|---|---|
| 필수 키 | 최상위 문자열 키와 컷의 `part`·`dur`·`shot`·`move`·`source`·`sketch`·`desc`·`intent`·`narration`·`voice`가 있고 문자열은 비어 있지 않다(`narration`만 빈 문자열 허용) |
| id | `genre`·`shot`·`move`는 jsonl에 있는 `id`, `part`는 `parts`의 `id` |
| 파트 순서 | 컷의 파트가 `parts` 순서대로 이어지고(앞 파트로 돌아가면 FAIL), 모든 파트가 한 번 이상 쓰인다 |
| 컷 수 | 6~40 |
| `dur` | 1~60초 |
| 훅 길이 | 첫 파트 컷 `dur`의 합 ≤ 장르의 `hook_max` |
| 첫 컷 | `shot`이 `title-card`가 아니다(장면으로 시작) |
| 답 뒤 길이 | `answer_cut` 다음 컷부터 끝까지 `dur`의 합 ÷ 전체 `dur`의 합 ≤ 0.20. `answer_cut`은 1~컷 수 |
| 반응 요소 | `reaction.cut`은 1~컷 수, `reaction.text`는 비어 있지 않다 |
| `voice` | `none`이면 `narration`이 빈 문자열, `adr`이면 `adr_reason`이 비어 있지 않음 |
| 말하는 속도 | 공백을 뺀 글자 수 ÷ `dur` ≤ 7(초당 글자) |
| `sketch` | 공백으로 나눈 낱말 6~40개, 한글 없음, `font`·`typeface`·`text`·`caption`·`letter` 낱말 없음 |
| `move` 반복 | 같은 `move`가 3컷 연속이면 FAIL. `none: true`인 `hold`는 예외 |
| `shot` 종류 | 컷이 8개 이상이면 `shot`이 3종류 이상 |
| `music` | `from_cut` ≤ `to_cut`, 범위가 1~컷 수, 서로 겹치지 않음, `id` 중복 없음, `bpm`은 0보다 큰 숫자, `mood`·`genre`·`instruments`·`energy`·`search_keywords`·`generation_prompt`가 비어 있지 않음 |

시간 표기는 `mm:ss`이고 초는 반올림한다(0.5초는 올림). 컷 범위는 시작~끝(`dur` 더한 값)이다.

moves.jsonl의 `limit`은 쓰는 법의 안내이고, 검사는 위의 연속 3컷만 본다.
