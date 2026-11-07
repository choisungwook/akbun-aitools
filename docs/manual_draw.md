# 그림 스킬 사용자 매뉴얼

이 문서는 `akbun-draw` 플러그인의 스킬을 어떤 상황에 고르는지 안내한다. 실제 작업 지침과 세부 조건은 연결된 `SKILL.md`가 기준이다.

스킬은 이름을 직접 불러 사용한다. 예: `$akbun-draw-slate-marker 이 대본으로 HTTP 캐시를 설명하는 장면을 만들어줘.` 스타일 스킬은 그림체·색·움직임만 고정하고, 무엇을 어디에 그릴지는 입력 내용에 맞춰 정한다.

## 설명 영상 장면

대본에 맞춘 설명 장면을 만든다. 대부분 MP4·MOV로 렌더하고, night-gouache는 스틸과 Resolve용 레이어 PNG를 만든다. Resolve에서 글자·시점을 고칠 수 있는 타임라인이 필요하면 표 오른쪽의 editvideo 짝을 쓴다([영상 편집 매뉴얼](manual_editvideo.md)).

| 상황 | 스킬 | 화면과 결과물 | Resolve 짝 |
|---|---|---|---|
| 요청·메모리·프로세스처럼 보이지 않는 시스템 동작을 카드와 상태 변화로 보여 주고 싶음 | [akbun-draw-slate-marker](../plugins/akbun-draw/skills/akbun-draw-slate-marker/SKILL.md) | 순검정 배경, 어두운 카드, 손글씨 캡션, 의미마다 하나씩 정한 강조색 | [explainer-slate-marker](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-slate-marker/SKILL.md) |
| 보드에 손으로 써 내려가듯 수식·단계·묻고 답하기를 설명하고 싶음 | [akbun-draw-scribble-black](../plugins/akbun-draw/skills/akbun-draw-scribble-black/SKILL.md) | 검정 보드, 흰 펜 선, 생각 구름·말풍선·얼굴 없는 막대 인물, 한 번에 한 획 | [explainer-scribble-black](../plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-scribble-black/SKILL.md) |
| 비유·대화를 어두운 배경 위 손채색 그림으로 보여 주고 싶음 | [akbun-draw-night-gouache](../plugins/akbun-draw/skills/akbun-draw-night-gouache/SKILL.md) | 외곽선 없는 손채색 사물·인물·막대 인물·말풍선, 핵심 대상 하나만 빛남. 결과는 스틸과 레이어 PNG | - |
| 코드를 한 줄씩 타이핑하며 짚어 주고 싶음 | [akbun-draw-code-window-lilac](../plugins/akbun-draw/skills/akbun-draw-code-window-lilac/SKILL.md) | 연회색 캔버스, 흰 코드 에디터 창, 연보라 줄 띠·토큰 상자 | - |
| 캐릭터가 연기하는 짧은 낙서 장면이 필요함 | [akbun-draw-motion-doodle](../plugins/akbun-draw/skills/akbun-draw-motion-doodle/SKILL.md) | 흰 종이 검은 잉크 낙서, 포즈 교체로 움직이는 캐릭터. 다른 모션 스킬이 쓰는 렌더러도 여기 있음 | - |
| 개념을 일상 비유로 풀고 싶고 연필 느낌이 맞음 | [akbun-draw-pencil-analogy-graphite](../plugins/akbun-draw/skills/akbun-draw-pencil-analogy-graphite/SKILL.md) | 연필 막대 인물, 색 소품 하나 | - |
| 비유를 동화책처럼 부드럽게 보여 주고 싶음 | [akbun-draw-storybook-crayon](../plugins/akbun-draw/skills/akbun-draw-storybook-crayon/SKILL.md) | 색연필 동화책 캐릭터, 빨간 점선 경고 | - |
| 짧은 이야기를 내레이션 자막이 붙은 세로 애니메이션 쇼츠로 보여 주고 싶음 | [akbun-draw-animation-dami](../plugins/akbun-draw/skills/akbun-draw-animation-dami/SKILL.md) | 외곽선 없는 회화풍 그림, 안개 낀 원경·앰버 빛·붉은 물체 하나, 이야기마다 새 배역(캐릭터 시트로 컷 사이 생김새 유지), 컷당 1–4장 자세 넘김과 하드컷, 흰 바탕 아래 2줄 자막. 결과는 프롬프트·codex.sh·그림과 9:16 MP4(spec을 스크립트가 조립·채점·렌더) | - |

비슷한 스킬끼리 고르는 기준:

- **누가 묻고 답하는지가 요점**: 손으로 써 내려가는 속도감이 필요하면 scribble-black, 그림 한 장면의 분위기가 중요하면 night-gouache의 막대 인물·말풍선.
- **밝은 화면 vs 어두운 화면**: 밝은 화면은 code-window-lilac·motion-doodle·pencil-analogy-graphite·storybook-crayon, 어두운 화면은 slate-marker·scribble-black·night-gouache.

## 그림 한 장 (이미지 생성 프롬프트·SVG)

