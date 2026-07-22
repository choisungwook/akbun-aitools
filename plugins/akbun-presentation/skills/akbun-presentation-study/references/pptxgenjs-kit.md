# pptxgenjs 스타일 키트 (스터디, 다크 스텝)

akbun 스터디 발표 스타일의 실행본이다. 상수와 헬퍼를 그대로 복사해 시작한다(`npm i pptxgenjs`).
실제 렌더링으로 검증된 코드다.

이 키트는 [../design.md](../design.md)의 스타일 스펙을 pptxgenjs로 구현한 것이다. 색·좌표·크기
값은 design.md를 단일 기준으로 삼는다. design.md를 고치면 이 키트의 해당 상수·좌표도 맞춘다.

공통 주의사항: 색상 hex에 `#`를 붙이지 않는다. 불릿은 `bullet: true` 또는 접두 문자로만 쓴다.
텍스트를 도형과 정렬할 때는 항상 `margin: 0`. pptxgen 인스턴스 하나로 파일 하나만 만든다.
`\n`은 줄바꿈으로 렌더링된다.

## 테마 상수와 슬라이드 헬퍼

스터디(다크 스텝) 테마 상수와 슬라이드 헬퍼:

```javascript
const pptxgen = require("pptxgenjs");

// ---- 스터디(다크 스텝) 테마 상수 ----
const C = {
  bg: "252525",     // 배경
  text: "EBEBEB",   // 본문 텍스트
  line: "FFFFFF",   // 도형 테두리/화살표
  point: "FFC000",  // 포인트(주인공/강조)
  danger: "FF0000", // 문제/에러
  black: "000000",
};
const FONT = "Gmarket Sans Medium";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.defineSlideMaster({ title: "AKBUN", background: { color: C.bg } });

// 표지: 제목 + 부제
function coverSlide(title, subtitle) {
  const s = pres.addSlide({ masterName: "AKBUN" });
  s.addText(title, { x: 0.9, y: 2.7, w: 11.5, h: 1.2, fontSize: 54, bold: true, fontFace: FONT, color: C.line, margin: 0 });
  if (subtitle) s.addText(subtitle, { x: 0.9, y: 3.9, w: 11.5, h: 0.6, fontSize: 20, fontFace: FONT, color: C.text, margin: 0 });
  return s;
}

// 훅/질문/섹션: 빈 화면 중앙 큰 글씨 (줄바꿈은 \n)
function hookSlide(text, size = 36) {
  const s = pres.addSlide({ masterName: "AKBUN" });
  s.addText(text, { x: 0.9, y: 2.9, w: 11.5, h: 1.7, fontSize: size, fontFace: FONT, color: C.text, align: "center", margin: 0 });
  return s;
}

// 내용 슬라이드: 상단 헤더(덱 주제 반복) + 메시지 한 줄
function contentSlide(header, message) {
  const s = pres.addSlide({ masterName: "AKBUN" });
  s.addText(header, { x: 0.46, y: 0.39, w: 9.5, h: 0.57, fontSize: 28, fontFace: FONT, color: C.text, margin: 0 });
  if (message) {
    s.addText([{ text: message, options: { bullet: true } }], { x: 0.75, y: 1.0, w: 11.9, h: 0.5, fontSize: 16, fontFace: FONT, color: C.text, margin: 0 });
  }
  return s;
}

// 컴퍼넌트 박스: 채움 없음 + 얇은 흰 테두리 + 가운데 라벨
function box(s, label, x, y, w, h, opts = {}) {
  s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: opts.lineColor || C.line, width: opts.lineWidth || 1 } });
  s.addText(label, { x, y, w, h, align: "center", valign: "middle", fontSize: opts.fontSize || 12, fontFace: FONT, color: opts.textColor || C.text, margin: 0 });
}

// 주인공 박스: 노랑 채움 + 검정 bold 라벨 (슬라이드당 1~2개)
function pointBox(s, label, x, y, w, h, opts = {}) {
  s.addShape("rect", { x, y, w, h, fill: { color: C.point }, line: { color: C.point, width: 1 } });
  s.addText(label, { x, y, w, h, align: "center", valign: "middle", fontSize: opts.fontSize || 12, bold: true, fontFace: FONT, color: C.black, margin: 0 });
}

// 논리 경계: 점선 흰 사각형 + 경계선 위 왼쪽 라벨
function groupBox(s, label, x, y, w, h) {
  s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: C.line, width: 1, dashType: "dash" } });
  s.addText(label, { x: x + 0.08, y: y - 0.32, w: w - 0.1, h: 0.3, fontSize: 11, fontFace: FONT, color: C.text, margin: 0 });
}

// 화살표: 흰 실선 + 선 위 라벨. 문제 흐름은 { color: C.danger, labelColor: C.danger }
function arrow(s, x1, y1, x2, y2, label, opts = {}) {
  s.addShape("line", {
    x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color: opts.color || C.line, width: opts.width || 1.5, endArrowType: "triangle", dashType: opts.dashType || "solid" },
  });
  if (label) {
    s.addText(label, { x: Math.min(x1, x2) - 0.3, y: (y1 + y2) / 2 - 0.42, w: Math.abs(x2 - x1) + 0.6, h: 0.3, align: "center", fontSize: 11, fontFace: FONT, color: opts.labelColor || C.text, margin: 0 });
  }
}

// 숫자 마커: 정상 스텝 = 노랑 원 + 검정 숫자, 문제 스텝 = 빨강 원 + 흰 숫자
function marker(s, n, x, y, danger = false) {
  const d = 0.32;
  s.addShape("ellipse", { x, y, w: d, h: d, fill: { color: danger ? C.danger : C.point }, line: { color: danger ? C.danger : C.point, width: 1 } });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontSize: 12, bold: true, fontFace: FONT, color: danger ? C.line : C.black, margin: 0 });
}

// 문제 표시: 빨간 X
function xMark(s, x, y) {
  s.addText("✕", { x, y, w: 0.4, h: 0.4, align: "center", valign: "middle", fontSize: 22, bold: true, fontFace: FONT, color: C.danger, margin: 0 });
}

// 명령어 박스: 얇은 흰 테두리 안 명령어 한 줄
function codeBox(s, command, x, y, w, h) {
  s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: C.line, width: 1 } });
  s.addText(command, { x: x + 0.15, y, w: w - 0.3, h, valign: "middle", fontSize: 16, fontFace: FONT, color: C.text, margin: 0 });
}

// 말풍선: 흰 채움 + 검정 텍스트 (스토리텔링용)
function bubble(s, text, x, y, w, h) {
  s.addShape("wedgeRoundRectCallout", { x, y, w, h, fill: { color: C.line }, line: { color: C.line, width: 1 } });
  s.addText(text, { x, y, w, h, align: "center", valign: "middle", fontSize: 10, fontFace: FONT, color: C.black, margin: 0 });
}

// ... 위 헬퍼로 슬라이드를 구성한 뒤:
pres.writeFile({ fileName: "output.pptx" });
```

