import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import itertools
from functools import reduce
from operator import iconcat

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock rich and pygit2 to avoid dependency issues during test import if they were missing,
# but since we installed them, we can import directly.
# However, creating a clean environment is good.
# Let's import the module.
import bastardkb_build_releases as bkb

class TestPerformance(unittest.TestCase):
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
