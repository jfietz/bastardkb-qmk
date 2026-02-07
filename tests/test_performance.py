import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
    def test_git_submodule_update_uses_jobs(self):
        """Verify that git submodule update uses the --jobs argument."""
        reporter = MagicMock()
        repository = MagicMock()
        parallel_count = 4
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=parallel_count)

        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        repository.lookup_worktree.return_value = worktree

        # Mock _run to avoid actual execution
        executor._run = MagicMock()
        executor._run.return_value.returncode = 0

        # Run the method
        executor.git_ensure_worktree("test_branch", update_submodules=True)

        # check if _run was called with correct arguments
        found = False
        for call in executor._run.call_args_list:
            args = call[0][0] # The argv tuple
            # We are looking for something like:
            # ('git', 'submodule', 'update', '--init', '--recursive', '--jobs', '4')
            # The order of flags might vary, but --jobs and 4 should be there.
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                if "--jobs" in args and str(parallel_count) in args:
                     # ensure 4 follows --jobs
                     idx = args.index("--jobs")
                     if idx + 1 < len(args) and args[idx+1] == str(parallel_count):
                         found = True
                         break

        self.assertTrue(found, f"git submodule update was not called with --jobs {parallel_count}")

if __name__ == '__main__':
    unittest.main()
