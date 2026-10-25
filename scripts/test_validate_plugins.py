import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_plugins import ROOT, bump_errors, plugin_errors, plugins_in_paths


class BumpTests(unittest.TestCase):
  def test_one_step_bump_is_accepted(self):
    for head in ("1.0.16", "1.1.0", "2.0.0"):
      with self.subTest(head=head):
        self.assertEqual(bump_errors({"p"}, {"p": "1.0.15"}, {"p": head}), [])

  def test_same_or_skipped_version_is_rejected(self):
    for head in ("1.0.15", "1.0.17", "1.2.0", "0.9.0"):
      with self.subTest(head=head):
        self.assertTrue(bump_errors({"p"}, {"p": "1.0.15"}, {"p": head}))

  def test_new_plugin_and_unchanged_plugin_are_skipped(self):
    self.assertEqual(bump_errors({"new"}, {"new": None}, {"new": "1.0.0"}), [])
    self.assertEqual(bump_errors(set(), {"p": "1.0.0"}, {"p": "1.0.0"}), [])


class ChangedPluginTests(unittest.TestCase):
  def test_both_sides_of_a_move_count_and_manifests_do_not(self):
    paths = ["plugins/a/skills/s/SKILL.md", "plugins/b/skills/s/SKILL.md", "plugins/c/.claude-plugin/plugin.json", "README.md", "plugins"]
    self.assertEqual(plugins_in_paths(paths), {"a", "b"})


class RepositoryTests(unittest.TestCase):
  def copy_repo(self, root):
    shutil.copytree(ROOT / "plugins", root / "plugins")
    shutil.copy2(ROOT / "README.md", root / "README.md")
    shutil.copytree(ROOT / "docs", root / "docs")

  def test_current_repository_is_consistent(self):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      self.copy_repo(root)
      self.assertEqual(plugin_errors(root), [])

  def test_renamed_skill_and_version_mismatch_are_rejected(self):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      self.copy_repo(root)
      skill = root / "plugins/akbun-draw/skills/akbun-mascot-whale"
      skill.rename(skill.with_name("akbun-mascot-renamed"))
      manifest = root / "plugins/akbun-writing/.codex-plugin/plugin.json"
      data = json.loads(manifest.read_text())
      data["version"] = "9.9.9"
      manifest.write_text(json.dumps(data))
      errors = plugin_errors(root)
      self.assertTrue(any("디렉터리 이름과 다름" in error for error in errors))
      self.assertTrue(any("'## plugin 목록'에 없는 skill" in error for error in errors))
      self.assertTrue(any("존재하지 않는 skill 링크" in error for error in errors))
      self.assertTrue(any("akbun-writing: manifest" in error for error in errors))


  def test_old_table_header_and_manual_gaps_are_rejected(self):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      self.copy_repo(root)
      readme = root / "README.md"
      readme.write_text(readme.read_text().replace("| skill | 이럴 때 쓰세요 |", "| skill | 하는 일 |", 1))
      manual = root / "docs/manual_draw.md"
      manual.write_text(manual.read_text().replace("akbun-draw-slate-marker/SKILL.md", "akbun-draw-gone/SKILL.md"))
      errors = plugin_errors(root)
      self.assertTrue(any("머리줄" in error and "하는 일" in error for error in errors))
      self.assertTrue(any("빠진 skill akbun-draw-slate-marker" in error for error in errors))
      self.assertTrue(any("존재하지 않는 skill akbun-draw-gone" in error for error in errors))
      readme.write_text(readme.read_text().replace("| 기술 블로그 글을 akbun 말투로 처음부터 쓸 때 |", "| akbun 스타일 기술 글 |", 1)
                        .replace("| skill | 이럴 때 쓰세요 |", "| Skill | 설명 | 비고 |", 1))
      manual.write_text(manual.read_text().replace("../plugins/akbun-draw/skills/akbun-mascot-whale/SKILL.md", "../plugin/akbun-draw/skills/akbun-mascot-whale/SKILL.md"))
      errors = plugin_errors(root)
      self.assertTrue(any("akbun-writing 행은" in error for error in errors))
      self.assertTrue(any("'| Skill | 설명 | 비고 |'" in error for error in errors))
      self.assertTrue(any("깨진 링크 ../plugin/akbun-draw" in error for error in errors))
      manual.unlink()
      self.assertIn("docs/manual_draw.md 없음", plugin_errors(root))


if __name__ == "__main__":
  unittest.main()
