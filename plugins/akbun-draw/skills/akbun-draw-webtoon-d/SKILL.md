---
name: akbun-draw-webtoon-d
description: >
  사용자의 실제 이야기(경험담, 회상, 썰)를 가로형 흑백 다큐멘터리 웹툰으로 만든다. 스타일은 고정이다 —
  거친 검정 잉크 낙서선, 흰 배경, 플랫 회색 음영, 화면 하단의 영상 자막 스타일 한글 내레이션 바.
  주인공급 얼굴은 최대 4명, 주변 인물은 얼굴 없는 회색 실루엣으로 그린다. 장면(1장)마다 이미지 생성
  프롬프트를 따로따로 만들고, 이야기 소재가 없으면 그리지 않고 먼저 인터뷰한다.
  Trigger on: "다큐툰", "썰툰", "회상 웹툰", "경험담 웹툰", "자막 웹툰", "흑백 웹툰",
  "documentary webtoon", "story-time webtoon", or any request to turn a personal
  story/memory into subtitle-narrated grayscale webtoon frames.
---

# 흑백 다큐툰 만들기 (장면별 이미지 프롬프트)

## 이 skill이 하는 일

사용자의 실제 이야기(경험담, 회상, 썰)를 **가로형 흑백 다큐멘터리 웹툰**으로 만든다. 유튜브 썰툰 영상의 한 프레임처럼, 이미지마다 하단 자막 바의 한글 내레이션이 이야기를 서술한다. 결과물은 **장면(1장)마다 따로 만든 영어 이미지 생성 프롬프트**다 — GPT image, nano-banana 같은 이미지 생성 모델(agent)에 한 장면씩 그대로 붙여넣는다.

비주얼 스타일은 이 skill이 정하지 않고 같은 디렉터리의 [design.md](design.md)에 고정되어 있다. **프롬프트를 쓰기 전에 design.md를 반드시 읽는다.** 소재·장면·구도는 사용자 이야기에 맞춰 자유롭게 정하되, design.md의 그림 언어(선, 회색 팔레트, 자막 바, 인물 위계)는 그대로 따른다.

다른 웹툰 skill과의 구분: `akbun-draw-webtoon-a`는 세로로 쌓은 3~4컷 스틱피겨 컷만화, `akbun-draw-webtoon-b`는 세로형 파스텔 치비 페이지, `akbun-draw-webtoon-c`는 세로형 1컷 에세이툰(고래 마스코트)이다. 이 skill은 **가로형 16:9 + 하단 자막 내레이션 + 흑백 낙서선 + 사람 캐릭터**가 고정이다.

## 소재가 없으면 그리지 않는다 (인터뷰 우선)

이 skill은 이야기를 지어내지 않는다. 사용자가 이야기를 주지 않았거나, 장면을 나눌 수 없을 만큼 정보가 부족하면 **프롬프트를 만들지 말고 먼저 인터뷰한다.** 아래를 묻는다 (이미 아는 항목은 건너뛴다).

- **언제, 어디서** 있었던 일인가?
- **누가** 나오는가? 이름을 붙일 인물(주인공급)은 누구인가?
- **무슨 일**이 일어났는가? 시작 → 사건 → 결말 순서로.
- 그때 **기분/분위기**는 어땠는가?
- 몇 장면(몇 장) 정도로 만들고 싶은가?

답을 받은 뒤에야 장면 나누기로 넘어간다. 대화 맥락과 첨부에서 이야기를 충분히 읽어낼 수 있으면 인터뷰 없이 진행하되, 추측으로 채운 부분은 사용자에게 밝힌다.

## 캐릭터 규칙

- **주인공급은 최대 4명.** 독특한 얼굴(이목구비)을 가진 캐릭터는 작품 전체에서 4명을 넘기지 않는다. 이야기에 이름 있는 인물이 더 많으면 사용자와 상의해 4명으로 줄이거나 나머지를 실루엣으로 내린다.
- 주인공급마다 **고정 영어 CHARACTER 문장**을 하나 만든다 — 헤어스타일·모자·안경·체형·옷 같은 구별 요소를 담은 한 문장. 이미지 모델은 장면 간 기억이 없으므로, 그 캐릭터가 나오는 모든 장면 프롬프트에 이 문장을 **글자 그대로** 복사한다.
- 주인공급이 아닌 모든 인물은 design.md의 인물 위계대로 **얼굴 없는 미드그레이 플랫 실루엣**(근경) 또는 **라이트그레이 외곽선 고스트**(원경)로 그린다. 실루엣에 이목구비를 그리지 않는다.

## 결과물 형식

항상 두 가지를 출력한다.

