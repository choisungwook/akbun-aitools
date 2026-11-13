---
description: 사진·영상 같은 참고 자료(assets)에서 제목 글자 스타일을 뽑아, 폰트 없이 이미지 생성 모델이 그림 위에 title을 직접 그리게 하는 akbun-draw skill(akbun-draw-title-<고유명사>)을 추가하고, 루트 index.md에 전|후 비교를 남기는 이 저장소 전용 절차.
argument-hint: <사진 경로 | 영상 파일 | 유튜브 URL> ... [제목을 얹을 이미지] [요청]
disable-model-invocation: true
---

# repo-make-titleskillfromassets

입력: $ARGUMENTS

참고 자료(assets)를 받아 그 **제목 글자 스타일**을 재사용 가능한 skill로 만든다. skill은 이미 있는 이미지와 제목·부제를 받아, 이미지 생성 모델이 그 그림 위에 title을 그림의 일부로 직접 그리게 하는 편집 프롬프트를 만든다. **폰트 파일은 쓰지 않는다.** 글씨체는 프롬프트의 묘사로만 정한다. 원본의 글자를 흉내 내는 skill이 아니다. 받기·스타일 뽑기·시험·PR 절차는 [repo-make-skillfromassets](repo-make-skillfromassets.md)와 같고, 아래는 그와 다른 점만 적는다. 겹치는 규칙은 AGENTS.md가 원본이다.

## 사용자가 정한 규칙

1. **플러그인과 이름**: 언제나 `akbun-draw` 하나에만 만든다(editvideo 짝 없음). 이름은 `akbun-draw-title-<고유명사>`이고, 고유명사는 스타일을 떠올리게 하는 쉬운 영어 한 단어다(예: `folio`, `ember`). 만들기 전에 `ls plugins/akbun-draw/skills`로 겹치는지 본다.
2. **폰트를 쓰지 않음**: 이 skill은 조판이 아니라 그림이므로 AGENTS.md의 SVG `<text>` OFL 글꼴 규칙 대상이 아니다. 폰트를 받거나 설치하거나 Pillow·SVG로 글자를 얹지 않는다. 글자는 이미지 생성 모델이 그린다. 프롬프트에 폰트 이름(상용·OFL 모두)을 쓰지 않고, 획 모양으로 묘사한다(예: "획 대비가 큰 세리프, 가는 헤어라인과 굵은 줄기, 작은 브래킷 세리프", "붓으로 쓴 듯 끝이 갈라진 획").
3. **저작권**: 아래 중 하나라도 걸리면 쓰지 않는다.
   - 고유명사: 상표·회사·제품·작품·캐릭터·인물·지명 이름이 아니어야 한다. 정한 단어를 그 뜻으로 검색해 그 이름의 유명한 브랜드·작품이 먼저 나오면 다른 단어로 바꾼다.
   - title 설명: skill 문서·예시·description·프롬프트에 특정 브랜드·로고·작품·책·출판사·폰트를 가리키는 말을 쓰지 않는다. "옛 그림책 표지 같은 손글씨 세리프 제목"처럼 일반 말로 쓴다.
   - 문구: 예시 title 문구는 원본 문구와 다른, 지어낸 문구로 한다. 원본 로고·레터링 모양을 그대로 그리게 하는 묘사(특정 글자의 장식, 특정 배치 조합)를 쓰지 않는다.
4. **스타일만 묘사**: 획(세리프 유무·획 대비·끝 모양), 굵기, 대소문자, 자간, 제목과 부제의 크기 비율, 색(hex), 질감(그림과 같은 붓질·번짐), 효과(없음이면 "테두리·그림자·배경 박스 없음")를 규칙으로 쓴다. 제목 위치는 고정하지 않고 "주 소재를 가리지 않는 가장 비고 고른 곳"으로 모델에 맡긴다. 프롬프트에는 "철자를 주어진 그대로, 다른 글자 없이"와 "그림 자체는 구도·색·화풍을 그대로"를 늘 넣는다.
5. **출처를 남기지 않음**: [repo-make-skillfromassets](repo-make-skillfromassets.md) 규칙 5와 같다.

