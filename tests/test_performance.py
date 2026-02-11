import unittest
import sys
import os
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile

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
            for k, v in kwargs.items():
                setattr(self, k, v)

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

    def test_read_firmware_filename_from_logs_string_parsing(self):
        # Setup
        firmware = MagicMock()
        # Mock output_filename property
        type(firmware).output_filename = PropertyMock(return_value="bastardkb_skeletyl_default")

        log_content = """
Some random log line
Copying bastardkb_skeletyl_default.hex to qmk_firmware folder
Some other log line
"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
            tmp.write(log_content)
            tmp_path = Path(tmp.name)

        try:
            # Test existing implementation (regex)
            result = bkb.read_firmware_filename_from_logs(firmware, tmp_path)
            self.assertEqual(result, Path("bastardkb_skeletyl_default.hex"))
        finally:
            os.unlink(tmp_path)

    def test_total_firmware_count_sum(self):
        # Verify the sum logic works as intended (just validating Python's sum)
        f1 = MagicMock()
        f1.configurations = [1, 2, 3] # length 3
        f2 = MagicMock()
        f2.configurations = [1, 2] # length 2

        firmwares = [f1, f2]

        # Proposed implementation: sum
        proposed_result = sum(len(f.configurations) for f in firmwares)
        self.assertEqual(proposed_result, 5)

    def test_qmk_compile_argv(self):
        # Mock Executor dependencies
        reporter = MagicMock()
        repository = MagicMock()
        executor = bkb.Executor(reporter, repository, dry_run=False, parallel=4)

        firmware = MagicMock()
        firmware.keyboard = "test/kb"
        firmware.keymap = "default"
        # Mock output_filename property
        type(firmware).output_filename = PropertyMock(return_value="test_kb_default")
        firmware.env_vars = ("VAR1=val1", "VAR2=val2")

        # Mock _run to inspect argv
        executor._run = MagicMock()
        # Mock return value of _run (CompletedProcess)
        executor._run.return_value = MagicMock(returncode=0)

        # Mock worktree
        worktree = MagicMock()
        worktree.path = Path("/tmp/wt")

        executor.qmk_compile(firmware, worktree)

        # Check args
        args, kwargs = executor._run.call_args
        argv = args[0]

        # Check if environment variables are correctly flattened
        # Expected sequence: ... "-e", "VAR1=val1", "-e", "VAR2=val2" ...

        # Find index of VAR1=val1
        try:
            idx1 = argv.index("VAR1=val1")
            self.assertEqual(argv[idx1-1], "-e", "Flag -e missing before VAR1")

            idx2 = argv.index("VAR2=val2")
            self.assertEqual(argv[idx2-1], "-e", "Flag -e missing before VAR2")

        except ValueError:
            self.fail(f"Environment variables not found in argv: {argv}")

if __name__ == '__main__':
    unittest.main()
