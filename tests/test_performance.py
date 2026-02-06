import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        # Set parallel to a known value, e.g. 4
        self.parallel = 4
        self.executor = bkb.Executor(self.reporter, self.repository, dry_run=False, parallel=self.parallel)

    def test_git_submodule_update_uses_jobs(self):
        """Verify that git submodule update uses the --jobs argument."""
        # Mock worktree
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        self.repository.lookup_worktree.return_value = worktree

        # Mock _run
        self.executor._run = MagicMock()
        self.executor._run.return_value.returncode = 0

        # Run git_ensure_worktree
        self.executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Check arguments passed to _run
        found_jobs = False
        found_call = None
        for call in self.executor._run.call_args_list:
            args = call[0][0]
            # args is a tuple of strings
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                found_call = args
                if "--jobs" in args and str(self.parallel) in args:
                    found_jobs = True
                    break

        self.assertTrue(found_jobs, f"git submodule update was not called with --jobs {self.parallel}. Called with: {found_call}")

if __name__ == '__main__':
    unittest.main()
