# Golden Reference (webtoon-d)

`design.md` 스타일이 소재와 무관하게 재사용됨을 보여주는 완성 예시다. 소재는 "신입 개발자의 첫 새벽 장애 대응" — 스타일을 뽑아낸 원본과 다른 이야기로, 프롬프트 작성 형식을 참고하는 용도다. 문구·장면을 그대로 복사하지 말고 형식만 따른다.

## 인터뷰로 확보한 이야기 (요약)

- 입사 3주차 신입 개발자 "나"와 사수 "민 선배" 두 명이 주인공급.
- 새벽에 장애 알림이 울려 사무실로 달려갔고, 다른 팀 사람들도 하나둘 모였다.
- 원인을 찾은 건 아침이었고, 다 같이 해장국을 먹으러 갔다.

## 장면 나누기

장면표 형식이다. 자막이 이야기를 서술하고, 손글씨는 그 순간의 소리만 담는다.

| 장면 | 자막 (하단 내레이션) | 손글씨 | 구도 |
|---|---|---|---|
| 1 | 입사 3주차였나? 처음으로 새벽 알림이 울렸는데, | (없음) | 새벽 사무실 건물 전경 설정 샷 |
| 2 | 사무실엔 이미 사람들이 모여 있었다. | "서버 죽었어!!" | 목격자 시점, 모니터 앞 군중 |
| 3 | 그렇게 선배와 로그를 뒤졌고, 아침이 되어서야... | "찾았다!" | 두 주인공 뒷모습 |

## 장면별 이미지 프롬프트

장면 1 — 설정 샷:

```text
A horizontal 16:9 (1920x1080) frame of a Korean documentary-style webtoon. Rough
hand-drawn black ink doodle lines with uneven sketchy strokes on a plain white
background, grayscale only: white, flat mid-gray fills, flat light-gray shading
blobs, no gradients, no color, no panel borders.

SCENE: a wide establishing shot of a small office building at night, drawn with
loose freehand lines and slightly crooked windows, flat light-gray shading on one
wall, a streetlamp sketched roughly at the side, a few short horizontal strokes
suggesting the ground. No people in this frame.

SUBTITLE BAR: a semi-transparent dark-gray band across the full bottom width of the
frame, containing bold white Korean gothic subtitle text, center-aligned, two lines,
rendered exactly as written:
"입사 3주차였나?"
"처음으로 새벽 알림이 울렸는데,"

DO NOT: no color, no gradients, no clean vector lines, no panel borders, no speech
bubbles, no photorealism, no watermark. Do not misspell, translate, or rearrange the
Korean text, and do not add any text beyond the lines listed above.
```

장면 2 — 군중과 목격자 시점:

```text
A horizontal 16:9 (1920x1080) frame of a Korean documentary-style webtoon. Rough
hand-drawn black ink doodle lines with uneven sketchy strokes on a plain white
background, grayscale only: white, flat mid-gray fills, flat light-gray shading
blobs, no gradients, no color, no panel borders.

MAIN CHARACTERS: the narrator "me": a young man with short black hair, simple dot
eyes, wearing a plain white t-shirt, drawn with rough black ink lines. His senior
"Min": a taller man with wavy hair and round glasses, simple dot eyes, mid-gray
flat-colored jacket.

SCENE: an over-the-shoulder witness view — the narrator seen from behind in the left
foreground, looking across the room at a cluster of figures gathered around a glowing
monitor. The senior Min stands at the monitor pointing at the screen. Around him,
three coworkers are drawn as flat mid-gray silhouettes with no facial features,
hunched or leaning in. Two more distant figures are light-gray outline-only ghosts.
A gray scribble-burst shock mark floats above the group.

TEXT IN SCENE: handwritten rough Korean text floating near the monitor group,
no speech bubble, rendered exactly as written: "서버 죽었어!!"

SUBTITLE BAR: a semi-transparent dark-gray band across the full bottom width of the
frame, containing bold white Korean gothic subtitle text, center-aligned, one line,
rendered exactly as written:
"사무실엔 이미 사람들이 모여 있었다."

DO NOT: no color, no gradients, no clean vector lines, no panel borders, no speech
bubbles, no facial features on the gray silhouette figures, no more than two
distinct faces, no photorealism, no watermark. Do not misspell, translate, or
rearrange the Korean text, and do not add any text beyond the lines listed above.
```

장면 3 — 뒷모습 마무리:

```text
A horizontal 16:9 (1920x1080) frame of a Korean documentary-style webtoon. Rough
hand-drawn black ink doodle lines with uneven sketchy strokes on a plain white
background, grayscale only: white, flat mid-gray fills, flat light-gray shading
blobs, no gradients, no color, no panel borders.

MAIN CHARACTERS: the narrator "me": a young man with short black hair, simple dot
eyes, wearing a plain white t-shirt, drawn with rough black ink lines. His senior
"Min": a taller man with wavy hair and round glasses, simple dot eyes, mid-gray
flat-colored jacket.

SCENE: the two main characters seen from behind, side by side at a desk, the senior
Min raising one fist, a small sweat drop near the narrator's head, two rough
monitors in front of them, flat light-gray shading blob under the desk, a few short
horizontal ground strokes. Empty white space fills most of the frame.

TEXT IN SCENE: handwritten rough Korean text floating above the senior's raised
fist, no speech bubble, rendered exactly as written: "찾았다!"

SUBTITLE BAR: a semi-transparent dark-gray band across the full bottom width of the
frame, containing bold white Korean gothic subtitle text, center-aligned, one line,
rendered exactly as written:
"그렇게 선배와 로그를 뒤졌고, 아침이 되어서야..."

DO NOT: no color, no gradients, no clean vector lines, no panel borders, no speech
bubbles, no photorealism, no watermark. Do not misspell, translate, or rearrange the
Korean text, and do not add any text beyond the lines listed above.
```
