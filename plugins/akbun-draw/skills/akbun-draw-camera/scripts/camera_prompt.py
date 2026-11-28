"""만화·일러스트 skill이 함께 쓰는 camera 값의 로더와 검사.

값은 references/cameras.jsonl 한 곳에서만 고친다.
  --selftest   자체 검사
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROWS = {r["id"]: r for r in map(json.loads, filter(str.strip, (Path(__file__).resolve().parents[1] / "references" / "cameras.jsonl").read_text().splitlines()))}
CAMERAS = {k: r["prompt"] for k, r in ROWS.items()}
FULL_BODY = {k for k, r in ROWS.items() if r["full_body"]}  # 인물의 전신이 화면에 다 들어오는 값


def bad_camera(camera, people, allowed=CAMERAS):
    """camera 값의 실패 이유. 없으면 None."""
    if not isinstance(camera, str) or camera not in allowed:
        return f"camera는 {sorted(allowed)} 중 하나: {camera}"
    if people < ROWS[camera]["min_people"]:
        return f"camera {camera}는 그 장면에 인물이 {ROWS[camera]['min_people']}명 이상일 때만 쓴다"
    return None


def framing(camera):
    """한 장에 한 장면인 프롬프트의 앞머리(FORMAT 바로 뒤)에 둘 샷 문장. 뒤에 두면 그림체의 전신 묘사에 밀린다.
    한 장에 여러 컷이면 컷마다 다르므로 PANEL 문장 안에 둔다. camera가 없으면 빈 목록."""
    return [f"FRAMING (highest priority, overrides every later description of body, ground or layout): {CAMERAS[camera]}"] if camera else []


if __name__ == "__main__" and sys.argv[1:] == ["--selftest"]:
    assert len(CAMERAS) == 9 and all(p.startswith("Camera:") for p in CAMERAS.values())
    assert FULL_BODY == {"full", "low", "high", "top"}
    assert bad_camera(["x"], 2) and bad_camera("nope", 2) and bad_camera("tilt", 1) and not bad_camera("tilt", 2)
    assert bad_camera("close", 2, FULL_BODY) and framing(None) == [] and CAMERAS["low"] in framing("low")[0]
    table = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text()
    assert all(f"| `{k}` | {r['ko']} | {r['when']}" in table for k, r in ROWS.items()), "SKILL.md 표가 cameras.jsonl과 다름"
    print("selftest ok")
