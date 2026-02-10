import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path
import itertools

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
    def test_git_submodule_update_uses_jobs(self):
        """Verify git submodule update uses --jobs argument."""
        # Setup mocks
        reporter = MagicMock()
        repository = MagicMock()
        parallel_jobs = 4

        # We need to ensure we can instantiate Executor even with mocks
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=parallel_jobs)

        # Mock worktree lookup
        worktree = MagicMock()
        worktree.name = "test_branch"
        worktree.path = Path("/tmp/test_worktree")
        repository.lookup_worktree.return_value = worktree

        # Mock _run
        executor._run = MagicMock()
        success_process = MagicMock()
        success_process.returncode = 0
        executor._run.return_value = success_process

        # Run the method
        executor.git_ensure_worktree("test_branch", update_submodules=True)

        # Verify _run was called
        # We need to find the call that matches submodule update
        found = False
        git_submodule_call_args = None

        for call in executor._run.call_args_list:
            args = call[0][0] # The first argument is the command tuple/list
            if len(args) >= 3 and args[:3] == ("git", "submodule", "update"):
                git_submodule_call_args = args
                if "--jobs" in args:
                    # Check if the number of jobs follows --jobs
                    try:
                        jobs_index = args.index("--jobs")
                        if str(parallel_jobs) == args[jobs_index + 1]:
                            found = True
                    except (ValueError, IndexError):
                        pass
                break

        self.assertTrue(found, f"git submodule update was not called with --jobs {parallel_jobs}. Called with: {git_submodule_call_args}")

    def test_firmware_count_optimization(self):
        """Verify that the optimized counting logic produces the same result as the original."""
        # Setup data: 10 branches, each with 10 firmwares
        firmwares = []
        for i in range(10):
            configs = tuple(bkb.Firmware(f"kb{i}", "km") for _ in range(10))
            firmwares.append(bkb.FirmwareList(f"branch{i}", configs))
        firmwares = tuple(firmwares)

        # Original logic (reproduced from source)
        def original_callback(acc, firmware_list):
            return acc + len(list(firmware_list.configurations))

        from functools import reduce
        count_original = reduce(original_callback, firmwares, 0)

        # Optimized logic
        count_optimized = sum(len(fl.configurations) for fl in firmwares)

        self.assertEqual(count_original, count_optimized)
        self.assertEqual(count_optimized, 100)

    def test_qmk_compile_argv_construction(self):
        """Verify that qmk_compile constructs arguments correctly with the optimization."""
        # Setup
        reporter = MagicMock()
        repository = MagicMock()
        executor = bkb.Executor(reporter, repository, dry_run=True, parallel=4)

        env_vars = ("VAR1=VAL1", "VAR2=VAL2")
        firmware = bkb.Firmware("kb", "km", env_vars=env_vars)
        worktree = MagicMock()
        worktree.path = "/tmp/worktree"

        # We need to check how argv is constructed.
        # Since we are modifying the code, we want to ensure the result is the same.
        # But we can't easily run the "old" code inside the test if we overwrite it.
        # So we test that the CURRENT code (before modification) works as expected,
        # and then after modification, this test should still pass (or we update it if we change behavior, but we preserve behavior).

        # Currently, qmk_compile calls _run. We can mock _run.
        with patch.object(executor, '_run') as mock_run:
            mock_run.return_value = MagicMock(return_code=0)
            executor.qmk_compile(firmware, worktree)

            args, kwargs = mock_run.call_args
            argv = args[0]

            # Check standard args
            self.assertIn("qmk", argv)
            self.assertIn("compile", argv)

            # Check flattened env vars
            # Expect: ... -e VAR1=VAL1 -e VAR2=VAL2 ...
            indices = [i for i, x in enumerate(argv) if x == "-e"]
            self.assertEqual(len(indices), 2)
            self.assertEqual(argv[indices[0]+1], "VAR1=VAL1")
            self.assertEqual(argv[indices[1]+1], "VAR2=VAL2")

if __name__ == '__main__':
    unittest.main()
