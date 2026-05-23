# draw.io CLI와 XML 핵심 규칙

이 reference는 사용자가 제공한 draw.io 공식 글(`Generate and validate draw.io diagrams with AI`, draw.io Style Reference, `mxfile.xsd`)에서 이 skill에 필요한 내용만 한국어로 줄인 것이다.

## CLI

- draw.io Desktop 앱은 export용 CLI를 포함한다.
- macOS 기본 경로:

```bash
/Applications/draw.io.app/Contents/MacOS/draw.io
```

- PATH에 `drawio`가 있으면 그것을 먼저 사용하고, 없으면 macOS 기본 경로를 확인한다.
- export 기본 명령:

```bash
drawio -x -f png -e -b 10 -o output.drawio.png input.drawio
```

옵션 의미:

- `-x`: export 모드
- `-f`: 출력 형식. `png`, `svg`, `pdf`, `jpg`
- `-e`: PNG/SVG/PDF 안에 diagram XML을 embed
- `-b`: 다이어그램 주변 여백
- `-o`: 출력 파일
- `-p`: page index 선택

이 skill은 draw server를 사용하지 않는다. CLI export가 실패하면 draw.io Desktop 설치 여부와 CLI 경로를 먼저 확인한다.
Codex sandbox에서 `Abort trap`이 발생하면 XML 문제가 아니라 GUI 앱 실행 제한일 수 있다. 이 경우 사용자 승인을 받아 sandbox 밖에서 CLI를 실행하거나, computer-use로 draw.io Desktop export를 수행한다.

## XML 구조

AI가 생성할 때는 사람이 읽고 검증할 수 있는 uncompressed XML을 사용한다.

```xml
<mxfile host="Electron" type="device">
  <diagram id="aws-vpc" name="AWS VPC">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1"
                  tooltips="1" connect="1" arrows="1" fold="1"
                  page="1" pageScale="1" pageWidth="1200" pageHeight="760"
                  math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

필수 규칙:

- `id="0"` root cell과 `id="1" parent="0"` default layer를 반드시 넣는다.
- visible shape는 `vertex="1"`을 사용한다.
- connector는 `edge="1"`을 사용하고 `source`, `target`으로 shape id를 참조한다.
- edge에는 `<mxGeometry relative="1" as="geometry"/>`가 필요하다.
- style은 `key=value;` 형식으로 작성한다.
- 모든 cell id는 diagram 안에서 고유해야 한다.
- 좌표는 왼쪽 위가 원점이다. x는 오른쪽, y는 아래로 증가한다.
- HTML label은 XML attribute 안에서 escape한다.
- XML comment는 넣지 않는다.
- compressed/base64 diagram은 만들지 않는다.

## 검증 체크

- XML이 well-formed인지 확인한다.
- root가 `<mxfile>`이고 diagram이 하나 이상 있는지 확인한다.
- 모든 parent가 존재하는 cell id를 참조하는지 확인한다.
- edge source/target이 실제 vertex id인지 확인한다.
- non-rectangular shape는 필요한 perimeter를 style에 포함한다.
- 라벨 값은 plain text 한 줄만 사용한다. `<br>` 같은 HTML tag나 HTML entity 줄바꿈을 넣지 않는다.
- 이 skill에서는 VPC와 subnet label에 CIDR을 넣는다. 사용자가 CIDR을 모르면 `10.x` 기반 기본값을 제안하고 확인받는다.
- 포트 번호, 계정 번호처럼 다이어그램을 복잡하게 만드는 값은 사용자가 명시적으로 요구할 때만 넣는다.
