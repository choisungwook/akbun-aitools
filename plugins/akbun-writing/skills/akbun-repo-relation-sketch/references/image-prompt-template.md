# Image-generation prompt template

이 파일은 이미지 생성 AI(nano-banana, DALL-E 등)가 손그림 스타일 repo 연관관계 다이어그램을 그리도록 지시하는 영어 프롬프트의 템플릿이다. 확정한 relation model을 아래 구조에 채워 `~/Downloads/<name>/<name>-image-prompt.md`로 저장한다(산출물은 `<name>` 디렉터리에 모은다).

## 작성 규칙

- 프롬프트 전체와 다이어그램 안의 모든 글씨는 영어로 쓴다.
- 노드(repo 박스) 하나하나와 화살표(관계) 하나하나, 그리고 각 화살표의 라벨을 빠짐없이 적는다. 이미지 모델은 구조를 추론하지 못하므로 명시적으로 나열한다.
- 스타일 묘사는 아래 "Style block"을 거의 그대로 쓴다. 이게 첨부 이미지의 손그림 분위기를 만든다.
- 강조(emphasize)된 관계는 "drawn in warm orange, slightly thicker"로 따로 표기한다.

## 프롬프트 구조

아래 순서대로 작성한다.

```text
Draw a hand-drawn, whiteboard-style diagram that shows how several code
repositories relate to each other.

STYLE:
- Hand-drawn / sketch look, like an Excalidraw or notebook doodle.
- Warm off-white paper background, plain with no grid lines.
- Slightly wobbly, imperfect ink strokes; rounded rectangles for each box.
- Friendly handwritten-marker font for all text. All text is in English.
- Soft drop shadows under each box. Arrow labels sit on a pale yellow
  highlighter swatch.
- Title at the top center: "<TITLE>".

BOXES (one rounded rectangle per repository):
- "<repo label>" — small caption underneath: "<keyword1 · keyword2 · keyword3>"
- "<repo label>" — small caption underneath: "<keyword1 · keyword2>"
  ... (one line per node)

ARROWS (hand-drawn arrows between the boxes, each with a short label):
- From "<from label>" to "<to label>", labeled "<edge keyword>".
- From "<from label>" to "<to label>", labeled "<edge keyword>",
  drawn in warm orange and slightly thicker (this is the key relationship).
  ... (one line per edge; note direction; use a double-headed arrow for "both")

LAYOUT:
- Spread the boxes out with generous spacing so arrows and labels do not
  overlap. Keep the whole diagram readable and uncluttered.
```

## 예시

아래는 `assets/example-relation.json`을 이 템플릿으로 채운 결과다.

```text
Draw a hand-drawn, whiteboard-style diagram that shows how several code
repositories relate to each other.

STYLE:
- Hand-drawn / sketch look, like an Excalidraw or notebook doodle.
- Warm off-white paper background, plain with no grid lines.
- Slightly wobbly, imperfect ink strokes; rounded rectangles for each box.
- Friendly handwritten-marker font for all text. All text is in English.
- Soft drop shadows under each box. Arrow labels sit on a pale yellow
  highlighter swatch.
- Title at the top center: "How the platform repos relate".

BOXES (one rounded rectangle per repository):
- "platform-core" — small caption underneath: "go · library · domain"
- "platform-api" — small caption underneath: "rest · grpc"
- "platform-web" — small caption underneath: "react · ui"
- "platform-infra" — small caption underneath: "terraform · k8s"

ARROWS (hand-drawn arrows between the boxes, each with a short label):
- From "platform-api" to "platform-core", labeled "imports", drawn in warm
  orange and slightly thicker (this is the key relationship).
- From "platform-web" to "platform-api", labeled "calls".
- From "platform-infra" to "platform-api", labeled "deploys".
- From "platform-infra" to "platform-web", labeled "deploys".

LAYOUT:
- Spread the boxes out with generous spacing so arrows and labels do not
  overlap. Keep the whole diagram readable and uncluttered.
```
