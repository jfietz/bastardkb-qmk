import unittest
import sys
import os
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Mock Panel class specifically since it might be used with isinstance
    class MockPanel(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__()
            if args:
                self.renderable = args[0]
            for key, value in kwargs.items():
                setattr(self, key, value)

    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

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


    def test_qmk_compile_incremental(self):
        """Verify qmk compile is called without --clean flag for incremental builds."""
        # Setup mocks
        reporter = MagicMock()
        repository = MagicMock()
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=1)

        # Mock _run
        executor._run = MagicMock()
        executor._run.return_value = MagicMock(returncode=0)

        # Mock Firmware and Worktree
        firmware = MagicMock()
        firmware.keyboard = "test_kb"
        firmware.keymap = "test_km"
        firmware.output_filename = "test_output"
        firmware.env_vars = []

        worktree = MagicMock()
        worktree.path = Path("/tmp/test_worktree")

        # Run the method
        executor.qmk_compile(firmware, worktree)

        # Verify arguments passed to _run
        self.assertTrue(executor._run.called)
        args = executor._run.call_args[0][0]

        # Check that --clean is NOT present
        self.assertNotIn("--clean", args, "qmk compile should not use --clean flag to allow incremental builds")

    def test_read_firmware_filename_from_logs_optimization(self):
        """Verify log parsing optimization works correctly."""
        firmware = MagicMock()
        firmware.output_filename = "test_kb_via"

        # Mock log file
        log_file = MagicMock()

        # Case 1: Standard log with "Copying" prefix
        log_content = [
            "Compiling...\n",
            "Linking...\n",
            f"Copying {firmware.output_filename}.hex to qmk_firmware folder\n",
            "Done.\n"
        ]

        # Use a context manager mock for open()
        file_handle = MagicMock()
        file_handle.__enter__.return_value = log_content
        file_handle.__exit__.return_value = None
        log_file.open.return_value = file_handle

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(result, Path(f"{firmware.output_filename}.hex"))

        # Case 2: Log where the regex would match (if compiled differently) but startswith fails?
        # Since the regex is anchored to "Copying", startswith is safe.
        # We just verify it doesn't crash on other lines.

if __name__ == '__main__':
    unittest.main()
