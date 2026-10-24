"""프레임 PNG들에서 많이 쓰인 색과 채도 높은 강조색을 뽑는다.

uv run --python 3.12 --with pillow python -I sample_palette.py a.png b.png
uv run --python 3.12 --with pillow python -I sample_palette.py --selftest
"""
import sys
from collections import Counter
from PIL import Image

STEP = 6  # 비슷한 색을 묶는 양자화 폭


def palette(paths, top=12, accents=20):
  c = Counter()
  for p in paths:
    for px in Image.open(p).convert("RGB").getdata():
      c[tuple(v // STEP * STEP for v in px)] += 1
  sat = Counter({k: n for k, n in c.items() if max(k) - min(k) > 60 and max(k) > 120})
  return c.most_common(top), sat.most_common(accents)


def hexc(k):
  return "#%02X%02X%02X" % k


if __name__ == "__main__":
  if sys.argv[1:] == ["--selftest"]:
    import tempfile, os
    im = Image.new("RGB", (10, 10), (6, 6, 6)); im.putpixel((0, 0), (252, 102, 102))
    f = os.path.join(tempfile.mkdtemp(), "t.png"); im.save(f)
    common, acc = palette([f])
    assert hexc(common[0][0]) == "#060606" and hexc(acc[0][0]) == "#FC6666", (common, acc)
    print("selftest ok"); sys.exit()
  common, acc = palette(sys.argv[1:])
  print("most common:"); [print(hexc(k), n) for k, n in common]
  print("accents:"); [print(hexc(k), n) for k, n in acc]
