import sys
import os
import unittest
import tempfile
import stat
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Mock Panel class specifically since it might be used with isinstance
    sys.modules["rich.panel"].Panel = MagicMock
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('bastardkb_build_releases.Console')
    def test_log_file_location_secure(self, mock_console, mock_handler):
        """Verify log file is created in XDG_STATE_HOME with 0700 permissions."""
        mock_handler.return_value.level = 0

        with tempfile.TemporaryDirectory() as temp_home:
            # We patch os.environ but we need to ensure XDG_STATE_HOME is set
            with patch.dict(os.environ, {"XDG_STATE_HOME": temp_home}):
                reporter = bkb.Reporter(verbose=False)

                # Check log directory
                expected_dir = Path(temp_home) / "bastardkb-qmk"
                self.assertTrue(expected_dir.exists(), f"Log directory {expected_dir} should exist")
                self.assertTrue(expected_dir.is_dir(), f"{expected_dir} should be a directory")

                # Check permissions
                mode = expected_dir.stat().st_mode
                permissions = stat.S_IMODE(mode)
                self.assertEqual(permissions, 0o700, f"Log directory permissions should be 0700 (got {oct(permissions)})")

                # Check log file path
                expected_log_file = expected_dir / "bastardkb_build_releases.py.log"
                args, kwargs = mock_handler.call_args
                filename = kwargs.get('filename') or (args[0] if args else None)
                self.assertEqual(Path(filename).resolve(), expected_log_file.resolve(), "Log file path mismatch")

if __name__ == '__main__':
    unittest.main()
