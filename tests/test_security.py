import sys
import os
import unittest
import logging
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()

# Mock Panel as a class so isinstance checks work (consistent with test_ux.py)
mock_panel_module = MagicMock()
class MockPanel:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get("title", "")
mock_panel_module.Panel = MockPanel
sys.modules["rich.panel"] = mock_panel_module

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

class TestLoggingSecurity(unittest.TestCase):
    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("os.chmod")
    @patch("pathlib.Path.mkdir")
    @patch("os.getcwd")
    @patch("os.path.expanduser")
    @patch("os.environ", {})
    def test_log_location_is_secure(self, mock_expanduser, mock_getcwd, mock_mkdir, mock_chmod, mock_handler):
        # Setup
        mock_getcwd.return_value = "/unsafe/cwd"
        mock_expanduser.side_effect = lambda p: p.replace("~", "/home/user")

        # Configure mock handler to have a valid level so logging internals don't crash
        mock_handler.return_value.level = logging.NOTSET

        # Instantiate Reporter
        reporter = bkb.Reporter(verbose=False)

        # Check calls to RotatingFileHandler
        self.assertTrue(mock_handler.called)
        call_args = mock_handler.call_args[1] # kwargs
        filename = call_args.get('filename')

        # EXPECTED (Secure): /home/user/.local/state/bastardkb-qmk/bastardkb_build_releases.py.log
        expected_dir = "/home/user/.local/state/bastardkb-qmk"

        # Assert that the filename starts with the secure directory
        self.assertTrue(str(filename).startswith(expected_dir),
                        f"Log file {filename} should be in {expected_dir}")

        self.assertFalse(str(filename).startswith("/unsafe/cwd"),
                         "Log file should NOT be in CWD")

    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("pathlib.Path.mkdir")
    @patch("os.chmod")
    @patch("os.path.expanduser")
    @patch("os.environ", {})
    def test_secure_dir_creation(self, mock_expanduser, mock_chmod, mock_mkdir, mock_handler):
        mock_expanduser.side_effect = lambda p: p.replace("~", "/home/user")

        # Configure mock handler
        mock_handler.return_value.level = logging.NOTSET

        # Instantiate Reporter
        bkb.Reporter(verbose=False)

        expected_dir = "/home/user/.local/state/bastardkb-qmk"

        # Check that directory was created
        # We patch Path.mkdir because we call mkdir on a Path object
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)

        # Check that permissions were set to 0700
        # mock_chmod called with Path object
        self.assertTrue(mock_chmod.called)
        args, _ = mock_chmod.call_args
        self.assertEqual(str(args[0]), expected_dir)
        self.assertEqual(args[1], 0o700)

if __name__ == '__main__':
    unittest.main()