1. **한국어 장면표** — 장면 번호, 하단 자막 내레이션(1~2줄), 장면 내 손글씨 텍스트(있으면), 구도 요약. 인터뷰로 만든 이야기면 장면표를 먼저 보여주고 확인을 받는다.
2. **장면별 영어 이미지 프롬프트** — 장면마다 하나씩, 각각 별도의 코드 펜스 블록(```text)으로. 여러 장면을 한 프롬프트에 합치지 않는다.

## 작업 순서

1. **design.md를 읽는다.** 스타일 정의 전체를 읽고 나서 시작한다.
2. **이야기 확보.** 사용자 글·첨부·대화 맥락에서 이야기를 파악한다. 부족하면 위 인터뷰 질문으로 묻고, 답을 받을 때까지 프롬프트를 만들지 않는다.
3. **장면 나누기.** 이야기를 장면 단위로 자른다. 한 장면 = 한 프레임 = 자막 1~2줄. 사건이 바뀌는 지점이 장면 경계다. 설정 샷(장소 전경)으로 시작하면 회상 무드가 산다.
4. **캐릭터 시트.** 주인공급(최대 4명)의 고정 영어 CHARACTER 문장을 만든다.
5. **자막·손글씨 쓰기.** 자막은 과거 회상체의 담담한 한국어 서술로, 장면 사이를 말줄임표로 잇는다. 손글씨는 그 순간의 소리(외침, 구호)만 장면당 최대 2개.
6. **장면별 프롬프트 작성.** 아래 템플릿을 장면마다 채워 **따로따로** 만든다.
7. **출력.** 장면표 + 장면별 프롬프트 블록들을 출력한다.

## 이미지 프롬프트 템플릿

장면마다 아래 영어 템플릿의 `<...>`를 채운다. 스타일 문단과 DO NOT 문단은 design.md를 요약한 고정 문구이므로 바꾸지 않는다. 그 장면에 나오지 않는 캐릭터 문장과 쓰지 않는 텍스트 줄은 지운다.

```text
A horizontal 16:9 (1920x1080) frame of a Korean documentary-style webtoon. Rough
hand-drawn black ink doodle lines with uneven sketchy strokes on a plain white
background, grayscale only: white, flat mid-gray fills, flat light-gray shading
blobs, no gradients, no color, no panel borders.

MAIN CHARACTERS: <paste the fixed CHARACTER sentences of the characters in this
scene, verbatim>.

SCENE: <who does what, camera angle (back view / over-the-shoulder / crowd facing
front / establishing shot), posture and emotion, comic marks (sweat drop, gray
scribble-burst) used sparingly. Describe nearby extras as "flat mid-gray silhouettes
with no facial features" and distant extras as "light-gray outline-only ghosts">.

TEXT IN SCENE: handwritten rough Korean text floating near <character/group>,
no speech bubble, rendered exactly as written: "<...>"

SUBTITLE BAR: a semi-transparent dark-gray band across the full bottom width of the
frame, containing bold white Korean gothic subtitle text, center-aligned,
<one line / two lines>, rendered exactly as written:
"<subtitle line 1>"
"<subtitle line 2>"

DO NOT: no color, no gradients, no clean vector lines, no panel borders, no speech
bubbles, no facial features on the gray silhouette figures, no more than four
distinct faces, no photorealism, no watermark. Do not misspell, translate, or
rearrange the Korean text, and do not add any text beyond the lines listed above.
```

## 예시

완성 예시는 [references/golden-reference.md](references/golden-reference.md)에 있다 — 인터뷰로 확보한 이야기를 장면표로 나누고 장면별 프롬프트로 만든 전 과정을 보여준다. 형식만 참고하고 문구·장면을 복사하지 않는다.

## 완료 전 확인

- design.md를 읽고 그 스타일 정의대로 프롬프트를 썼는가?
- 소재가 부족했을 때 지어내지 않고 인터뷰했는가? 추측으로 채운 부분을 밝혔는가?
- 장면(1장)마다 프롬프트를 따로따로 만들었는가? 한 블록에 여러 장면을 합치지 않았는가?
- 독특한 얼굴을 가진 주인공급이 4명 이하이고, 각 CHARACTER 문장을 모든 등장 장면에 글자 그대로 복사했는가?
- 주변 인물을 얼굴 없는 회색 실루엣/고스트로 지시했는가?
- 모든 장면에 하단 자막 바(흰 굵은 한글, 1~2줄)가 있고, 손글씨는 장면당 최대 2개인가?
- DO NOT에 색·말풍선·실루엣 이목구비·얼굴 5명 이상 금지를 넣었는가?
