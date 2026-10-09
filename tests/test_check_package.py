"""Package map validation must detect drift, including with Python optimization."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_package


ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="mentor-package-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for relative in ("docs/objectives.json", "templates/PROGRESS.json"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def corrupt_progress(self, key, value):
        target = self.root / "templates/PROGRESS.json"
        data = json.loads(target.read_text())
        if key == "lesson":
            data["objectives"][0]["lesson"] = value
        else:
            data[key] = value
        target.write_text(json.dumps(data))

    def test_corrupt_template_lesson_is_detected(self):
        self.corrupt_progress("lesson", "09.2")
        with self.assertRaisesRegex(ValueError, "Progress lesson map drift"):
            check_package.check(self.root)

    def test_corrupt_template_exam_target_is_detected(self):
        self.corrupt_progress("exam_target", "Terraform Associate 003")
        with self.assertRaisesRegex(ValueError, "Progress exam target drift"):
            check_package.check(self.root)

    def test_corrupt_template_terraform_version_is_detected(self):
        self.corrupt_progress("exam_terraform_version", "1.5")
        with self.assertRaisesRegex(ValueError, "Progress Terraform version drift"):
            check_package.check(self.root)

    def test_optimized_python_still_detects_corrupt_mapping(self):
        self.corrupt_progress("lesson", "09.2")
        code = "from scripts.check_package import check; import sys; check(sys.argv[1])"
        result = subprocess.run([sys.executable, "-O", "-c", code, str(self.root)],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Progress lesson map drift", result.stderr)


if __name__ == "__main__":
    unittest.main()
