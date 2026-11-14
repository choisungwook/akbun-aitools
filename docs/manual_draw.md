# 그림 스킬 사용자 매뉴얼

이 문서는 `akbun-draw` 플러그인의 스킬을 어떤 상황에 고르는지 안내한다. 실제 작업 지침과 세부 조건은 연결된 `SKILL.md`가 기준이다.

스킬은 이름을 직접 불러 사용한다. 예: `$akbun-draw-code-window-lilac 이 코드로 HTTP 캐시 헤더를 짚는 장면을 만들어줘.` 스타일 스킬은 그림체·색·움직임만 고정하고, 무엇을 어디에 그릴지는 입력 내용에 맞춰 정한다.

## 설명 영상 장면

대본에 맞춘 설명 장면을 만든다. 대부분 MP4·MOV로 렌더하고, explain-sora는 스틸과 Resolve용 레이어 PNG를 만든다. Resolve에서 글자·시점을 고칠 수 있는 타임라인이 필요하면 표 오른쪽의 editvideo 짝을 쓴다([영상 편집 매뉴얼](manual_editvideo.md)).

| 상황 | 스킬 | 화면과 결과물 | Resolve 짝 |
|---|---|---|---|
| 비유·대화를 어두운 배경 위 손채색 그림으로 보여 주고 싶음 | [akbun-draw-explain-sora](../plugins/akbun-draw/skills/akbun-draw-explain-sora/SKILL.md) | 외곽선 없는 손채색 사물·인물·막대 인물·말풍선, 핵심 대상 하나만 빛남. 결과는 스틸과 레이어 PNG | - |
| 코드를 한 줄씩 타이핑하며 짚어 주고 싶음 | [akbun-draw-code-window-lilac](../plugins/akbun-draw/skills/akbun-draw-code-window-lilac/SKILL.md) | 연회색 캔버스, 흰 코드 에디터 창, 연보라 줄 띠·토큰 상자 | - |
| 터미널·AI 도구 화면 녹화의 오류 줄·결과 줄을 짚어 주고 싶음 | [akbun-draw-code-nari](../plugins/akbun-draw/skills/akbun-draw-code-nari/SKILL.md) | 연회색 캔버스 위 어두운 창 카드에 실제 녹화, 노란 손그림 화살표·손글씨 라벨·토큰 하이라이트. 결과는 Resolve Fusion 장면 | - |
| 캐릭터가 연기하는 짧은 낙서 장면이 필요함 | [akbun-draw-motion-doodle](../plugins/akbun-draw/skills/akbun-draw-motion-doodle/SKILL.md) | 흰 종이 검은 잉크 낙서, 포즈 교체로 움직이는 캐릭터. 다른 모션 스킬이 쓰는 렌더러도 여기 있음 | - |
| 개념을 일상 비유로 풀고 싶고 연필 느낌이 맞음 | [akbun-draw-raon](../plugins/akbun-draw/skills/akbun-draw-raon/SKILL.md) | 연필 막대 인물, 색 소품 하나 | - |
| 짧은 이야기를 내레이션 자막이 붙은 세로 애니메이션 쇼츠로 보여 주고 싶음 | [akbun-draw-animation-dami](../plugins/akbun-draw/skills/akbun-draw-animation-dami/SKILL.md) | 외곽선 없는 회화풍 그림, 안개 낀 원경·앰버 빛·붉은 물체 하나, 이야기마다 새 배역(캐릭터 시트로 컷 사이 생김새 유지), 컷당 1–4장 자세 넘김과 하드컷, 흰 바탕 아래 2줄 자막. 결과는 프롬프트·codex.sh·그림과 9:16 MP4(spec을 스크립트가 조립·채점·렌더) | - |

비슷한 스킬끼리 고르는 기준:

- **밝은 화면 vs 어두운 화면**: 밝은 화면은 code-window-lilac·motion-doodle·raon, 실제 터미널 녹화는 code-nari, 어두운 화면은 explain-sora.

