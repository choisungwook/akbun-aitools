# pptxgenjs 스타일 키트 (외부 발표, 라이트 샌드위치)

akbun 외부 발표 스타일의 실행본이다. 상수와 헬퍼를 그대로 복사해 시작한다(`npm i pptxgenjs`).
실제 렌더링으로 검증된 코드다.

이 키트는 [../design.md](../design.md)의 스타일 스펙을 pptxgenjs로 구현한 것이다. 색·좌표·크기
값은 design.md를 단일 기준으로 삼는다. design.md를 고치면 이 키트의 해당 상수·좌표도 맞춘다.

공통 주의사항: 색상 hex에 `#`를 붙이지 않는다. 불릿은 `bullet: true` 또는 접두 문자(■/-)로만
쓴다. 텍스트를 도형과 정렬할 때는 항상 `margin: 0`. pptxgen 인스턴스 하나로 파일 하나만 만든다.
`\n`은 줄바꿈으로 렌더링된다.

## 테마 상수와 슬라이드 헬퍼

외부 발표(라이트 샌드위치) 테마 상수와 슬라이드 헬퍼:

```javascript
const pptxgen = require("pptxgenjs");

// ---- 외부 발표(라이트 샌드위치) 테마 상수 ----
const L = {
  dark: "212022",    // 표지/섹션 배경
  white: "FFFFFF",
  text: "000000",
  gray: "7F7F7F",    // 출처 캡션
  point: "FFC000",   // 노랑 포인트(세로 바, 표지 키워드)
  danger: "FF0000",  // 빨강 강조
  podFill: "FFF2CC", // 워크로드 연노랑
  resFill: "E2EFDA", // 리소스 연초록
  groupFill: "F2F2F2",
  codeBg: "1E1E1E",
  codeText: "D4D4D4",
  codeKey: "569CD6",
  codeStr: "CE9178",
};
const FONT = "나눔바른고딕";
const CODEFONT = "Consolas";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
// 페이지 번호: 표지를 제외한 모든 슬라이드. 다크 마스터는 회색, 라이트 마스터는 검정.
pres.defineSlideMaster({
  title: "AKBUN_DARK",
  background: { color: L.dark },
  slideNumber: { x: 12.6, y: 7.05, w: 0.5, h: 0.3, color: L.gray, fontFace: FONT, fontSize: 11 },
});
pres.defineSlideMaster({
  title: "AKBUN_COVER",
  background: { color: L.dark },
});
pres.defineSlideMaster({
  title: "AKBUN_LIGHT",
  background: { color: L.white },
  slideNumber: { x: 12.6, y: 7.05, w: 0.5, h: 0.3, color: L.text, fontFace: FONT, fontSize: 11 },
});

// 표지: 다크 + 제목(핵심 키워드만 노랑) + 우하단 발표자 정보
function coverSlide(titleRuns, presenter, email) {
  const s = pres.addSlide({ masterName: "AKBUN_COVER" });
  s.addText(titleRuns, { x: 0.9, y: 2.2, w: 11.5, h: 1.0, fontSize: 40, bold: true, fontFace: FONT, align: "center", margin: 0 });
  s.addText(`발표자: ${presenter}\n${email}`, { x: 7.4, y: 5.4, w: 5.0, h: 0.9, fontSize: 18, bold: true, fontFace: FONT, color: L.white, align: "right", margin: 0 });
  return s;
}
// 사용 예: coverSlide([{ text: "Redis 캐시 스탬피드", options: { color: L.point } },
//                     { text: " 대응기", options: { color: L.white } }], "이름", "email@example.com")

// 섹션 표지: 다크 + 노란 세로 바 + 흰 bold 제목 (+부제)
function sectionSlide(title, subtitle) {
  const s = pres.addSlide({ masterName: "AKBUN_DARK" });
  s.addShape("rect", { x: 0.42, y: 2.9, w: 0.18, h: 1.0, fill: { color: L.point }, line: { color: L.point, width: 0 } });
  s.addText(title, { x: 0.95, y: 2.9, w: 11.5, h: 1.0, fontSize: 40, bold: true, fontFace: FONT, color: L.white, margin: 0 });
  if (subtitle) s.addText(`- ${subtitle}`, { x: 1.0, y: 3.95, w: 11.0, h: 0.5, fontSize: 20, fontFace: FONT, color: L.white, margin: 0 });
  return s;
}

// 내용 슬라이드: 흰 배경 + "N. 섹션명" 헤더 + ■/- 불릿 계층
// bullets: [[0, "메인"], [1, "서브"], ...] — level 0 = ■ 14pt, level 1 = "- " 12pt
function lightContent(header, bullets = []) {
  const s = pres.addSlide({ masterName: "AKBUN_LIGHT" });
  s.addText(header, { x: 0.42, y: 0.2, w: 10.5, h: 0.5, fontSize: 18, bold: true, fontFace: FONT, color: L.text, margin: 0 });
  const runs = bullets.map(([level, text]) => ({
    text: (level === 0 ? "■ " : "  - ") + text,
    options: { breakLine: true, fontSize: level === 0 ? 14 : 12 },
  }));
  if (runs.length) s.addText(runs, { x: 0.79, y: 0.96, w: 11.8, h: 0.35 * bullets.length + 0.2, fontFace: FONT, color: L.text, margin: 0, valign: "top" });
  return s;
}

// 전환/질문 멘트: 흰 배경 중앙 큰 글씨 (해요체 허용, \n로 2~4줄 스택)
function transitionSlide(text) {
  const s = pres.addSlide({ masterName: "AKBUN_LIGHT" });
  s.addText(text, { x: 1.5, y: 2.6, w: 10.3, h: 2.3, fontSize: 32, bold: true, fontFace: FONT, color: L.text, align: "center", valign: "middle", margin: 0 });
  return s;
}

// 컴퍼넌트 박스: 흰 채움 + 얇은 검정 테두리. opts.fill로 L.podFill/L.resFill/L.groupFill 지정
function lbox(s, label, x, y, w, h, opts = {}) {
  s.addShape("rect", { x, y, w, h, fill: { color: opts.fill || L.white }, line: { color: L.text, width: 0.75 } });
  s.addText(label, { x, y, w, h, align: "center", valign: "middle", fontSize: opts.fontSize || 11, bold: !!opts.bold, fontFace: FONT, color: L.text, margin: 0 });
}

// 논리 경계(노드·클러스터·호스트): 둥근 모서리 얇은 검정 테두리 + 안쪽 왼쪽 위 라벨
function lgroup(s, label, x, y, w, h) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.08, fill: { color: L.white }, line: { color: L.text, width: 0.75 } });
  s.addText(label, { x: x + 0.12, y: y + 0.05, w: w - 0.2, h: 0.3, fontSize: 11, bold: true, fontFace: FONT, color: L.text, margin: 0 });
}

// 화살표: 데이터 흐름 = 검정 실선. 설정·강조 흐름 = { color: L.danger, dashType: "dash", labelColor: L.danger }
function larrow(s, x1, y1, x2, y2, label, opts = {}) {
  s.addShape("line", { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: opts.color || L.text, width: opts.width || 1.25, endArrowType: "triangle", dashType: opts.dashType || "solid" } });
  if (label) s.addText(label, { x: Math.min(x1, x2) - 0.3, y: (y1 + y2) / 2 - 0.38, w: Math.abs(x2 - x1) + 0.6, h: 0.28, align: "center", fontSize: 10, bold: true, fontFace: FONT, color: opts.labelColor || L.text, margin: 0 });
}

// 순서 마커는 서클 숫자 문자를 그대로 쓴다
const CIRC = ["①", "②", "③", "④", "⑤"];

// 코드 패널: 검정 배경 + VS Code Dark+ 색 런
// lines: [[["apiVersion", "key"], [": v1", "plain"]], [["  ttl", "key"], [": ", "plain"], ["\"3600\"", "str"]]]
function codePanel(s, lines, x, y, w, h) {
  s.addShape("rect", { x, y, w, h, fill: { color: L.codeBg }, line: { color: L.codeBg, width: 0 } });
  const colorOf = { key: L.codeKey, str: L.codeStr, plain: L.codeText };
  const runs = [];
  lines.forEach((segs) => {
    segs.forEach((seg, j) => {
      runs.push({ text: seg[0], options: { color: colorOf[seg[1]] || L.codeText, breakLine: j === segs.length - 1 } });
    });
  });
  s.addText(runs, { x: x + 0.12, y: y + 0.08, w: w - 0.24, h: h - 0.16, fontSize: 10, fontFace: CODEFONT, valign: "top", margin: 0 });
}

// 푸터 링크: 좌하단 github/유투브 데모 링크
function footerLinks(s, links) {
  s.addText(links.join("     "), { x: 0.3, y: 7.12, w: 11.5, h: 0.28, fontSize: 10, fontFace: FONT, color: L.text, margin: 0 });
}

// 출처 캡션: 이미지·인용 아래
function sourceCaption(s, text, x, y, w) {
  s.addText(`[ 출처: ${text} ]`, { x, y, w, h: 0.26, fontSize: 9, fontFace: FONT, color: L.gray, align: "center", margin: 0 });
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
페이지 번호(표지 제외 전 슬라이드).
