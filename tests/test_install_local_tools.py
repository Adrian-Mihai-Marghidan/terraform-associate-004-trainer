"""Regression checks for preservation, offline setup, and interrupted downloads."""
import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts import install_local_tools as installer


class InterruptedResponse(io.BytesIO):
    def read(self, size=-1):
        if self.tell():
            raise OSError("connection interrupted")
        return super().read(3)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="mentor-installer-test-")
        self.addCleanup(self.directory.cleanup)
        self.tools = Path(self.directory.name) / ".tools"
        self.downloads = self.tools / "downloads"
        self.downloads.mkdir(parents=True)
        for name, value in (("TOOLS", self.tools), ("DOWNLOADS", self.downloads)):
            patch = mock.patch.object(installer, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def binary(self, relative):
        target = self.tools / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"existing fixture installation")
        return target

    @staticmethod
    def output(command, **kwargs):
        if command[1:] == ["version"]:
            result = f"go version {installer.GO_VERSION} darwin/arm64\n"
        elif command[1:] == ["env", "-json", "GOHOSTOS", "GOHOSTARCH"]:
            result = json.dumps({"GOHOSTOS": "darwin", "GOHOSTARCH": "arm64"})
        elif command[1:] == ["version", "-json"]:
            result = json.dumps({"terraform_version": installer.TERRAFORM_VERSION, "platform": "darwin_arm64"})
        else:
            raise AssertionError(f"Unexpected verification command: {command}")
        return subprocess.CompletedProcess(command, 0, stdout=result, stderr="")

    def test_existing_wrong_go_is_preserved_before_other_installation(self):
        binary = self.binary("go/bin/go")
        original = binary.read_bytes()
        with mock.patch.object(installer.platform, "system", return_value="Darwin"), \
                mock.patch.object(installer.platform, "machine", return_value="arm64"), \
                mock.patch.object(installer.subprocess, "run", return_value=subprocess.CompletedProcess(
                    [], 0, stdout="go version go1.20.0 darwin/arm64\n", stderr="")), \
                mock.patch.object(installer.urllib.request, "urlopen") as network:
            with self.assertRaisesRegex(SystemExit, "Go tool mismatch.*Preserved"):
                installer.main()
        self.assertEqual(binary.read_bytes(), original)
        self.assertFalse((self.tools / "terraform").exists())
        network.assert_not_called()

    def test_existing_go_wrong_host_platform_is_preserved(self):
        binary = self.binary("go/bin/go")
        responses = [subprocess.CompletedProcess([], 0, stdout=f"go version {installer.GO_VERSION} darwin/arm64\n"),
                     subprocess.CompletedProcess([], 0, stdout='{"GOHOSTOS":"linux","GOHOSTARCH":"amd64"}')]
        with mock.patch.object(installer.subprocess, "run", side_effect=responses):
            with self.assertRaisesRegex(SystemExit, "Go host mismatch.*Preserved"):
                installer.verify_go(binary, "darwin", "arm64")
        self.assertEqual(binary.read_bytes(), b"existing fixture installation")

    def test_correct_existing_tools_work_offline_without_rewriting(self):
        go = self.binary("go/bin/go")
        terraform = self.binary("terraform/terraform")
        before = [(path.read_bytes(), path.stat().st_mtime_ns) for path in (go, terraform)]
        with mock.patch.object(installer.platform, "system", return_value="Darwin"), \
                mock.patch.object(installer.platform, "machine", return_value="arm64"), \
                mock.patch.object(installer.subprocess, "run", side_effect=self.output) as commands, \
                mock.patch.object(installer.urllib.request, "urlopen") as network, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            installer.main()
        self.assertIn("Verified Terraform", output.getvalue())
        self.assertEqual(before, [(path.read_bytes(), path.stat().st_mtime_ns) for path in (go, terraform)])
        self.assertTrue(any(call.args[0][1:] == ["env", "-json", "GOHOSTOS", "GOHOSTARCH"]
                            for call in commands.call_args_list))
        network.assert_not_called()

    def test_go_verification_disables_toolchain_downloads_and_global_goroot(self):
        with mock.patch.dict(installer.os.environ, {"GOROOT": "/global/go", "GOTOOLCHAIN": "auto"}), \
                mock.patch.object(installer.subprocess, "run", side_effect=self.output) as commands:
            installer.verify_go(Path("fixture/go"), "darwin", "arm64")
        for call in commands.call_args_list:
            self.assertEqual(call.kwargs["env"]["GOTOOLCHAIN"], "local")
            self.assertNotIn("GOROOT", call.kwargs["env"])

    def test_interrupted_download_does_not_cache_partial_file(self):
        target = self.downloads / "archive.zip"
        with mock.patch.object(installer.urllib.request, "urlopen", return_value=InterruptedResponse(b"complete")):
            with self.assertRaisesRegex(OSError, "connection interrupted"):
                installer.download("https://fixture.invalid/archive.zip", target)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.downloads.iterdir()), [])
        with mock.patch.object(installer.urllib.request, "urlopen", return_value=io.BytesIO(b"complete")):
            installer.download("https://fixture.invalid/archive.zip", target)
        self.assertEqual(target.read_bytes(), b"complete")

    def test_interrupted_atomic_copy_preserves_existing_file(self):
        target = self.downloads / "metadata.json"
        target.write_bytes(b"original complete metadata")
        with self.assertRaisesRegex(OSError, "connection interrupted"):
            installer.atomic_copy(InterruptedResponse(b"replacement"), target)
        self.assertEqual(target.read_bytes(), b"original complete metadata")
        self.assertEqual(list(self.downloads.iterdir()), [target])

    def test_verified_legacy_archive_is_reused_without_network(self):
        legacy = self.downloads / "terraform.zip"
        legacy.write_bytes(b"verified archive fixture")
        expected = hashlib.sha256(legacy.read_bytes()).hexdigest()
        with mock.patch.object(installer.urllib.request, "urlopen") as network:
            archive = installer.archive_with_legacy_cache("https://fixture.invalid/archive.zip",
                                                         "terraform_1.12.2_darwin_arm64.zip", "terraform.zip", expected)
        self.assertEqual(archive.read_bytes(), legacy.read_bytes())
        network.assert_not_called()

    def test_other_platform_legacy_archive_is_preserved_while_new_cache_downloads(self):
        legacy = self.downloads / "go.tar.gz"
        legacy.write_bytes(b"different platform fixture")
        expected = hashlib.sha256(b"desired platform fixture").hexdigest()
        with mock.patch.object(installer.urllib.request, "urlopen", return_value=io.BytesIO(b"desired platform fixture")):
            archive = installer.archive_with_legacy_cache("https://fixture.invalid/go.tar.gz",
                                                         "go1.27.2.darwin-arm64.tar.gz", "go.tar.gz", expected)
        self.assertEqual(archive.read_bytes(), b"desired platform fixture")
        self.assertEqual(legacy.read_bytes(), b"different platform fixture")

    def test_cached_manifest_and_go_metadata_are_usable_offline(self):
        filename = "terraform_1.12.2_darwin_arm64.zip"
        (self.downloads / "terraform_SHA256SUMS").write_text("a" * 64 + "  " + filename + "\n")
        entry = {"version": installer.GO_VERSION, "os": "darwin", "arch": "arm64", "kind": "archive",
                 "filename": "go1.27.2.darwin-arm64.tar.gz", "sha256": "b" * 64}
        (self.downloads / "go-releases.json").write_text(json.dumps([{"files": [entry]}]))
        with mock.patch.object(installer.urllib.request, "urlopen") as network:
            self.assertEqual(installer.terraform_checksum(filename), "a" * 64)
            self.assertEqual(installer.go_release("darwin", "arm64"), entry)
        self.assertTrue((self.downloads / "terraform_1.12.2_SHA256SUMS").is_file())
        self.assertTrue((self.downloads / "terraform_SHA256SUMS").is_file())
        network.assert_not_called()

    def test_unexpected_staged_terraform_version_is_not_published(self):
        archive = self.downloads / "terraform.zip"
        with zipfile.ZipFile(archive, "w") as contents:
            contents.writestr("terraform", b"fixture binary")
        filename = "terraform_1.12.2_darwin_arm64.zip"
        (self.downloads / "terraform_SHA256SUMS").write_text(installer.checksum(archive) + "  " + filename + "\n")
        wrong = subprocess.CompletedProcess([], 0, stdout='{"terraform_version":"1.5.7","platform":"darwin_arm64"}')
        with mock.patch.object(installer.subprocess, "run", return_value=wrong), \
                mock.patch.object(installer.urllib.request, "urlopen") as network:
            with self.assertRaisesRegex(SystemExit, "Terraform tool mismatch"):
                installer.install_terraform("darwin", "arm64")
        self.assertFalse((self.tools / "terraform/terraform").exists())
        self.assertEqual(list(self.tools.glob(".terraform-install-*")), [])
        self.assertTrue(archive.is_file())
        network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