## 그림 한 장 (이미지 생성 프롬프트·SVG)

이미지 생성 모델에 넣을 프롬프트나 편집용 SVG를 만든다. `akbun-draw-chalkboard`는 프롬프트가 아니라 16:9 SVG 코드를 직접 쓰고, 칠판 스타일 토큰 JSON과 검사 스크립트(`check_style_svg.py`)로 색·여백·자막 영역을 검수한다.

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 시스템 구조·요청 흐름을 흰 바탕 손그림 다이어그램 이미지로 보여 주고 싶음 | [akbun-draw-diagram-haru](../plugins/akbun-draw/skills/akbun-draw-diagram-haru/SKILL.md) | 검정 외곽선 빈 도형·강조색 속 빈 화살표·손글씨 이름을 아이콘 없이 화면 가운데에 놓는 다이어그램 프롬프트(spec을 스크립트가 조립·채점) |
| 소품 가득한 아늑한 배경 속 동물 캐릭터 일상 장면이 필요함 | [akbun-draw-bori](../plugins/akbun-draw/skills/akbun-draw-bori/SKILL.md) | 갈색 손그림 선·셀 채색 장면 프롬프트(spec을 스크립트가 조립·채점) |
| 굵은 잉크 선·단색 면으로 동물·사물의 엉뚱한 한 순간을 그리고 싶음 | [akbun-draw-moss](../plugins/akbun-draw/skills/akbun-draw-moss/SKILL.md) | 올리브 잉크 선·그늘 없는 단색·단색 배경·강조색 하나 그림 프롬프트(spec을 스크립트가 조립·채점) |
| 흰 종이 여백이 넓은 펜 선·수채 칠 장면이 필요함 | [akbun-draw-wash](../plugins/akbun-draw/skills/akbun-draw-wash/SKILL.md) | 끊어 겹친 펜 선·옅은 수채 칠·무표정 동물 장면 프롬프트(spec을 스크립트가 조립·채점) |
| 사람 없는 장면을 바랜 옛 필름 사진처럼 보여 주고 싶음 | [akbun-draw-sena](../plugins/akbun-draw/skills/akbun-draw-sena/SKILL.md) | 필름 입자·무른 초점·실제 광원·아날로그 사물 사진 프롬프트(spec을 스크립트가 조립·채점) |
| 사물·동물 장면을 옛 그림책 삽화처럼 보여 주고 싶음 | [akbun-draw-storybook-vintage](../plugins/akbun-draw/skills/akbun-draw-storybook-vintage/SKILL.md) | 갈색 연필 윤곽·겹친 수채·한 색 얼룩 바탕·바랜 종이결 삽화 프롬프트(spec을 스크립트가 조립·채점) |
| 거리·역·부두 같은 장소를 가는 펜 선 라인 드로잉으로 보여 주고 싶음 | [akbun-draw-gaon](../plugins/akbun-draw/skills/akbun-draw-gaon/SKILL.md) | 미색 종이 위 굵기 하나인 가는 선, 원근 없는 정면 건물의 촘촘한 세부, 얼굴 없이 팔다리를 두 줄로 연 길쭉한 인물, 강조색 1~2개, 밤이면 남색 종이에 옅은 선으로 반전하는 그림 프롬프트(spec을 스크립트가 조립·채점) |
| 이미 있는 그림에 제목을 손글씨처럼 그려 넣고 싶음 | [akbun-draw-title-nib](../plugins/akbun-draw/skills/akbun-draw-title-nib/SKILL.md) | 폰트 없이 이미지 모델이 그림 위에 그리는 세리프 제목·부제 편집 프롬프트(spec을 스크립트가 조립·채점) |
| 그림·사진 위에 크레용으로 덧그린 듯한 굵은 손글씨 제목을 넣고 싶음 | [akbun-draw-title-pastel](../plugins/akbun-draw/skills/akbun-draw-title-pastel/SKILL.md) | 폰트 없이 이미지 모델이 그리는 굵고 둥근 크레용 질감 제목·부제 편집 프롬프트(spec을 스크립트가 조립·채점) |
| 1990년대 TV 셀 애니메이션 느낌의 오리지널 인물 그림이 필요함 | [akbun-draw-character-hana](../plugins/akbun-draw/skills/akbun-draw-character-hana/SKILL.md) | 가는 잉크 선·두 단 셀 채색·바랜 필름 색의 인물을 투명 바탕에 그리는 프롬프트(spec을 스크립트가 조립·채점) |
| 여행지 거리를 카메라 스냅 사진이나 짧은 반복 영상으로 보여 주고 싶음 | [akbun-draw-juno](../plugins/akbun-draw/skills/akbun-draw-juno/SKILL.md) | 무광 베이지·올리브 색 보정, 얼굴 없는 뒷모습 인물 거리 스냅 프롬프트와 2×2 시트를 이은 mp4(spec을 스크립트가 조립·채점) |
| 다정한 제목 한 줄과 그 뒤 웃긴 속사정을 보여 주는 개그 한 컷을 원하는 그림체로 그리고 싶음 | [akbun-draw-template-comedy](../plugins/akbun-draw/skills/akbun-draw-template-comedy/SKILL.md) | 고른 akbun-draw 그림체로 한국어 제목과 두 캐릭터 무표정 개그 한 컷 프롬프트(spec을 스크립트가 조립·검사) |
| 논문·학습 자료를 이미지와 설명 대본으로 바꾸고 싶음 | [akbun-draw-learning-mono](../plugins/akbun-draw/skills/akbun-draw-learning-mono/SKILL.md) | 흑백 16:9 학습 이미지와 대본 |
| IT·여행 글이나 영상의 유튜브·티스토리 썸네일을 포스터처럼 만들고 싶음 | [akbun-draw-thumbnail-retro](../plugins/akbun-draw/skills/akbun-draw-thumbnail-retro/SKILL.md) | 70년대 필름 사진 위 레트로 디스플레이 글자 썸네일 프롬프트(16:9·1:1) |
| 블로그·유튜브 썸네일을 흰 종이 낙서 그림으로 만들고 싶음 | [akbun-draw-thumbnail-doodle](../plugins/akbun-draw/skills/akbun-draw-thumbnail-doodle/SKILL.md) | 낙서 그림체 썸네일 프롬프트(16:9·4:3), 요청 시 codex로 생성해 ~/Downloads에 저장 |
| 시스템 구조·개념을 설명 영상·슬라이드용 16:9 그림 한 장으로 만들고 싶음 | [akbun-draw-chalkboard](../plugins/akbun-draw/skills/akbun-draw-chalkboard/SKILL.md) | 1920×1080 SVG 코드. 다크 그린 칠판 위 분필 선 그림체(`styles/chalkboard.json`)만 고정하고 배치는 내용이 정함 |

## 만화·웹툰

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 쓰던 akbun-draw 그림체 그대로 짧은 이야기를 4컷·격자·인스타툰·유튜브 커뮤니티 만화로 만들고 싶음 | [akbun-draw-template-cartoon](../plugins/akbun-draw/skills/akbun-draw-template-cartoon/SKILL.md) | 템플릿(4koma·grid·instagram·youtube) 이미지 생성 프롬프트. 대사·번호도 이미지 모델이 손글씨로 직접 쓴다 |

## 기준 스킬

| 상황 | 스킬 | 결과물 |
|---|---|---|
| 다른 그림에 akbun 고래 마스코트를 같은 모습으로 넣어야 함 | [akbun-mascot-whale](../plugins/akbun-draw/skills/akbun-mascot-whale/SKILL.md) | 마스코트 외형 기준. 다른 스킬이 참조한다 |
