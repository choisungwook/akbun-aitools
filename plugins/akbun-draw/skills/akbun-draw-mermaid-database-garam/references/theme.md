# garam 테마

Mermaid 코드 맨 위에 아래 frontmatter를 한 글자도 바꾸지 않고 붙인다. 베이지 둥근 노드와 테라코타 글자, 파란 테두리 알약 모양 화살표 라벨, 옅은 회색 가는 선, 테두리만 있는 DB 상자를 만든다. 글꼴은 SIL OFL인 Pretendard와 Noto Sans KR이고, 둘 다 없으면 보는 사람 환경의 sans-serif로 그린다.

```yaml
---
config:
  theme: base
  themeVariables:
    fontFamily: "Pretendard, 'Noto Sans KR', sans-serif"
    fontSize: 15px
    background: "#FAFAF8"
    primaryColor: "#F3E7E1"
    primaryBorderColor: "#E9DAD3"
    primaryTextColor: "#C8714F"
    lineColor: "#8C8C8C"
    clusterBkg: "#FAFAF8"
    clusterBorder: "#E6E6E6"
    titleColor: "#222222"
    edgeLabelBackground: "#FAFAF8"
  themeCSS: |
    .node rect { rx: 18px; ry: 18px; }
    .nodeLabel, .node .label { font-weight: 500; }
    .edgeLabel, .edgeLabel p, .edgeLabel .labelBkg { background: transparent !important; }
    .edgeLabel span.edgeLabel { display: inline-block; background: #FAFAF8 !important; color: #C8714F !important; font-weight: 500; border: 1.5px solid #4A86E8; border-radius: 999px; padding: 2px 12px; }
    .edgeLabel foreignObject { overflow: visible; }
    .flowchart-link { stroke-width: 1px !important; }
    .cluster-label .nodeLabel, .cluster-label span { color: #222222 !important; font-weight: 400; }
---
```

`themeCSS`는 Mermaid 11 HTML 라벨 기준이다. 렌더러가 frontmatter나 `themeCSS`를 막으면(예: GitHub) 색 없이 기본 테마로 그려질 뿐 관계도 내용은 같다. Mermaid 11.4.1에서 frontmatter의 `flowchart.curve`·간격 값은 적용되지 않아 넣지 않는다.
