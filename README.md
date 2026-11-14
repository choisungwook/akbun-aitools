# akbun-aitools

akbun(악분)이 매일 쓰는 AI skill을 Claude Code, Codex, Antigravity plugin으로 묶었습니다.

## 설치

Claude Code와 Codex 명령의 `akbun-draw`를 설치할 plugin 이름으로 바꿔 실행합니다. plugin 이름은 아래 표에 있습니다.

Claude Code 입력창에서 marketplace를 등록하고 plugin을 설치하는 명령입니다.

```bash
/plugin marketplace add choisungwook/akbun-aitools
/plugin install akbun-draw@akbun-aitools
/reload-plugins
```

Codex에서 marketplace를 등록하고 plugin을 설치하는 명령입니다.

```bash
codex plugin marketplace add choisungwook/akbun-aitools --json
codex plugin add akbun-draw@akbun-aitools --json
```

Antigravity는 Google 공식 marketplace만 등록할 수 있어서 저장소를 받은 뒤 plugin 폴더를 지정해 설치합니다. 아래 명령은 이 저장소의 모든 plugin을 한 번에 설치합니다. 설치하면 `~/.gemini/config/plugins/`로 복사되므로 받은 폴더는 지워도 됩니다. 새 agent 세션부터 skill이 보입니다.

```bash
rm -rf /tmp/akbun-aitools
git clone --depth 1 https://github.com/choisungwook/akbun-aitools /tmp/akbun-aitools
for d in /tmp/akbun-aitools/plugins/*/; do agy plugin install "${d%/}"; done
```

## 재설치

plugin을 최신 버전으로 다시 받을 때 씁니다. 외부 marketplace는 자동으로 갱신되지 않습니다.

Claude Code의 plugin 하나를 지우고 marketplace를 갱신한 뒤 다시 설치하는 터미널 명령입니다. 끝나면 Claude Code에서 `/reload-plugins`를 실행합니다.

```bash
P=akbun-draw
claude plugin uninstall $P@akbun-aitools
claude plugin marketplace update akbun-aitools
claude plugin install $P@akbun-aitools
```

Codex의 plugin 하나를 지우고 캐시를 비운 뒤 다시 설치하는 터미널 명령입니다.

```bash
P=akbun-draw
codex plugin remove $P@akbun-aitools --json
rm -rf ~/.codex/plugins/cache/akbun-aitools ~/.codex/.tmp/marketplaces/akbun-aitools
codex plugin marketplace add choisungwook/akbun-aitools --json
codex plugin add $P@akbun-aitools --json
codex plugin list --json
```

Antigravity의 모든 plugin을 지우고 남은 복사본까지 비운 뒤 저장소를 새로 받아 다시 설치하는 터미널 명령입니다. 끝나면 agent 세션을 새로 엽니다.

```bash
rm -rf /tmp/akbun-aitools
git clone --depth 1 https://github.com/choisungwook/akbun-aitools /tmp/akbun-aitools
for d in /tmp/akbun-aitools/plugins/*/; do
  P=$(basename "$d")
  agy plugin uninstall "$P"
  rm -rf ~/.gemini/config/plugins/"$P"
  agy plugin install "${d%/}"
done
agy plugin list --json
```

## plugin

