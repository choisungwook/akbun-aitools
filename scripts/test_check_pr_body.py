import unittest

from check_pr_body import body_errors, risk_tier


BODY = """<!-- 안내 -->
# 구현

skill 설명 한 줄 수정
- SKILL.md 설명 줄 교체

# 구조

```mermaid
flowchart LR
  skill[SKILL.md]:::changed --> script[scripts/render.py]
  classDef changed stroke-width:3px
```

# 검증

- validate_plugins.py → 오류 0건

# 리스크

등급: 중간
- 설명 문장의 뜻이 바뀌었는지는 사람이 읽어야 함

Closes #12
"""


class TierTests(unittest.TestCase):
  def test_change_sets_tier(self):
    self.assertEqual(risk_tier(["README.md", "imgs/a.png"])[0], "낮음")
    self.assertEqual(risk_tier(["README.md", "plugins/akbun-draw/skills/x/SKILL.md"])[0], "중간")
    self.assertEqual(risk_tier(["plugins/akbun-draw/skills/x/SKILL.md", ".github/workflows/a.yml"])[0], "높음")
    for path in ("AGENTS.md", "CLAUDE.md", "scripts/check_pr_body.py", ".claude/settings.json", ".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"):
      with self.subTest(path=path):
        self.assertEqual(risk_tier([path])[0], "높음")


class BodyTests(unittest.TestCase):
  def test_complete_body_passes(self):
    self.assertEqual(body_errors(BODY, "중간"), [])

  def test_low_tier_may_omit_risk(self):
    body = BODY.replace("# 리스크\n\n등급: 중간\n- 설명 문장의 뜻이 바뀌었는지는 사람이 읽어야 함\n", "")
    self.assertEqual(body_errors(body, "낮음"), [])
    self.assertTrue(body_errors(body, "중간"))

  def test_medium_and_high_tier_require_mermaid_structure(self):
    body = BODY.replace("```mermaid\nflowchart LR\n  skill[SKILL.md]:::changed --> script[scripts/render.py]\n  classDef changed stroke-width:3px\n```\n", "- 글로 설명\n")
    self.assertTrue(any("mermaid" in error for error in body_errors(body, "중간")))
    self.assertEqual(body_errors(body.replace("등급: 중간", "등급: 낮음"), "낮음"), [])

  def test_code_block_lines_do_not_count_toward_limit(self):
    body = BODY.replace("  classDef changed stroke-width:3px\n", "".join(f"  n{i} --> n{i + 1}\n" for i in range(40)))
    self.assertEqual(body_errors(body, "중간"), [])

  def test_declared_tier_must_match_changed_paths(self):
    self.assertTrue(body_errors(BODY, "높음"))
    self.assertTrue(body_errors(BODY.replace("등급: 중간", "등급: 낮음"), "중간"))

  def test_missing_sections_are_rejected(self):
    cases = {
      "구현": BODY.replace("skill 설명 한 줄 수정\n- SKILL.md 설명 줄 교체\n", ""),
      "검증": BODY.replace("- validate_plugins.py → 오류 0건\n", ""),
      "형식": BODY.replace("- validate_plugins.py → 오류 0건", "- 확인함"),
      "issue": BODY.replace("Closes #12", "Closes #"),
      "못 보는 것": BODY.replace("- 설명 문장의 뜻이 바뀌었는지는 사람이 읽어야 함\n", ""),
    }
    for name, body in cases.items():
      with self.subTest(name=name):
        self.assertTrue(body_errors(body, "중간"))

  def test_comments_do_not_count_as_content(self):
    body = BODY.replace("- validate_plugins.py → 오류 0건", "<!-- - 명령 → 결과 -->")
    self.assertTrue(body_errors(body, "중간"))

  def test_long_body_is_rejected(self):
    body = BODY + "\n".join(f"- 줄 {i}" for i in range(40))
    self.assertTrue(any("40줄" in error for error in body_errors(body, "중간")))


if __name__ == "__main__":
  unittest.main()
