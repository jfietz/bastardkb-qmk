import sys
import os
import unittest
import tempfile
import stat
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

import bastardkb_build_releases as bkb

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        self.executor = bkb.Executor(self.reporter, self.repository, dry_run=False, parallel=1)

    def test_git_submodule_update_failure_raises_error(self):
        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        self.repository.lookup_worktree.return_value = worktree

        # Mock _run to return failure for git submodule update
        self.executor._run = MagicMock()

        # Return a failure process
        failure_process = MagicMock()
        failure_process.returncode = 1
        self.executor._run.return_value = failure_process

        # We expect the code to exit or raise an error when submodule update fails.
        with self.assertRaises(SystemExit):
            self.executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called with git submodule update
        # We need to find the call that matches submodule update
        found = False
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                found = True
                break
        self.assertTrue(found, "git submodule update was not called")

    def test_secure_rotating_file_handler_maintains_permissions(self):
        with tempfile.TemporaryDirectory() as td:
            log_file = os.path.join(td, "test.log")

            # Start with a permissive umask
            old_umask = os.umask(0o022)
            try:
                # Create handler with small maxBytes to easily trigger rotation
                handler = bkb.SecureRotatingFileHandler(
                    filename=log_file,
                    maxBytes=100,
                    backupCount=2
                )

                # Check initial file permissions
                st_initial = os.stat(log_file)
                perms_initial = stat.S_IMODE(st_initial.st_mode)
                self.assertEqual(perms_initial, 0o600, f"Expected initial log to have 0o600, got {oct(perms_initial)}")

                # Write enough data to trigger rotation
                import logging
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg="A" * 150,
                    args=(),
                    exc_info=None
                )
                # Need a formatter to format the record
                handler.setFormatter(logging.Formatter('%(message)s'))
                handler.emit(record)

                # Emit a second record to actually trigger the rotation
                # (the first write might just fill it up to maxBytes)
                handler.emit(record)

                # Check rotated file permissions
                st_rotated = os.stat(log_file + ".1")
                perms_rotated = stat.S_IMODE(st_rotated.st_mode)
                self.assertEqual(perms_rotated, 0o600, f"Expected rotated log to have 0o600, got {oct(perms_rotated)}")

                # Check new active file permissions
                st_new = os.stat(log_file)
                perms_new = stat.S_IMODE(st_new.st_mode)
                self.assertEqual(perms_new, 0o600, f"Expected new active log to have 0o600, got {oct(perms_new)}")

            finally:
                os.umask(old_umask)
                if 'handler' in locals():
                    handler.close()

    @patch("bastardkb_build_releases.SecureRotatingFileHandler")
    def test_app_log_dir_permissions_are_enforced_on_existing_dir(self, mock_handler):
        # Configure the mock handler
        mock_handler.return_value.level = 0

        with tempfile.TemporaryDirectory() as td:
            # Pre-create the log directory with permissive permissions (e.g., 0o777)
            app_log_dir = os.path.join(td, "bastardkb-qmk")
            os.makedirs(app_log_dir)
            os.chmod(app_log_dir, 0o777)

            with patch.dict(os.environ, {"XDG_STATE_HOME": td}):
                # Initialize reporter
                reporter = bkb.Reporter(verbose=False)

                # Verify that permissions were restricted to 0o700
                st = os.stat(app_log_dir)
                perms = stat.S_IMODE(st.st_mode)
                self.assertEqual(perms, 0o700, f"Expected 0o700 permissions, got {oct(perms)}")

    def test_copy_assets_prevents_symlink_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)

            # Create a mock repository directory structure
            repo_path = td_path / "repo"
            via_dir = repo_path / "main" / "via"
            via_dir.mkdir(parents=True)

            # Create a dummy .via.json file
            via_file = via_dir / "test_keyboard.via.json"
            via_file.write_text("via config content")

            # Create an output directory
            out_dir = td_path / "output"
            out_dir.mkdir()

            # Create a sensitive target file outside the output directory
            sensitive_file = td_path / "sensitive.txt"
            sensitive_file.write_text("secret")

            # Create a symlink in the output directory pointing to the sensitive file
            dst = out_dir / "test_keyboard.via.json"
            os.symlink(sensitive_file, dst)

            # Execute copy_assets_to_output_dir
            bkb.copy_assets_to_output_dir(self.executor, self.reporter, out_dir, repo_path)

            # Assert sensitive file was NOT overwritten
            self.assertEqual(sensitive_file.read_text(), "secret")

            # Assert the destination is no longer a symlink and contains the copied content
            self.assertFalse(dst.is_symlink())
            self.assertEqual(dst.read_text(), "via config content")


if __name__ == '__main__':
    unittest.main()
