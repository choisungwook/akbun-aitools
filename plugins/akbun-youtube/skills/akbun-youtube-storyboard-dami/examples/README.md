# 예시 결과물

이 skill이 실제로 만든 결과를 PNG로 둔다. 목적은 둘이다. 처음 보는 사람이 결과가 어떻게 생겼는지 아는 것, 그리고 skill을 고칠 때마다 전과 후를 비교하는 것이다.

## 목록

| 디렉터리 | 입력 | 장르 |
|---|---|---|
| [kubectl-debug/](kubectl-debug/) | "셸이 없는 이미지는 exec가 안 되는데 kubectl debug를 쓰면 된다"는 메모 한 줄 | `it-handson` |

디렉터리마다 들어 있는 것은 같다. `storyboard.json`은 그 결과를 만든 spec, `script.md`는 대본, `slide_NN.png`는 `storyboard.pptx`의 장을 순서대로 내보낸 그림이다. pptx와 스케치 원본은 넣지 않는다.

## 전과 후 비교

skill의 규칙·스크립트·jsonl을 고쳤으면 같은 변경에서 예시를 다시 만든다.

1. 예시의 `storyboard.json`을 출력 폴더에 복사한다. 규칙이 바뀌어 검사에 걸리면 spec을 새 규칙에 맞게 고친다.
2. SKILL.md의 작업 흐름대로 검사, 스케치 생성, `build`를 한다. 스케치 프롬프트가 바뀌지 않았으면 이전 스케치를 다시 쓴다.
3. `storyboard.pptx`를 장마다 PNG로 내보내 `slide_NN.png`를 같은 이름으로 덮어쓰고, `storyboard.json`과 `script.md`도 덮어쓴다. 장 수가 줄었으면 남은 번호의 PNG를 지운다.
4. 전과 후는 git이 보관한다. PR의 파일 변경 화면에서 PNG를 나란히 놓고 본다.

macOS에서 장마다 PNG로 내보내는 명령이다. `<skill>`은 `SKILL.md`가 있는 디렉터리다. 다른 환경에서는 쓸 수 있는 도구로 내보낸다.

```bash
uv run --python 3.12 <skill>/scripts/slides_to_png.py storyboard-output/<작업명>/storyboard.pptx <skill>/examples/<예시 이름>
```

pptx는 저장소에 올리지 않는다(`.gitignore`의 `*.pptx`, `storyboard-output/`). 대표 예시는 PNG로만 남긴다.

이전 그림을 `before/` 같은 폴더로 따로 남기지 않는다. 같은 파일 이름을 덮어써야 git이 전과 후를 짝지어 보여 준다. 새 장르나 새 주제의 예시는 디렉터리를 하나 더 만들고 위 표에 한 줄을 더한다.
