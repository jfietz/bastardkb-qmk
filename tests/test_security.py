import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import subprocess

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies that might be missing in CI/test environment
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

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

    @patch('shutil.which')
    def test_check_dependencies_failure(self, mock_which):
        # Simulate 'qmk' missing
        mock_which.side_effect = lambda x: x == 'git'

        # Capture stderr to avoid polluting test output
        from io import StringIO
        with patch('sys.stderr', new=StringIO()) as fake_err:
            with self.assertRaises(SystemExit) as cm:
                bkb.check_dependencies()
            self.assertEqual(cm.exception.code, 1)
            self.assertIn("Missing required dependencies: qmk", fake_err.getvalue())

    @patch('os.makedirs')
    @patch('os.chmod')
    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.path.exists', return_value=False)
    @patch.dict(os.environ, {'XDG_STATE_HOME': '/tmp/test_home'})
    def test_secure_logging_setup(self, mock_exists, mock_open, mock_rfh, mock_chmod, mock_makedirs):
        # Configure mock handler to have a valid level
        mock_rfh.return_value.level = 0

        # Initialize reporter (which triggers logging setup)
        # We mock Console/Live to avoid rich output issues
        with patch('bastardkb_build_releases.Console'), patch('bastardkb_build_releases.Live'):
             reporter = bkb.Reporter(verbose=False)

        # Verify log directory creation with secure permissions
        expected_log_dir = os.path.join('/tmp/test_home', 'bastardkb-qmk')
        mock_makedirs.assert_called_with(expected_log_dir, mode=0o700, exist_ok=True)

        # Verify log file permissions
        expected_log_file = os.path.join(expected_log_dir, 'bastardkb_build_releases.py.log')
        mock_chmod.assert_called_with(expected_log_file, 0o600)

if __name__ == '__main__':
    unittest.main()