## macOS에서 QA (렌더링 확인)

LibreOffice가 없어도 Microsoft PowerPoint가 설치돼 있으면 AppleScript로 PDF를 뽑아 확인할 수
있다. PowerPoint는 샌드박스라서 **자기 컨테이너 안의 파일만** 안정적으로 열고 저장한다. 실행 전
PowerPoint에 열려 있는 문서를 닫아야 한다(다른 문서가 열려 있으면 `active presentation`이 그
문서를 가리킨다). 자동화가 "Parameter error"나 "User canceled"로 실패하면 사용자가 PowerPoint를
쓰는 중일 수 있으니 반복 시도하지 말고 사용자에게 파일을 직접 열어 확인해달라고 안내한다.

PowerPoint 컨테이너로 복사해 PDF로 변환하는 스크립트:

```bash
PPTC="$HOME/Library/Containers/com.microsoft.Powerpoint/Data"
cp output.pptx "$PPTC/output.pptx"
osascript <<'EOF'
set f to POSIX file (do shell script "echo $HOME/Library/Containers/com.microsoft.Powerpoint/Data/output.pptx")
tell application "Microsoft PowerPoint"
    activate
    delay 2
    open f
    delay 2
    save active presentation in "out.pdf" as save as PDF
    close active presentation saving no
    quit
end tell
EOF
mv "$PPTC/out.pdf" ./output.pdf && rm "$PPTC/output.pptx"
```

PDF를 슬라이드 이미지로 바꿔 눈으로 확인:

```bash
pdftoppm -jpeg -r 100 output.pdf slide
```

확인 항목: 텍스트 잘림·겹침(라벨과 마커, 라벨과 화살표), 색 문법 위반, 헤더 위치·형식 통일,
슬라이드당 메시지 한 줄.
