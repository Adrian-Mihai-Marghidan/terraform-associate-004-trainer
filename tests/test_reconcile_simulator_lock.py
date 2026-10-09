"""Reconciliation never publishes an unverified or stale provider lock."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("reconcile_simulator_lock", SCRIPTS / "reconcile_simulator_lock.py")
sys.path.insert(0, str(SCRIPTS))
reconcile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile)
sys.path.remove(str(SCRIPTS))


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.lab = self.root / "lab"
        self.lab.mkdir()
        (self.lab / "main.tf").write_text("# A fixed configuration\n")
        self.lock = self.lab / reconcile.LOCK_NAME
        self.lock.write_bytes(b"original lock")
        (self.lab / "terraform.tfstate").write_bytes(b"preserved state")
        (self.lab / ".simulator").mkdir()
        (self.lab / ".simulator/infrastructure.json").write_bytes(b"preserved store")
        (self.root / "private").mkdir()
        self.setup = {"terraform_binary": "/verified/terraform", "platform": "linux_amd64",
                      "cli_config": str(self.root / ".tools/simulator.tfrc")}
        (self.root / "private/SIMULATOR_SETUP.json").write_text(json.dumps(self.setup))
        self.root_patch = patch.object(reconcile, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.startup_patch = patch.object(reconcile.check_simulator, "check")
        self.startup = self.startup_patch.start()
        self.addCleanup(self.startup_patch.stop)
        self.print_patch = patch.object(reconcile, "print", create=True)
        self.print_patch.start()
        self.addCleanup(self.print_patch.stop)
        self.commands = []

    def runner(self, command, cwd, env, **kwargs):
        self.assertTrue(self.startup.called)
        self.assertNotEqual(Path(cwd), self.lab)
        self.assertFalse((Path(cwd) / "terraform.tfstate").exists())
        self.assertFalse((Path(cwd) / ".simulator").exists())
        self.assertEqual(command[0], self.setup["terraform_binary"])
        self.assertEqual(env["TF_CLI_CONFIG_FILE"], self.setup["cli_config"])
        self.commands.append(command)
        if command[1:3] == ["providers", "lock"]:
            self.assertIn(f"-fs-mirror={self.root / '.tools/provider-mirror'}", command)
            self.assertIn("-platform=linux_amd64", command)
            self.assertEqual(command[-1], reconcile.SOURCE)
            (Path(cwd) / reconcile.LOCK_NAME).write_bytes(b"verified candidate")
        else:
            self.assertEqual(command[1:], ["init", "-lockfile=readonly", "-input=false", "-no-color"])
        return SimpleNamespace(returncode=0, stdout="verified", stderr="")

    def assert_runtime_preserved(self):
        self.assertEqual((self.lab / "terraform.tfstate").read_bytes(), b"preserved state")
        self.assertEqual((self.lab / ".simulator/infrastructure.json").read_bytes(), b"preserved store")
        self.assertEqual((self.lab / "main.tf").read_text(), "# A fixed configuration\n")

    def test_dry_run_retains_candidate_without_writing_lab(self):
        with patch.object(reconcile.subprocess, "run", side_effect=self.runner):
            record = reconcile.reconcile(self.lab)
        self.assertTrue(record["changed"])
        self.assertFalse(record["written"])
        self.assertEqual(self.lock.read_bytes(), b"original lock")
        self.assertEqual(len(self.commands), 2)
        self.assert_runtime_preserved()
        evidence = list((self.root / "private/development/lock-validation").glob("native-*"))
        self.assertEqual(len(evidence), 1)
        self.assertEqual(json.loads((evidence[0] / "summary.json").read_text())["result"], "passed")

    def test_write_preserves_original_and_runtime(self):
        with patch.object(reconcile.subprocess, "run", side_effect=self.runner):
            record = reconcile.reconcile(self.lab, write=True)
        self.assertTrue(record["written"])
        self.assertEqual(self.lock.read_bytes(), b"verified candidate")
        backups = list((self.root / "private/development/lock-validation").glob("native-*/original.terraform.lock.hcl"))
        self.assertEqual([file.read_bytes() for file in backups], [b"original lock"])
        self.assert_runtime_preserved()

    def test_failed_readonly_init_never_publishes(self):
        def failed(command, **kwargs):
            result = self.runner(command, **kwargs)
            if command[1] == "init":
                result.returncode = 1
            return result
        with patch.object(reconcile.subprocess, "run", side_effect=failed), self.assertRaisesRegex(RuntimeError, "init-readonly failed"):
            reconcile.reconcile(self.lab, write=True)
        self.assertEqual(self.lock.read_bytes(), b"original lock")
        self.assert_runtime_preserved()

    def test_readonly_init_cannot_change_the_verified_candidate(self):
        def changed(command, **kwargs):
            result = self.runner(command, **kwargs)
            if command[1] == "init":
                (Path(kwargs["cwd"]) / reconcile.LOCK_NAME).write_bytes(b"unexpected candidate")
            return result
        with patch.object(reconcile.subprocess, "run", side_effect=changed), self.assertRaisesRegex(RuntimeError, "Readonly"):
            reconcile.reconcile(self.lab, write=True)
        self.assertEqual(self.lock.read_bytes(), b"original lock")
        self.assert_runtime_preserved()

    def test_failed_lock_generation_never_initializes_or_publishes(self):
        def failed(command, **kwargs):
            result = self.runner(command, **kwargs)
            result.returncode = 1
            return result
        with patch.object(reconcile.subprocess, "run", side_effect=failed), self.assertRaisesRegex(RuntimeError, "providers-lock failed"):
            reconcile.reconcile(self.lab, write=True)
        self.assertEqual(len(self.commands), 1)
        self.assertEqual(self.lock.read_bytes(), b"original lock")
        self.assert_runtime_preserved()

    def test_symlinked_original_is_preserved_before_commands(self):
        target = self.lab / "actual-lock"
        self.lock.rename(target)
        self.lock.symlink_to(target)
        with patch.object(reconcile.subprocess, "run") as run, self.assertRaisesRegex(ValueError, "symlinked"):
            reconcile.reconcile(self.lab, write=True)
        run.assert_not_called()
        self.assertTrue(self.lock.is_symlink())
        self.assertEqual(target.read_bytes(), b"original lock")

    def test_concurrent_lock_change_is_preserved(self):
        def changed(command, **kwargs):
            result = self.runner(command, **kwargs)
            if command[1] == "init":
                self.lock.write_bytes(b"other writer")
            return result
        with patch.object(reconcile.subprocess, "run", side_effect=changed), self.assertRaisesRegex(ValueError, "lock changed"):
            reconcile.reconcile(self.lab, write=True)
        self.assertEqual(self.lock.read_bytes(), b"other writer")
        self.assert_runtime_preserved()

    def test_new_lock_creation_checks_for_concurrent_creation(self):
        self.lock.unlink()
        def changed(command, **kwargs):
            result = self.runner(command, **kwargs)
            if command[1] == "init":
                self.lock.write_bytes(b"other new lock")
            return result
        with patch.object(reconcile.subprocess, "run", side_effect=changed), self.assertRaisesRegex(ValueError, "lock changed"):
            reconcile.reconcile(self.lab, write=True)
        self.assertEqual(self.lock.read_bytes(), b"other new lock")

    def test_missing_lock_can_be_created_after_verification(self):
        self.lock.unlink()
        with patch.object(reconcile.subprocess, "run", side_effect=self.runner):
            record = reconcile.reconcile(self.lab, write=True)
        self.assertTrue(record["written"])
        self.assertEqual(self.lock.read_bytes(), b"verified candidate")
        self.assert_runtime_preserved()

    def test_startup_failure_runs_no_terraform_or_publication(self):
        self.startup.side_effect = ValueError("Source private/simulator-env.sh")
        with patch.object(reconcile.subprocess, "run") as run, self.assertRaisesRegex(ValueError, "Source"):
            reconcile.reconcile(self.lab, write=True)
        run.assert_not_called()
        self.assertEqual(self.lock.read_bytes(), b"original lock")


if __name__ == "__main__":
    unittest.main()