## 절차

### 1~2. 받기·스타일 뽑기

[repo-make-skillfromassets](repo-make-skillfromassets.md)의 1·2단계와 같다. 다만 "스타일 표"는 글자 항목만 만든다: 획 모양, 굵기, 대소문자, 자간, 제목:부제 크기 비율, 색(값과 쓰임), 질감·효과. 폰트 대응 칸은 만들지 않는다.

### 3. skill 쓰기

- 구조는 `akbun-draw-faded-film`처럼 SKILL.md는 라우팅 표, 글자 스타일 문장은 `references/style.jsonl`, 프롬프트 조립과 채점은 `scripts/`가 맡는다. 모델은 spec(JSON: 입력 이미지 경로, 제목, 부제)만 쓴다.
- 채점은 제목·부제가 비어 있지 않은지, 길이(제목 1~20자, 부제 0~40자, 공백 포함 글자 수, 경계 포함), 금지 낱말(폰트 이름·브랜드를 가리키는 말 목록)이 없는지 본다. 스크립트에 `--selftest`를 둔다.
- frontmatter에 `disable-model-invocation: true`. 수치 규칙은 세는 법·단위·반올림까지 쓴다.

codex CLI로 원본 그림에 title을 그리게 하는 명령이다. 프롬프트를 `-i` 앞에 둔다. `-i`는 값을 여러 개 받아서, 뒤에 두면 프롬프트까지 이미지 경로로 먹고 "No prompt provided"로 끝난다.

```bash
codex exec --skip-git-repo-check -s workspace-write "Read <id>.txt. Edit the attached image <id>.jpg with your built-in image generation tool: use that file's full text as the edit prompt, exactly, keep the original aspect ratio. Save the result as <id>-after.png here. Reply with the path only." -i <id>.jpg < /dev/null
```

### 4. 전|후 비교와 README 샘플

- title을 그릴 이미지는 사용자가 준 것을 쓰고, 없으면 저장소 `imgs/` 아래 사람 없는 그림 3장을 고른다. 원본 assets에는 그리지 않는다. 시험 title은 한글 2장, 영어 1장 이상으로 한다.
- 결과는 `imgs/<skill 이름>/<이름>-before.jpg`, `<이름>-after.jpg`(1280px 폭)로 저장한다. 대표 after 한 장을 `imgs/<skill 이름>.jpg`로 두고 README 두 표와 `docs/manual_draw.md`에 넣는다.
- after를 한 장으로 붙여 한 번만 보고 확인한다: 철자가 주어진 그대로인가, 다른 글자가 없는가, 주 소재를 가리지 않는가, 묘사한 획 모양(특히 한글)이 나왔는가, 그림 자체가 크게 바뀌지 않았는가. 어긋난 장은 같은 프롬프트로 다시 생성하고, 몇 번 만에 맞았는지 PR 검증 표에 적는다.
- 루트 `index.md`를 전|후 표로 쓴다. 그림은 루트에 둔 심볼릭 링크(`<skill 이름>-<이름>-before.jpg` → `imgs/...`)로 가리킨다. 루트 `index.md`와 심볼릭 링크는 로컬 확인용이라 `git add`하지 않는다(커밋할 때 경로를 하나씩 지정).

루트 `index.md` 형식이다.

```markdown
# <skill 이름> 전·후 비교

| 전 | 후 |
|---|---|
| ![<이름> 전](<skill 이름>-<이름>-before.jpg) | ![<이름> 후](<skill 이름>-<이름>-after.jpg) |
```

### 5. 시험·검증·PR

[repo-make-skillfromassets](repo-make-skillfromassets.md)의 5단계와 같다(editvideo 검사 제외). 더해서 올리기 전 `git diff origin/main`과 새 파일에 폰트 이름·원본 title 문구·브랜드명이 없는지 본다.
