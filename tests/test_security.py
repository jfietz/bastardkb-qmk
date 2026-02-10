import sys
import os
import unittest
import logging
from unittest.mock import MagicMock, patch
from pathlib import Path

# We need to mock dependencies before importing bastardkb_build_releases
# because it imports them at the top level.
# We'll use a setUpClass to handle this cleanly.

class TestSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock dependencies in sys.modules
        cls.modules_patcher = patch.dict(sys.modules, {
            "pygit2": MagicMock(),
            "rich": MagicMock(),
            "rich.console": MagicMock(),
            "rich.live": MagicMock(),
            "rich.panel": MagicMock(),
            "rich.progress": MagicMock(),
            "rich.text": MagicMock(),
        })
        cls.modules_patcher.start()

        # Add root to sys.path
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

        # Now import the module under test
        global bkb
        import bastardkb_build_releases as bkb

    @classmethod
    def tearDownClass(cls):
        cls.modules_patcher.stop()

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
        found = False
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                found = True
                break
        self.assertTrue(found, "git submodule update was not called")

    @patch('os.environ', {})
    @patch('os.makedirs')
    @patch('os.chmod')
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('os.path.expanduser')
    def test_secure_logging_setup(self, mock_expanduser, mock_handler, mock_chmod, mock_makedirs):
        # Setup mocks
        mock_expanduser.return_value = "/home/testuser"

        # Configure mock handler to avoid logging errors
        mock_handler.return_value.level = logging.NOTSET

        # Re-initialize Reporter to trigger __init__ logic
        bkb.Reporter(verbose=False)

        # Expected path: /home/testuser/.local/state/bastardkb-qmk
        expected_dir = os.path.join("/home/testuser", ".local", "state", "bastardkb-qmk")

        # Verify mkdirs called
        mock_makedirs.assert_called_with(expected_dir, exist_ok=True)

        # Verify chmod called with 0700 (448 in decimal)
        mock_chmod.assert_called_with(expected_dir, 0o700)

        # Verify handler created with correct path
        expected_log_file = os.path.join(expected_dir, "bastardkb_build_releases.py.log")
        mock_handler.assert_called()
        call_args = mock_handler.call_args
        self.assertEqual(call_args.kwargs['filename'], expected_log_file)

if __name__ == '__main__':
    unittest.main()
