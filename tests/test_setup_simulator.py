"""Protect existing installed artifacts during provider maintenance."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("setup_simulator", Path(__file__).resolve().parents[1] / "scripts/setup_simulator.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class InstallationTests(unittest.TestCase):
    def test_changed_same_version_preserves_active_installation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools, built = root / ".tools", root / "built"
            built.mkdir()
            (built / "terraform-provider-azuresim").write_bytes(b"new-provider")
            (built / "simctl").write_bytes(b"new-control")
            package = tools / "provider-mirror" / setup.SOURCE / setup.VERSION / "darwin_arm64"
            package.mkdir(parents=True)
            binary = package / f"terraform-provider-azuresim_v{setup.VERSION}"
            binary.write_bytes(b"installed-provider")
            (root / "private").mkdir()
            record = root / "private/SIMULATOR_SETUP.json"
            record.write_bytes(b"old-record")
            with patch.object(setup, "ROOT", root), self.assertRaisesRegex(ValueError, "checksum differs"):
                setup.install_built_tools(built, root / "simulator", tools,
                                          {"platform": "darwin_arm64", "terraform_version": "1.12.2"})
            self.assertEqual(binary.read_bytes(), b"installed-provider")
            self.assertEqual(record.read_bytes(), b"old-record")
            self.assertFalse((tools / "bin").exists())

    def test_new_version_keeps_previous_setup_and_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools, built = root / ".tools", root / "built"
            built.mkdir()
            (built / "terraform-provider-azuresim").write_bytes(b"new-provider")
            (built / "simctl").write_bytes(b"new-control")
            (tools / "bin").mkdir(parents=True)
            (tools / "bin/simctl").write_bytes(b"old-control")
            (root / "private").mkdir()
            old_record = json.dumps({"provider_version": "0.1.0"}).encode()
            (root / "private/SIMULATOR_SETUP.json").write_bytes(old_record)
            with patch.object(setup, "ROOT", root):
                setup.install_built_tools(built, root / "simulator", tools,
                                          {"platform": "darwin_arm64", "terraform_version": "1.12.2"})
            backups = list((root / "private/development/setup-history").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / "simctl").read_bytes(), b"old-control")
            self.assertEqual((backups[0] / "SIMULATOR_SETUP.json").read_bytes(), old_record)
            record = json.loads((root / "private/SIMULATOR_SETUP.json").read_text())
            self.assertEqual(record["provider_version"], setup.VERSION)
            self.assertTrue(record["simctl_sha256"])

    def test_missing_package_does_not_bypass_recorded_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tools, built = root / ".tools", root / "built"
            built.mkdir()
            (built / "terraform-provider-azuresim").write_bytes(b"changed-provider")
            (built / "simctl").write_bytes(b"changed-control")
            (root / "private").mkdir()
            record = root / "private/SIMULATOR_SETUP.json"
            original = json.dumps({"provider_source": setup.SOURCE, "provider_version": setup.VERSION,
                                   "platform": "darwin_arm64", "provider_sha256": "previous-checksum"}).encode()
            record.write_bytes(original)
            with patch.object(setup, "ROOT", root), self.assertRaisesRegex(ValueError, "different.*checksum"):
                setup.install_built_tools(built, root / "simulator", tools,
                                          {"platform": "darwin_arm64", "terraform_version": "1.12.2"})
            self.assertEqual(record.read_bytes(), original)
            self.assertFalse((tools / "bin").exists())


if __name__ == "__main__":
    unittest.main()