| plugin | 하는 일 |
|---|---|
| [akbun-writing](#akbun-writing) | 기술 글 쓰기, 문서 교정 |
| [akbun-draw](#akbun-draw) | 그림 프롬프트, 모션그래픽 영상, 만화 |
| [akbun-draw-architecture](#akbun-draw-architecture) | AWS·시스템 구조 다이어그램 |
| [akbun-presentation](#akbun-presentation) | 발표 덱과 대본 |
| [akbun-learning](#akbun-learning) | 개념 학습, 영상 대본, 발음, Anki |
| [akbun-analysis](#akbun-analysis) | 코드 변경 조사와 리뷰 |
| [akbun-agent-ops](#akbun-agent-ops) | agent 기억과 세션 맥락 |
| [akbun-pulse](#akbun-pulse) | GitHub·Readwise 하루·기간 요약 |
| [akbun-editvideo](#akbun-editvideo) | DaVinci Resolve 영상 편집 |
| [akbun-youtube](#akbun-youtube) | 채널·영상 설정과 분석 |
| [akbun-contentcreator](#akbun-contentcreator) | 악분일상 영상 주제·대본·업로드 준비물(제목·블로그·쇼츠) |

## plugin 예시

그림을 누르면 그 skill 문서로 이동합니다.

### akbun-draw 예시

<table>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-motion-doodle/SKILL.md"><img src="./imgs/akbun-draw-motion-doodle.png" alt="akbun-draw-motion-doodle" width="260"></a><br><code>akbun-draw-motion-doodle</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-code-window-lilac/SKILL.md"><img src="./imgs/akbun-draw-code-window-lilac.jpg" alt="akbun-draw-code-window-lilac" width="260"></a><br><code>akbun-draw-code-window-lilac</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-code-nari/SKILL.md"><img src="./imgs/akbun-draw-code-nari.jpg" alt="akbun-draw-code-nari" width="260"></a><br><code>akbun-draw-code-nari</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-raon/SKILL.md"><img src="./imgs/akbun-draw-raon.jpg" alt="akbun-draw-raon" width="260"></a><br><code>akbun-draw-raon</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-mascot-whale/SKILL.md"><img src="./imgs/akbun-mascot-whale.png" alt="akbun-mascot-whale" width="260"></a><br><code>akbun-mascot-whale</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-explain-sora/SKILL.md"><img src="./imgs/akbun-draw-explain-sora.jpg" alt="akbun-draw-explain-sora" width="260"></a><br><code>akbun-draw-explain-sora</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-animation-dami/SKILL.md"><img src="./imgs/akbun-draw-animation-dami.jpg" alt="akbun-draw-animation-dami" width="260"></a><br><code>akbun-draw-animation-dami</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-thumbnail-retro/SKILL.md"><img src="./imgs/akbun-draw-thumbnail-retro.jpg" alt="akbun-draw-thumbnail-retro" width="260"></a><br><code>akbun-draw-thumbnail-retro</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-thumbnail-doodle/SKILL.md"><img src="./imgs/akbun-draw-thumbnail-doodle.jpg" alt="akbun-draw-thumbnail-doodle" width="260"></a><br><code>akbun-draw-thumbnail-doodle</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-chalkboard/SKILL.md"><img src="./imgs/akbun-draw-chalkboard.png" alt="akbun-draw-chalkboard" width="260"></a><br><code>akbun-draw-chalkboard</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-bori/SKILL.md"><img src="./imgs/akbun-draw-bori.jpg" alt="akbun-draw-bori" width="260"></a><br><code>akbun-draw-bori</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-moss/SKILL.md"><img src="./imgs/akbun-draw-moss/toaster-morning.jpg" alt="akbun-draw-moss toaster-morning" width="260"></a><br><a href="./plugins/akbun-draw/skills/akbun-draw-moss/SKILL.md"><img src="./imgs/akbun-draw-moss/dumpling-carry.jpg" alt="akbun-draw-moss dumpling-carry" width="260"></a><br><a href="./plugins/akbun-draw/skills/akbun-draw-moss/SKILL.md"><img src="./imgs/akbun-draw-moss/rain-umbrella.jpg" alt="akbun-draw-moss rain-umbrella" width="260"></a><br><code>akbun-draw-moss</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-learning-mono/SKILL.md"><img src="./imgs/akbun-draw-learning-mono.jpg" alt="akbun-draw-learning-mono" width="260"></a><br><code>akbun-draw-learning-mono</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-diagram-haru/SKILL.md"><img src="./imgs/akbun-draw-diagram-haru.jpg" alt="akbun-draw-diagram-haru" width="260"></a><br><code>akbun-draw-diagram-haru</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-wash/SKILL.md"><img src="./imgs/akbun-draw-wash.jpg" alt="akbun-draw-wash" width="260"></a><br><code>akbun-draw-wash</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-template-comedy/SKILL.md"><img src="./imgs/akbun-draw-template-comedy.jpg" alt="akbun-draw-template-comedy" width="260"></a><br><code>akbun-draw-template-comedy</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-template-cartoon/SKILL.md"><img src="./imgs/akbun-draw-template-cartoon.jpg" alt="akbun-draw-template-cartoon" width="260"></a><br><code>akbun-draw-template-cartoon</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-sena/SKILL.md"><img src="./imgs/akbun-draw-sena.jpg" alt="akbun-draw-sena" width="260"></a><br><code>akbun-draw-sena</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-juno/SKILL.md"><img src="./imgs/akbun-draw-juno.jpg" alt="akbun-draw-juno" width="260"></a><br><code>akbun-draw-juno</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-storybook-vintage/SKILL.md"><img src="./imgs/akbun-draw-storybook-vintage.jpg" alt="akbun-draw-storybook-vintage" width="260"></a><br><code>akbun-draw-storybook-vintage</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-title-nib/SKILL.md"><img src="./imgs/akbun-draw-title-nib.jpg" alt="akbun-draw-title-nib" width="260"></a><br><code>akbun-draw-title-nib</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-gaon/SKILL.md"><img src="./imgs/akbun-draw-gaon.jpg" alt="akbun-draw-gaon" width="260"></a><br><code>akbun-draw-gaon</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-title-pastel/SKILL.md"><img src="./imgs/akbun-draw-title-pastel.jpg" alt="akbun-draw-title-pastel" width="260"></a><br><code>akbun-draw-title-pastel</code></td>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-character-hana/SKILL.md"><img src="./imgs/akbun-draw-character-hana.png" alt="akbun-draw-character-hana" width="260"></a><br><code>akbun-draw-character-hana</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-draw/skills/akbun-draw-character-byeol/SKILL.md"><img src="./imgs/akbun-draw-character-byeol/mira.png" alt="akbun-draw-character-byeol mira" width="84"></a><a href="./plugins/akbun-draw/skills/akbun-draw-character-byeol/SKILL.md"><img src="./imgs/akbun-draw-character-byeol/yuna.png" alt="akbun-draw-character-byeol yuna" width="84"></a><a href="./plugins/akbun-draw/skills/akbun-draw-character-byeol/SKILL.md"><img src="./imgs/akbun-draw-character-byeol/beomsu.png" alt="akbun-draw-character-byeol beomsu" width="84"></a><br><code>akbun-draw-character-byeol</code></td>
</tr>
</table>

### akbun-presentation 예시

<table>
<tr>
<td><a href="./plugins/akbun-presentation/skills/akbun-presentation-paper/SKILL.md"><img src="./imgs/akbun-presentation.png" alt="akbun-presentation-paper" width="400"></a><br><code>akbun-presentation-paper</code></td>
</tr>
</table>

### akbun-editvideo 예시

<table>
<tr>
<td><a href="./plugins/akbun-editvideo/skills/akbun-edit-page-tour-lilac/SKILL.md"><img src="./imgs/akbun-edit-page-tour-lilac.jpg" alt="akbun-edit-page-tour-lilac" width="400"></a><br><code>akbun-edit-page-tour-lilac</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-editvideo/skills/akbun-edit-quote-cards-lilac/SKILL.md"><img src="./imgs/akbun-edit-quote-cards-lilac.jpg" alt="akbun-edit-quote-cards-lilac" width="400"></a><br><code>akbun-edit-quote-cards-lilac</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/SKILL.md"><img src="./imgs/akbun-davinciresolve-explainer.gif" alt="akbun-davinciresolve-explainer" width="400"></a><br><code>akbun-davinciresolve-explainer</code></td>
</tr>
<tr>
<td><a href="./plugins/akbun-editvideo/skills/akbun-davinciresolve-motion-stamp/SKILL.md"><img src="./imgs/akbun-davinciresolve-motion-stamp.jpg" alt="akbun-davinciresolve-motion-stamp" width="400"></a><br><code>akbun-davinciresolve-motion-stamp</code></td>
</tr>
</table>

### explainer 색 조합과 도형 스타일

`akbun-davinciresolve-explainer`는 호출할 때 색 조합과 도형 스타일을 고릅니다. 말하지 않으면 `night` 색과 `gouache` 도형입니다. 각 그림의 왼쪽은 `gouache` 도형(손채색 질감, 붓 화살표), 오른쪽은 `akbun` 도형(akbun-presentation-paper의 테두리 상자와 곧은 화살표)입니다. 색 값은 [palettes.jsonl](./plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/references/palettes.jsonl)에 있습니다.

| 색 조합 | 색 | 미리보기 |
|---|---|---|
| `night` (기본) | 배경 `#202020`, 사람 `#9A9EA6`, 상자 `#F0A040` `#17F0D8` `#FF5F8F` `#91CCA3`, 강조 `#FFD84D` | <img src="./imgs/explainer-palette-night.jpg" alt="night" width="480"> |
| `apple-orchard` | 배경 `#E8E9E5`, `#796236` `#D2AF7D` `#6A8871` `#907C6C` | <img src="./imgs/explainer-palette-apple-orchard.jpg" alt="apple-orchard" width="480"> |
| `fiery-ocean` | 배경 `#FDF0D5`, `#780000` `#C1121F` `#003049` `#669BBC` | <img src="./imgs/explainer-palette-fiery-ocean.jpg" alt="fiery-ocean" width="480"> |
| `akbun` | 배경 `#000000`, 기본 `#FFFFFF`, 강조 주황 `#FF8A00`, 문제 빨강 `#FF3B30` | <img src="./imgs/explainer-palette-akbun.jpg" alt="akbun" width="480"> |

색 조합과 도형 스타일을 정해 호출하는 예입니다.

```text
$akbun-davinciresolve-explainer 이 대본을 fiery-ocean 색, akbun 도형으로 만들어줘.
```

## plugin 목록

표의 오른쪽 칸은 그 skill을 쓰면 좋은 상황입니다. skill 이름을 누르면 문서로 이동합니다. 그림 스킬을 고르는 자세한 기준은 [그림 스킬 매뉴얼](docs/manual_draw.md), 영상 편집 스킬은 [영상 편집 매뉴얼](docs/manual_editvideo.md)에 있습니다.

### akbun-writing

<details><summary>기술 글 쓰기, 문서 교정, 운영 공지</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-writing](./plugins/akbun-writing/skills/akbun-writing/) | 기술 블로그 글을 akbun 말투로 처음부터 쓸 때 |
| [akbun-writing-with-question](./plugins/akbun-writing/skills/akbun-writing-with-question/) | 독자가 질문을 따라가며 개념을 익히는 학습형 글이 필요할 때 |
| [akbun-writing-humanize](./plugins/akbun-writing/skills/akbun-writing-humanize/) | AI가 쓴 부연스러운 글을 내가 고른 견본 문체로 자연스럽게 다시 쓰고 싶을 때 |
| [akbun-docs-review](./plugins/akbun-writing/skills/akbun-docs-review/) | 기술 문서의 용어가 들쭉날쭉하거나 사실 확인이 필요할 때 |
| [akbun-voice-diary](./plugins/akbun-writing/skills/akbun-voice-diary/) | 말로 한 하루를 일기로 남기고 공부 일정까지 잡고 싶을 때 |
| [akbun-thumbnail-review](./plugins/akbun-writing/skills/akbun-thumbnail-review/) | 올리기 전 유튜브 썸네일이 잘 읽히는지 점검할 때 |
| [akbun-markdown-to-html-pandoc](./plugins/akbun-writing/skills/akbun-markdown-to-html-pandoc/) | markdown 글을 블로그에 붙일 HTML로 바꿀 때 |
| [akbun-md-to-notion](./plugins/akbun-writing/skills/akbun-md-to-notion/) | markdown·Obsidian 문서를 Notion 페이지로 옮기거나 맞출 때 |

</details>

### akbun-draw

<details><summary>그림 프롬프트, 모션그래픽 영상, 만화</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-draw-motion-doodle](./plugins/akbun-draw/skills/akbun-draw-motion-doodle/) | 흰 종이 낙서 캐릭터가 연기하는 짧은 모션그래픽이 필요할 때 |
| [akbun-draw-code-window-lilac](./plugins/akbun-draw/skills/akbun-draw-code-window-lilac/) | 코드를 한 줄씩 타이핑하며 짚어 주는 영상 장면이 필요할 때 |
| [akbun-draw-code-nari](./plugins/akbun-draw/skills/akbun-draw-code-nari/) | 터미널·AI 도구 화면 녹화에 화살표·라벨을 붙여 짚는 영상 장면이 필요할 때 |
| [akbun-draw-explain-sora](./plugins/akbun-draw/skills/akbun-draw-explain-sora/) | 어두운 배경 손채색 그림으로 비유·대화를 보여 주는 설명 장면이 필요할 때 |
| [akbun-draw-raon](./plugins/akbun-draw/skills/akbun-draw-raon/) | 연필 막대 인물로 개념을 일상 비유로 풀어 줄 때 |
| [akbun-draw-diagram-haru](./plugins/akbun-draw/skills/akbun-draw-diagram-haru/) | 시스템 구조·요청 흐름을 흰 바탕 손그림 다이어그램 이미지로 만들 때 |
| [akbun-draw-bori](./plugins/akbun-draw/skills/akbun-draw-bori/) | 아늑한 배경 속 동글동글한 동물들의 일상 장면 그림이 필요할 때 |
| [akbun-draw-moss](./plugins/akbun-draw/skills/akbun-draw-moss/) | 굵은 잉크 선·단색 면에 강조색 하나만 칠한 엉뚱한 한 컷이 필요할 때 |
| [akbun-draw-wash](./plugins/akbun-draw/skills/akbun-draw-wash/) | 흰 종이 여백이 넓은 펜 선·수채 칠 동물 장면 그림이 필요할 때 |
| [akbun-draw-sena](./plugins/akbun-draw/skills/akbun-draw-sena/) | 사람 없는 장면을 바랜 옛 필름 사진처럼 담은 이미지가 필요할 때 |
| [akbun-draw-storybook-vintage](./plugins/akbun-draw/skills/akbun-draw-storybook-vintage/) | 사물·동물 장면을 옛 그림책 수채 삽화처럼 그린 이미지가 필요할 때 |
| [akbun-draw-gaon](./plugins/akbun-draw/skills/akbun-draw-gaon/) | 가는 펜 선으로 세부 많은 건물과 얼굴 없는 작은 인물이 있는 거리·장소 풍경을 낮이나 밤으로 그리고 싶을 때 |
| [akbun-draw-title-nib](./plugins/akbun-draw/skills/akbun-draw-title-nib/) | 이미 있는 그림에 옛 그림책 표지 같은 손글씨 제목을 그려 넣고 싶을 때 |
| [akbun-draw-title-pastel](./plugins/akbun-draw/skills/akbun-draw-title-pastel/) | 그림이나 사진 위에 크레용으로 덧그린 듯한 굵은 손글씨 제목을 넣고 싶을 때 |
| [akbun-draw-character-hana](./plugins/akbun-draw/skills/akbun-draw-character-hana/) | 1990년대 TV 셀 애니메이션 느낌의 오리지널 인물 그림이 필요할 때 |
| [akbun-draw-character-byeol](./plugins/akbun-draw/skills/akbun-draw-character-byeol/) | 직업·외모 같은 페르소나로 배경 없는 캐릭터 그림을 만들 때 |
| [akbun-draw-juno](./plugins/akbun-draw/skills/akbun-draw-juno/) | 여행지 거리를 무광 색감의 카메라 스냅 사진이나 고정 카메라 반복 영상으로 담고 싶을 때 |
| [akbun-draw-template-comedy](./plugins/akbun-draw/skills/akbun-draw-template-comedy/) | 다정한 제목과 그 뒤 웃긴 속사정을 보여 주는 개그 한 컷을 원하는 그림체로 만들 때 |
| [akbun-draw-template-cartoon](./plugins/akbun-draw/skills/akbun-draw-template-cartoon/) | 쓰던 그림체 그대로 4컷 만화·인스타툰·유튜브 커뮤니티 만화를 만들 때 |
| [akbun-draw-animation-dami](./plugins/akbun-draw/skills/akbun-draw-animation-dami/) | 짧은 이야기를 회화풍 세로 애니메이션 쇼츠로 만들 때 |
| [akbun-draw-learning-mono](./plugins/akbun-draw/skills/akbun-draw-learning-mono/) | 논문·학습 자료를 흑백 16:9 학습 이미지와 대본으로 바꿀 때 |
| [akbun-draw-thumbnail-retro](./plugins/akbun-draw/skills/akbun-draw-thumbnail-retro/) | IT·여행 글과 영상의 썸네일을 레트로 포스터처럼 만들고 싶을 때 |
| [akbun-draw-thumbnail-doodle](./plugins/akbun-draw/skills/akbun-draw-thumbnail-doodle/) | 블로그·유튜브 썸네일을 낙서 그림체 한 장(16:9·4:3)으로 만들 때 |
| [akbun-draw-chalkboard](./plugins/akbun-draw/skills/akbun-draw-chalkboard/) | 시스템 구조·개념을 칠판 분필 그림체 16:9 SVG 한 장으로 설명 영상·슬라이드에 넣을 때 |
| [akbun-mascot-whale](./plugins/akbun-draw/skills/akbun-mascot-whale/) | 다른 그림에 akbun 고래 마스코트를 같은 모습으로 넣어야 할 때 |

</details>

### akbun-draw-architecture

<details><summary>AWS·시스템 구조 다이어그램</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-drawio-aws-vpc](./plugins/akbun-draw-architecture/skills/akbun-drawio-aws-vpc/) | AWS VPC 구성을 draw.io에서 고칠 수 있는 다이어그램으로 남길 때 |
| [akbun-draw-architecture](./plugins/akbun-draw-architecture/skills/akbun-draw-architecture/) | 시스템 경계와 데이터 흐름을 아키텍처 그림 한 장으로 보여 줄 때 |

</details>

### akbun-presentation

<details><summary>발표 덱과 대본</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-presentation-paper](./plugins/akbun-presentation/skills/akbun-presentation-paper/) | 논문형식(배경·방법·결과)으로 발표 덱과 대본을 만들 때 |
| [akbun-presentation](./plugins/akbun-presentation/skills/akbun-presentation/) | 다크 고정 디자인으로 발표 덱과 대본을 만들 때 |
| [akbun-presentation-visual](./plugins/akbun-presentation/skills/akbun-presentation-visual/) | 발표 슬라이드에 넣을 16:9 설명 그림이 필요할 때 |

</details>

### akbun-learning

<details><summary>개념 학습, 영상 대본, 발음, Anki</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-driven-learning](./plugins/akbun-learning/skills/akbun-driven-learning/) | 내가 이해한 내용을 확인받으며 개념을 파고들 때 |
| [akbun-describe-youtube-transcript](./plugins/akbun-learning/skills/akbun-describe-youtube-transcript/) | 유튜브 영상의 말을 한국어 대본으로 옮겨 읽고 싶을 때 |
| [akbun-describe-twitter-transcript](./plugins/akbun-learning/skills/akbun-describe-twitter-transcript/) | x.com 영상 내용을 대본으로 정리하고 싶을 때 |
| [akbun-learning-english](./plugins/akbun-learning/skills/akbun-learning-english/) | 영어 문장의 발음과 끊어 읽기를 익힐 때 |
| [akbun-learning-japanese](./plugins/akbun-learning/skills/akbun-learning-japanese/) | 일본어 문장의 발음과 읽기를 익힐 때 |
| [akbun-make-anki-japanese](./plugins/akbun-learning/skills/akbun-make-anki-japanese/) | 일본어 단어·문장 사진이나 PDF를 Anki 덱으로 만들 때 |

</details>

### akbun-analysis

<details><summary>코드 변경 조사와 리뷰</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-analysis-git-whyandhow](./plugins/akbun-analysis/skills/akbun-analysis-git-whyandhow/) | 이 코드·PR이 왜, 어떻게 바뀌었는지 알아야 할 때 |
| [akbun-analysis-gitdiff-blast-radius](./plugins/akbun-analysis/skills/akbun-analysis-gitdiff-blast-radius/) | 머지 전에 이 변경이 어디를 깨뜨릴지 확인할 때 |
| [akbun-analysis-adversarial-review](./plugins/akbun-analysis/skills/akbun-analysis-adversarial-review/) | 코드나 주장이 정말 맞는지 반례로 흔들어 볼 때 |
| [akbun-analysis-token-credential](./plugins/akbun-analysis/skills/akbun-analysis-token-credential/) | 토큰·API 키를 누가 발급하고 누가 읽는지 따져 볼 때 |

</details>

### akbun-agent-ops

<details><summary>agent 기억과 세션 맥락</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-memory-setup](./plugins/akbun-agent-ops/skills/akbun-memory-setup/) | agent가 기억할 구조를 처음 만들 때 |
| [akbun-recall](./plugins/akbun-agent-ops/skills/akbun-recall/) | 새 세션에서 이전 작업 맥락을 이어받을 때 |
| [akbun-reflect](./plugins/akbun-agent-ops/skills/akbun-reflect/) | 세션에서 배운 것을 SKILL.md에 남길 때 |

</details>

### akbun-pulse

<details><summary>GitHub·Readwise 하루·기간 요약</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [github-daily-pulse](./plugins/akbun-pulse/skills/github-daily-pulse/) | 오늘 GitHub에서 한 일을 복습 문서로 정리할 때 |
| [github-period-pulse](./plugins/akbun-pulse/skills/github-period-pulse/) | 한 기간의 GitHub 결과를 주간회의 브리프로 만들 때 |
| [readwise-daily-pulse](./plugins/akbun-pulse/skills/readwise-daily-pulse/) | 어제 Readwise에 쌓인 글을 한 번에 훑고 싶을 때 |

</details>

### akbun-editvideo

<details><summary>DaVinci Resolve 영상 편집</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-davinciresolve-workflow](./plugins/akbun-editvideo/skills/akbun-davinciresolve-workflow/) | 말소리 없는 여행 브이로그를 처음부터 끝까지 편집할 때 |
| [akbun-davinciresolve-timeline-chrono](./plugins/akbun-editvideo/skills/akbun-davinciresolve-timeline-chrono/) | 촬영한 클립을 찍은 시간순으로 늘어놓고 싶을 때 |
| [davinciresolve-cut-travelflow](./plugins/akbun-editvideo/skills/davinciresolve-cut-travelflow/) | 여행 클립을 흐름 있게 자르고 흔들림을 잡을 때 |
| [akbun-davinciresolve-cut-new-york](./plugins/akbun-editvideo/skills/akbun-davinciresolve-cut-new-york/) | 도시 풍경을 리듬감 있는 몽타주로 이을 때 |
| [akbun-davinciresolve-logconvert](./plugins/akbun-editvideo/skills/akbun-davinciresolve-logconvert/) | Log로 찍은 영상인지 판정하고 LUT로 변환할 때 |
| [akbun-davinciresolve-exposure](./plugins/akbun-editvideo/skills/akbun-davinciresolve-exposure/) | 시간대가 다른 클립의 밝기를 맞출 때 |
| [akbun-davinciresolve-whitebalance](./plugins/akbun-editvideo/skills/akbun-davinciresolve-whitebalance/) | 클립마다 색온도가 달라 화면이 누렇거나 퍼렇게 보일 때 |
| [akbun-davinciresolve-contrast](./plugins/akbun-editvideo/skills/akbun-davinciresolve-contrast/) | 화면이 밋밋해 대비를 잡아야 할 때 |
| [akbun-davinciresolve-saturation](./plugins/akbun-editvideo/skills/akbun-davinciresolve-saturation/) | 색이 바래 보여 채도를 조금 보충할 때 |
| [akbun-davinciresolve-sky](./plugins/akbun-editvideo/skills/akbun-davinciresolve-sky/) | 하늘만 진하게 살리고 싶을 때 |
| [akbun-davinciresolve-look-japan-summer](./plugins/akbun-editvideo/skills/akbun-davinciresolve-look-japan-summer/) | 밝고 산뜻한 일본 여름 느낌의 룩을 입힐 때 |
| [akbun-davinciresolve-look-tokyo-night](./plugins/akbun-editvideo/skills/akbun-davinciresolve-look-tokyo-night/) | 네온이 도는 도쿄 야경 룩을 입힐 때 |
| [akbun-davinciresolve-look-still](./plugins/akbun-editvideo/skills/akbun-davinciresolve-look-still/) | 차분한 자연주의 드라마 룩을 입힐 때 |
| [akbun-davinciresolve-look-new-york](./plugins/akbun-editvideo/skills/akbun-davinciresolve-look-new-york/) | 도시적인 뉴욕 룩을 입힐 때 |
| [davinciresolve-face-privacy](./plugins/akbun-editvideo/skills/davinciresolve-face-privacy/) | 얼굴이 보이는 장면을 넓고 약하게 가릴 때 |
| [davinciresolve-face-mosaic](./plugins/akbun-editvideo/skills/davinciresolve-face-mosaic/) | 필요한 영역만 얼굴 모자이크하고 배경은 그대로 둘 때 |
| [akbun-davinciresolve-make-caption](./plugins/akbun-editvideo/skills/akbun-davinciresolve-make-caption/) | 영상에 자막·챕터 제목을 넣거나 같은 모양의 자막을 다시 쓰고 싶을 때 |
| [davinciresolve-youtube-shorts](./plugins/akbun-editvideo/skills/davinciresolve-youtube-shorts/) | 긴 영상에서 세로 Shorts를 뽑아 렌더·업로드할 때 |
| [akbun-vlog-shotsketch](./plugins/akbun-editvideo/skills/akbun-vlog-shotsketch/) | 한 샷의 구도·카메라 위치·빛을 미리 정할 때 |
| [davinciresolve-style-project](./plugins/akbun-editvideo/skills/davinciresolve-style-project/) | 프로젝트 과정을 기록하는 diary형 영상의 편집 기준이 필요할 때 |
| [akbun-davinciresolve-explainer-dark-diagram](./plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer-dark-diagram/) | 어두운 다이어그램 설명 영상을 만들고 내 녹음에 맞출 때 |
| [akbun-davinciresolve-explainer](./plugins/akbun-editvideo/skills/akbun-davinciresolve-explainer/) | 대본을 그림이 자막에 맞춰 튀어나오는 설명 영상으로 만들고, 색 조합·도형 스타일을 골라 쓰고 싶을 때 |
| [akbun-davinciresolve-motion-stamp](./plugins/akbun-editvideo/skills/akbun-davinciresolve-motion-stamp/) | 내레이션 영상의 사진 컷을 숫자·키워드 모션그래픽으로 바꿀 때 |
| [akbun-davinciresolve-narration-cleanup](./plugins/akbun-editvideo/skills/akbun-davinciresolve-narration-cleanup/) | 녹음한 내레이션의 숨소리·긴 쉼을 정리할 때 |
| [akbun-edit-page-tour-lilac](./plugins/akbun-editvideo/skills/akbun-edit-page-tour-lilac/) | 웹 페이지 스크린샷을 짚어 가며 설명할 때 |
| [akbun-edit-quote-cards-lilac](./plugins/akbun-editvideo/skills/akbun-edit-quote-cards-lilac/) | 인용 글 카드를 쌓고 형광펜으로 강조할 때 |

</details>

### akbun-youtube

<details><summary>채널·영상 설정과 분석</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-youtube-plan-channel-settings](./plugins/akbun-youtube/skills/akbun-youtube-plan-channel-settings/) | 채널을 만들거나 정비하며 설정표가 필요할 때 |
| [akbun-youtube-set-video-metadata](./plugins/akbun-youtube/skills/akbun-youtube-set-video-metadata/) | 올린 영상의 제목·설명·태그를 입력할 때 |
| [akbun-youtube-translate-title-description](./plugins/akbun-youtube/skills/akbun-youtube-translate-title-description/) | 제목·설명을 여러 언어로 등록할 때 |
| [akbun-youtube-analyze-my-videos](./plugins/akbun-youtube/skills/akbun-youtube-analyze-my-videos/) | 내 영상들의 지표를 비교해 볼 때 |
| [akbun-youtube-analyze-my-style](./plugins/akbun-youtube/skills/akbun-youtube-analyze-my-style/) | 내 영상 스타일을 정리해 다음 영상에 쓰고 싶을 때 |

</details>

### akbun-contentcreator

<details><summary>악분일상 영상 주제·대본·업로드 준비물(제목·블로그·쇼츠)</summary>

| skill | 이럴 때 쓰세요 |
|---|---|
| [akbun-contentcreator-topic-finder](./plugins/akbun-contentcreator/skills/akbun-contentcreator-topic-finder/) | 다음 영상 주제를 공식 문서·보안 뉴스·블로그 인기 글에서 찾을 때 |
| [akbun-contentcreator-script-builder](./plugins/akbun-contentcreator/skills/akbun-contentcreator-script-builder/) | 옵시디언 공부 노트를 문제→예상→실험→결과 대본과 15초 훅으로 바꿀 때 |
| [akbun-contentcreator-publish-kit](./plugins/akbun-contentcreator/skills/akbun-contentcreator-publish-kit/) | 확정된 대본으로 제목·썸네일 문구, 티스토리 글, 쇼츠 대본을 한 번에 또는 골라서 만들 때 |

</details>
