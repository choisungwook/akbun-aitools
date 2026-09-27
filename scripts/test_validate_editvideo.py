import shutil
import tempfile
import unittest
from pathlib import Path

from validate_editvideo import ROOT, frontmatter_errors, repository_errors


VALID = "---\nname: sample\ndescription: 설명\ndisable-model-invocation: true\n---\n# Sample\n"


class FrontmatterTests(unittest.TestCase):
  def test_direct_invocation_key_is_supported(self):
    self.assertEqual(frontmatter_errors(VALID, "sample"), [])

  def test_policy_cannot_be_removed_or_misspelled(self):
    for content in (VALID.replace("disable-model-invocation: true\n", ""), VALID.replace("invocation", "invokation")):
      with self.subTest(content=content):
        self.assertTrue(frontmatter_errors(content, "sample"))

  def test_policy_requires_boolean_true(self):
    for value in ('"true"', "false", "1"):
      with self.subTest(value=value):
        self.assertTrue(frontmatter_errors(VALID.replace("true", value), "sample"))

  def test_malformed_metadata_is_rejected(self):
    for content in (VALID.replace("description: 설명", "description: ["), VALID.replace("description: 설명", "description: ''"), VALID.replace("name: sample", "name: wrong")):
      with self.subTest(content=content):
        self.assertTrue(frontmatter_errors(content, "sample"))


class RepositoryTests(unittest.TestCase):
  def test_stale_inventory_and_missing_prompt_are_rejected(self):
    with tempfile.TemporaryDirectory() as temporary:
      root = Path(temporary)
      for name in ("plugins", "docs"):
        shutil.copytree(ROOT / name, root / name)
      for name in ("README.md", "AGENTS.md"):
        shutil.copy2(ROOT / name, root / name)
      self.assertEqual(repository_errors(root), [])
      skill = root / "plugins/akbun-editvideo/skills/akbun-davinciresolve-look-still"
      skill.rename(skill.with_name("akbun-davinciresolve-look-renamed"))
      errors = repository_errors(root)
      self.assertTrue(any("목록 누락" in error for error in errors))
      self.assertTrue(any("없는 링크" in error for error in errors))
      self.assertTrue(any("prompt 오류" in error for error in errors))


if __name__ == "__main__":
  unittest.main()
