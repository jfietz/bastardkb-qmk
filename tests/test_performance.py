import sys
import os
import unittest
from unittest.mock import MagicMock
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bastardkb_build_releases as bkb


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()
        self.repository = MagicMock()
        self.parallel = 4
        self.executor = bkb.Executor(
            self.reporter, self.repository, dry_run=False, parallel=self.parallel
        )

    def test_git_submodule_update_uses_jobs(self):
        """Verify that git submodule update uses the --jobs parameter for parallel execution."""
        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        self.repository.lookup_worktree.return_value = worktree

        # Mock _run to simulate successful git execution
        # We need to mock _run because it calls subprocess.run which we don't want to actually execute
        self.executor._run = MagicMock()
        success_process = MagicMock()
        success_process.returncode = 0
        self.executor._run.return_value = success_process

        # Run git_ensure_worktree
        self.executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called with git submodule update and --jobs
        # The arguments are passed as a tuple/list to _run
        found = False
        # Retrieve all calls to _run
        calls = self.executor._run.call_args_list

        for call in calls:
            # call.args[0] is the command list/tuple
            args = call.args[0]
            # Check if this is the submodule update command
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                # Check for --jobs argument
                if "--jobs" in args:
                    try:
                        jobs_index = args.index("--jobs")
                        jobs_val = args[jobs_index + 1]
                        if str(jobs_val) == str(self.parallel):
                            found = True
                    except IndexError:
                        pass
                break

        # We expect this to FAIL initially because the code doesn't use --jobs yet
        if not found:
            # Try to print debug info if possible (though captured stdout might hide it)
            pass

        self.assertTrue(
            found, f"git submodule update was not called with --jobs {self.parallel}."
        )


if __name__ == "__main__":
    unittest.main()