이미지 생성 모델에 넣을 프롬프트나 편집용 SVG를 만든다. `akbun-draw-explainer-svg`는 프롬프트가 아니라 16:9 SVG 코드를 직접 쓰고, 스타일 토큰 JSON과 검사 스크립트(`check_style_svg.py`)로 색·여백·자막 영역을 검수한다.

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 블로그에 코드를 짚어 설명하는 그림이 필요함 | [akbun-generateimage-code](../plugins/akbun-draw/skills/akbun-generateimage-code/SKILL.md) | 코드 위 강조 박스·화살표·콜아웃이 들어간 그림 프롬프트 |
| 시스템 흐름을 아이가 그린 듯한 다이어그램으로 보여 주고 싶음 | [akbun-draw-crayon-milo](../plugins/akbun-draw/skills/akbun-draw-crayon-milo/SKILL.md) | 크레용 다이어그램 프롬프트 |
| 시스템 구조·요청 흐름을 흰 바탕 손그림 다이어그램 이미지로 보여 주고 싶음 | [akbun-draw-diagram-haru](../plugins/akbun-draw/skills/akbun-draw-diagram-haru/SKILL.md) | 검정 외곽선 빈 도형·속 빈 화살표·손글씨 이름 다이어그램 프롬프트(spec을 스크립트가 조립·채점) |
| 개념 하나를 카드 한 장으로 정리하고 싶음 | [akbun-draw-sketchbook-card](../plugins/akbun-draw/skills/akbun-draw-sketchbook-card/SKILL.md) | 스파이럴 스케치북 카드 프롬프트 |
| 여백 많은 조용한 일상 장면 그림이 필요함 | [akbun-draw-quiet-pencil](../plugins/akbun-draw/skills/akbun-draw-quiet-pencil/SKILL.md) | 크림 배경 연필 장면 프롬프트 |
| 소품 가득한 아늑한 배경 속 동물 캐릭터 일상 장면이 필요함 | [akbun-draw-style-bori](../plugins/akbun-draw/skills/akbun-draw-style-bori/SKILL.md) | 갈색 손그림 선·셀 채색 장면 프롬프트(spec을 스크립트가 조립·채점) |
| 논문·학습 자료를 이미지와 설명 대본으로 바꾸고 싶음 | [akbun-draw-learning-mono](../plugins/akbun-draw/skills/akbun-draw-learning-mono/SKILL.md) | 흑백 16:9 학습 이미지와 대본 |
| 여행 글에 넣을 썸네일·약도 삽화가 필요함 | [akbun-draw-travel-blog](../plugins/akbun-draw/skills/akbun-draw-travel-blog/SKILL.md) | 썸네일·코스 약도 프롬프트 |
| IT·여행 글이나 영상의 유튜브·티스토리 썸네일을 포스터처럼 만들고 싶음 | [akbun-draw-thumbnail-retro](../plugins/akbun-draw/skills/akbun-draw-thumbnail-retro/SKILL.md) | 70년대 필름 사진 위 레트로 디스플레이 글자 썸네일 프롬프트(16:9·1:1) |
| 블로그·유튜브 썸네일을 흰 종이 낙서 그림으로 만들고 싶음 | [akbun-draw-thumbnail-doodle](../plugins/akbun-draw/skills/akbun-draw-thumbnail-doodle/SKILL.md) | 낙서 그림체 썸네일 프롬프트(16:9·4:3), 요청 시 codex로 생성해 ~/Downloads에 저장 |
| 시스템 구조·개념을 설명 영상·슬라이드용 16:9 그림 한 장으로 만들고 싶음 | [akbun-draw-explainer-svg](../plugins/akbun-draw/skills/akbun-draw-explainer-svg/SKILL.md) | 1920×1080 SVG 코드. `styles/*.json` 토큰 9종(라인아트, 클레이 아이소메트릭, 칠판, 모눈 노트, 네온 와이어프레임, 종이 컷아웃, 벤토 카드, 잉크 해칭 삽화, 마커 와이어프레임) 중 하나를 골라 그림체만 고정하고 배치는 내용이 정함 |

## 만화·웹툰

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 짧은 이야기를 2·4·6컷 만화로 올리고 싶음 | [akbun-draw-doodle-comic](../plugins/akbun-draw/skills/akbun-draw-doodle-comic/SKILL.md) | 낙서 그림체 만화 PNG(블로그용 한 장 또는 인스타툰 컷별) |
| 이미지·글로 귀여운 동물 캐릭터 웹툰을 만들고 싶음 | [akbun-draw-webtoon-b](../plugins/akbun-draw/skills/akbun-draw-webtoon-b/SKILL.md) | 페이지별 프롬프트와 편집용 SVG |
| 이야기를 진지한 흑백 다큐 느낌으로 보여 주고 싶음 | [akbun-draw-webtoon-d](../plugins/akbun-draw/skills/akbun-draw-webtoon-d/SKILL.md) | 장면별 흑백 다큐툰 프롬프트 |

## 기준 스킬

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 다른 그림에 akbun 고래 마스코트를 같은 모습으로 넣어야 함 | [akbun-mascot-whale](../plugins/akbun-draw/skills/akbun-mascot-whale/SKILL.md) | 마스코트 외형 기준. 다른 스킬이 참조한다 |
