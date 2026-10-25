---
name: akbun-davinciresolve-explainer
description: 대본을 얼굴 없는 설명 영상 DaVinci Resolve 타임라인으로 만든다. 단색 배경 위 그림(사람·컴포넌트 상자·원통·코드 카드·화살표)이 자막에 맞춰 하나씩 튀어나오고, 강조는 점선 상자와 펀치 인으로만 한다. 색 조합(night 기본, apple-orchard, fiery-ocean, akbun)과 도형 스타일(gouache 기본, akbun)은 호출할 때 고른다. 장면은 JSON spec으로 쓰고, 모양·색은 references의 jsonl 라이브러리에서만 가져와 scripts/scene.py가 SVG·레이어 PNG·Fusion comp를 만들고 채점한다. 사용자가 직접 호출할 때만 실행한다.
disable-model-invocation: true
---

# akbun-davinciresolve-explainer

얼굴 없는 내레이션 설명 영상을 만든다. 같은 입력이면 누가 만들어도 같은 모양·색·위치·시점이 나와야 한다. 그래서 이 문서는 규칙을 담지 않고, 어떤 결정을 어느 파일이 정하는지만 정한다.

## 라우팅

| 정하려는 것 | 읽거나 고치는 파일 |
|---|---|
| 장면에 무엇을, 어느 순서로, 언제 둘지(spec 쓰는 법) | [references/spec.md](references/spec.md) |
| 모양(사람·상자·원통·코드 카드·화살표·점선 상자·✕·태그)의 치수·색 키·모션 | [references/shapes.jsonl](references/shapes.jsonl) |
| 색 조합(`night` 기본, `apple-orchard`, `fiery-ocean`, `akbun`)과 색 키마다 쓰는 곳 | [references/palettes.jsonl](references/palettes.jsonl) |
| 도형 스타일(`gouache` 기본, `akbun` = akbun-presentation-paper 도형 언어) | [references/shape-styles.jsonl](references/shape-styles.jsonl) |
| 가로 배치(row) 위치 | [references/layout.jsonl](references/layout.jsonl) |
| 합격 여부 | [references/checklist.jsonl](references/checklist.jsonl), `scripts/scene.py check` |
| Resolve 타임라인·자막 트랙·comp 넣기·확인 | [references/resolve.md](references/resolve.md) |
| 스킬을 고친 뒤의 시험(5개, 95%) | [references/testing.md](references/testing.md) |
| 정답 예시 spec | [references/example/](references/example/) |
| Template 매크로·Timing 노드 원리, 좌표와 단위(다른 explainer 스타일 스킬도 쓰는 공통 구현) | [references/resolve-core.md](references/resolve-core.md) |
| 녹음 정리 | [akbun-davinciresolve-narration-cleanup](../akbun-davinciresolve-narration-cleanup/SKILL.md) |

## 실행

이 스킬 디렉터리에서 `uv run --python 3.12`로 돌린다. 레이어 PNG 렌더는 [akbun-draw-night-gouache](../../../akbun-draw/skills/akbun-draw-night-gouache/SKILL.md)의 `render_gouache.py`를 불러 쓴다.

장면마다 자막 시각을 얻고 spec을 빌드한 뒤, 장면 전체를 한 번에 채점하고, 통과하면 타임라인 fps로 comp를 만드는 명령이다.

```bash
uv run --python 3.12 scripts/scene.py timing "<장면 자막 1>" "<장면 자막 2>"
uv run --python 3.12 scripts/scene.py build <작업 폴더>/spec/s1.json <작업 폴더>/out/
uv run --python 3.12 scripts/scene.py check <작업 폴더>/out/ <작업 폴더>/spec/s1.json <작업 폴더>/spec/s2.json
uv run --python 3.12 scripts/scene.py comp <작업 폴더>/spec/s1.json <작업 폴더>/out/ --fps 24
```

1. 사용자가 호출에서 색 조합·도형 스타일을 말했으면 그 id를, 아니면 기본값을 쓴다(따로 묻지 않는다). 대본을 spec 표(theme·자막·레이어·at·펀치 인)로 나누고 장면마다 `timing`으로 `subs`·`dur`를 얻어 사용자에게 먼저 확인받는다.
2. `build` → `check`. 장면별·`set` 점수가 모두 95% 이상이어야 다음으로 간다. 떨어지면 spec을 고쳐 다시 돈다. SVG를 손으로 고치지 않는다.
3. `comp` → resolve.md 순서대로 타임라인에 넣고 확인한다.
4. 완료 보고: 타임라인 이름·fps·길이, 장면 시작 프레임, `check` 출력, 코드 카드의 파일 경로·줄 범위, 자막 트랙 잠금 해제·스타일 적용 결과, 제너레이터 길이 복원 결과. 확인하지 못한 것(재생, 청취)은 따로 적는다.
