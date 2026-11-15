# 예시 결과물

detail 모드가 실제로 만든 결과를 PNG로 둔다. 처음 보는 사람이 detail.pptx가 어떻게 생겼는지 알고, skill을 고칠 때마다 전과 후를 비교하려고 둔다.

## 목록

| 디렉터리 | 입력 | 컷 |
|---|---|---|
| [cdp-tistory/](cdp-tistory/) | 블로그 글 "Claude는 어떻게 내 컴퓨터의 글을 티스토리에 올릴까"와 cdp-browser-access 핸즈온 코드 | 39개, 7분 39초 |

`storyboard.json`은 summary 키와 detail 키가 모두 들어간 spec이다. `slide_NN.png`는 `detail.pptx`에서 고른 장이다. 장 40개를 모두 넣지 않고, 첫 장(공통 규칙)과 source가 다른 컷을 하나씩 둔다.

| 그림 | detail.pptx 장 | 보여 주는 것 |
|---|---|---|
| `slide_01.png` | 1 | 제작 공통 규칙과 `motion_style` |
| `slide_02.png` | 3 (컷 2) | `사진·자료` 컷. 공개 공지 URL을 채운 `record` |
| `slide_03.png` | 14 (컷 13) | `모션그래픽` 컷. 스크립트가 조립한 AI 영상 프롬프트 |
| `slide_04.png` | 21 (컷 20) | `화면 녹화` 컷. 코드 심볼을 그대로 쓴 비트 |
| `slide_05.png` | 37 (컷 36) | 답이 나오는 컷(`answer_cut`) |

## 전과 후 비교

skill의 규칙이나 스크립트를 고쳤으면 같은 변경에서 예시를 다시 만든다.

1. `cdp-tistory/storyboard.json`을 출력 폴더에 복사하고 summary 예시와 같은 방법으로 스케치를 준비한다. 검사에 걸리면 spec을 새 규칙에 맞게 고친다.
2. `dami_detail.py build`로 `detail.pptx`를 만든다.
3. summary skill의 `slides_to_png.py`로 장마다 PNG를 내보내고, 위 표의 장을 같은 이름으로 덮어쓴다. `storyboard.json`도 덮어쓴다.

장마다 PNG로 내보내는 명령이다(macOS). `<summary>`는 `../akbun-youtube-storyboard-dami/`다.

```bash
uv run --python 3.12 <summary>/scripts/slides_to_png.py storyboard-output/<작업명>/detail.pptx <내보낼 폴더>
```

pptx는 저장소에 올리지 않는다. 이전 그림을 따로 남기지 않고 같은 이름을 덮어써 git이 전과 후를 짝지어 보여 주게 한다.
