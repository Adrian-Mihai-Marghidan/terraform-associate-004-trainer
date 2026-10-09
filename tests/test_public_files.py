"""Publication checks must inspect indexed data without exposing local records."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_public_files


class PublicFilesTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="mentor-public-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.git("init", "-q")

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments],
                              check=True, capture_output=True, text=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_ignored_local_records_are_not_public_candidates(self):
        self.write(".gitignore", "/private/\n/.tools/\n")
        self.write("README.md", "Use a relative checkout path.\n")
        self.write("private/PROGRESS.json", "private learner evidence")
        self.write(".tools/provider", "local runtime")
        self.git("add", ".")
        issues, count = check_public_files.check(self.root)
        self.assertEqual(issues, [])
        self.assertEqual(count, 2)

    def test_force_added_private_record_is_rejected(self):
        self.write(".gitignore", "/private/\n")
        self.write("private/PROGRESS.json", "private learner evidence")
        self.git("add", ".gitignore")
        self.git("add", "--force", "private/PROGRESS.json")
        issues, _ = check_public_files.check(self.root)
        self.assertTrue(any("private/PROGRESS.json" in issue for issue in issues))

    def test_staged_content_is_checked_even_if_worktree_is_fixed(self):
        self.write("README.md", "/" + "Users/" + "sampleuser/projects/mentor\n")
        self.git("add", "README.md")
        self.write("README.md", "../terraform-azure-simulator\n")
        issues, _ = check_public_files.check(self.root)
        self.assertTrue(any("README.md:1" in issue for issue in issues))

    def test_personal_paths_are_detected_on_supported_home_styles(self):
        examples = (
            "/" + "Users/" + "sampleuser/project",
            "/" + "home/" + "sampleuser/project",
            "C:" + "\\Users\\" + "sampleuser\\project",
        )
        for value in examples:
            with self.subTest(value=value):
                self.assertIsNotNone(check_public_files.PERSONAL_HOME.search(value))

    def test_example_inputs_and_lock_files_remain_publishable(self):
        for name in ("lab/.terraform.lock.hcl", "lab/settings.example.tfvars", ".env.example"):
            self.write(name, "example = true\n")
        self.write("README.md", "Use /absolute/path/to/checkout or ../terraform-azure-simulator.\n")
        self.git("add", ".")
        issues, count = check_public_files.check(self.root)
        self.assertEqual(issues, [])
        self.assertEqual(count, 4)

    def test_runtime_and_credential_paths_are_rejected(self):
        examples = (
            "lab/terraform.tfstate.backup", "lab/change.tfplan", "lab/plan.out",
            "lab/.simulator/infrastructure.json", "lab/infrastructure.sqlite3",
            "lab/settings.tfvars", "lab/settings.tfvars.json", ".env.local",
            "lab/crash.log", "keys/account.pem", ".aws/credentials",
        )
        for name in examples:
            with self.subTest(name=name):
                self.assertIsNotNone(check_public_files.private_path(name))

    def test_git_free_export_checks_actual_contents(self):
        with tempfile.TemporaryDirectory(prefix="mentor-public-export-") as export:
            root = Path(export)
            (root / "README.md").write_text("Use /absolute/path/to/checkout.\n")
            issues, count = check_public_files.check(root, mode="filesystem")
            self.assertEqual(issues, [])
            self.assertEqual(count, 1)
            (root / "private").mkdir()
            (root / "private/PROGRESS.json").write_text("private evidence")
            issues, _ = check_public_files.check(root, mode="filesystem")
            self.assertTrue(any("private/PROGRESS.json" in issue for issue in issues))

    def test_empty_index_cannot_report_success(self):
        issues, count = check_public_files.check(self.root)
        self.assertEqual(count, 0)
        self.assertTrue(any("No public files" in issue for issue in issues))

    def test_checker_source_does_not_match_its_own_path_patterns(self):
        source = Path(check_public_files.__file__).read_text()
        self.assertIsNone(check_public_files.PERSONAL_HOME.search(source))


if __name__ == "__main__":
    unittest.main()
