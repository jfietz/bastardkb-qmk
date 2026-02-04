import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock dependencies before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# We need to setup specific mocks for things that are imported directly or used in type hints/inheritance if necessary.
# In this case, since we mock the modules, 'from x import y' will get attributes from the mock.

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

    @patch("bastardkb_build_releases.RotatingFileHandler")
    @patch("pathlib.Path.chmod")
    @patch("pathlib.Path.mkdir")
    @patch.dict(os.environ, {"XDG_STATE_HOME": "/tmp/secure_logs"}, clear=True)
    def test_secure_logging_directory(self, mock_mkdir, mock_chmod, mock_rfh):
        # Setup mock for RotatingFileHandler to return a valid-looking handler mock
        # or just ensure it is accepted by logging.addHandler if real logging is used.
        # However, we are patching RotatingFileHandler class, so the instance returned is a MagicMock.
        # Real logging.Logger.addHandler might require an instance of logging.Handler.
        # Let's mock logging.getLogger as well to avoid side effects on root logger.

        with patch("bastardkb_build_releases.logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            reporter = bkb.Reporter(verbose=False)

            # Verify mkdir called
            self.assertTrue(mock_mkdir.called)

            # Verify chmod called with 0o700
            mock_chmod.assert_called_with(0o700)

            # Verify RotatingFileHandler called with correct path
            args, kwargs = mock_rfh.call_args
            filename = kwargs.get('filename') if 'filename' in kwargs else args[0]
            self.assertIn("/tmp/secure_logs/bastardkb-qmk", filename)

if __name__ == '__main__':
    unittest.main()
