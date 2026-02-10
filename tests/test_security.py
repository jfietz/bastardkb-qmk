import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock pygit2 and rich before importing the module
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Setup rich mocks specifically
sys.modules["rich.panel"].Panel = MagicMock() # Ensure Panel is a class or callable

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestSecurity(unittest.TestCase):
    def setUp(self):
        # We need to re-mock Reporter because importing bkb might have used the mocked rich/pygit2
        # but bkb.Reporter uses them in __init__.
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

    @patch('bastardkb_build_releases.RotatingFileHandler')
    @patch('pathlib.Path.mkdir')
    def test_secure_logging_location(self, mock_mkdir, mock_handler):
        # Set up environment variables
        test_state_home = "/tmp/test_state"

        # Mock handler instance to have a .level attribute as logging might access it
        mock_handler.return_value.level = 0

        # We need to mock os.cpu_count if it's used in default args, but it's already evaluated at import time.

        with patch.dict(os.environ, {"XDG_STATE_HOME": test_state_home}):
            # Instantiate Reporter
            reporter = bkb.Reporter(verbose=False)

            # Verify mkdir was called with correct mode (0o700)
            found_secure_mkdir = False
            # Check all calls to mkdir
            for call in mock_mkdir.call_args_list:
                # call.kwargs is a dict
                kwargs = call.kwargs
                if kwargs.get('mode') == 0o700:
                    found_secure_mkdir = True
                    break

            self.assertTrue(found_secure_mkdir, "Secure directory creation (mode=0o700) not found")

            # Verify RotatingFileHandler was initialized with a file inside the secure directory
            expected_log_dir = Path(test_state_home) / "bastardkb-qmk"
            expected_log_file = expected_log_dir / "bastardkb_build_releases.py.log"

            self.assertTrue(mock_handler.called)
            args, kwargs = mock_handler.call_args
            # filename is the first arg or keyword arg 'filename'
            filename = kwargs.get('filename') or args[0]

            # Compare paths as strings
            self.assertEqual(str(filename), str(expected_log_file))

if __name__ == '__main__':
    unittest.main()
