"""Bootstrap respects each learner's timezone and preserves existing evidence."""
import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.bootstrap_progress import RECORDS, bootstrap


ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="mentor-bootstrap-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        shutil.copytree(ROOT / "templates", self.root / "templates")

    def bootstrap(self, timezone=None):
        with contextlib.redirect_stdout(io.StringIO()):
            bootstrap(self.root, timezone=timezone)

    def existing_progress(self, content):
        private = self.root / "private"
        private.mkdir()
        (private / "PROGRESS.json").write_bytes(content)
        return private

    def test_fresh_setup_uses_explicit_timezone(self):
        self.bootstrap("America/New_York")
        private = self.root / "private"
        progress = json.loads((private / "PROGRESS.json").read_text())
        self.assertEqual(progress["timezone"], "America/New_York")
        self.assertIn("Timezone: America/New_York.", (private / "SESSION_HANDOFF.md").read_text())
        template = json.loads((self.root / "templates/PROGRESS.json").read_text())
        self.assertEqual(progress["objectives"], template["objectives"])
        self.assertEqual(template["timezone"], "Europe/Bucharest")

    def test_default_setup_retains_template_bytes_and_bucharest(self):
        self.bootstrap()
        for name in RECORDS:
            self.assertEqual((self.root / "private" / name).read_bytes(),
                             (self.root / "templates" / name).read_bytes())

    def test_existing_timezone_creates_matching_handoff_without_rewriting_records(self):
        progress_bytes = b'{"timezone":"Asia/Tokyo","custom_evidence":["preserve me"]}\n'
        private = self.existing_progress(progress_bytes)
        reviews_bytes = b'{"reviews":["learner evidence"]}\n'
        (private / "REVIEWS.json").write_bytes(reviews_bytes)
        self.bootstrap()
        self.assertEqual((private / "PROGRESS.json").read_bytes(), progress_bytes)
        self.assertEqual((private / "REVIEWS.json").read_bytes(), reviews_bytes)
        self.assertIn("Timezone: Asia/Tokyo.", (private / "SESSION_HANDOFF.md").read_text())
        # Repeating setup, even with an explicit matching preference, is lossless.
        before = {name: (private / name).read_bytes() for name in RECORDS}
        self.bootstrap("Asia/Tokyo")
        self.assertEqual({name: (private / name).read_bytes() for name in RECORDS}, before)

    def test_invalid_requested_timezone_creates_no_private_files(self):
        with self.assertRaisesRegex(ValueError, "Invalid IANA timezone"):
            self.bootstrap("Not/A_Timezone")
        self.assertFalse((self.root / "private").exists())

    def test_different_explicit_timezone_fails_before_writes(self):
        progress_bytes = b'{"timezone":"Europe/Bucharest","evidence":["keep"]}\n'
        private = self.existing_progress(progress_bytes)
        with self.assertRaisesRegex(ValueError, "Change the learner's timezone separately"):
            self.bootstrap("UTC")
        self.assertEqual(list(private.iterdir()), [private / "PROGRESS.json"])
        self.assertEqual((private / "PROGRESS.json").read_bytes(), progress_bytes)

    def test_malformed_existing_progress_is_preserved_without_creating_records(self):
        for content, diagnostic in (
            (b'\xff', "not valid UTF-8"),
            (b'{"timezone":', "Invalid progress JSON"),
            (b'null', "must be a JSON object"),
            (b'{"timezone":null}', "Invalid timezone"),
            (b'{"timezone":"Not/A_Timezone"}', "Invalid IANA timezone"),
        ):
            with self.subTest(content=content):
                private = self.root / "private"
                private.mkdir(exist_ok=True)
                (private / "PROGRESS.json").write_bytes(content)
                with self.assertRaisesRegex(ValueError, diagnostic):
                    self.bootstrap()
                self.assertEqual(list(private.iterdir()), [private / "PROGRESS.json"])
                self.assertEqual((private / "PROGRESS.json").read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
