# /// script
# requires-python = ">=3.12"
# dependencies = ["python-pptx"]
# ///
"""storyboard.pptx의 장을 slide_NN.png로 내보낸다. examples/의 전·후 비교용 그림을 만들 때 쓴다.

  slides_to_png.py <storyboard.pptx> <출력 폴더>

macOS 전용이다(Quick Look의 qlmanage를 쓴다). 다른 환경에서는 쓸 수 있는 도구로 장마다 PNG를 내보낸다.
Quick Look은 첫 장만 그리므로 장마다 그 장 하나만 남긴 사본을 만들어 그린다.
발표자 노트가 있으면 Quick Look이 멈추므로 사본에서는 노트를 뺀다.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from pptx import Presentation

WIDTH = 1600  # 내보내는 그림의 폭(px)


def main(src, out):
    src, out = Path(src), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    n = len(Presentation(str(src)).slides)
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(n):
            prs = Presentation(str(src))
            ids = prs.slides._sldIdLst
            keep = ids[i]
            for el in list(ids):
                if el is not keep:
                    prs.part.drop_rel(el.rId)
                    ids.remove(el)
            part = prs.slides[0].part
            for rid in [r.rId for r in part.rels.values() if r.reltype.endswith("/notesSlide")]:
                part.drop_rel(rid)
            one = Path(tmp) / f"slide_{i + 1:02d}.pptx"
            prs.save(str(one))
            subprocess.run(["qlmanage", "-t", "-s", str(WIDTH), "-o", tmp, str(one)], capture_output=True, timeout=120, check=True)
            Path(tmp, one.name + ".png").replace(out / f"slide_{i + 1:02d}.png")
    print(f"slides {n}장 -> {out}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
