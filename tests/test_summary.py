import sys
import unittest
from unittest.mock import MagicMock, call

# Mock external dependencies in sys.modules before importing the module under test
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()
sys.modules["rich.table"] = MagicMock()

# Now import the module
import bastardkb_build_releases as bkb

class TestSummary(unittest.TestCase):
    def setUp(self):
        self.reporter = bkb.Reporter(verbose=False)
        self.reporter.console = MagicMock()

    def test_print_summary(self):
        # We need to add the method to the class dynamically or verify it exists after modification
        # Since we are writing the test before the code, we assume the method will be added.

        # This test expects the method to exist, so it will fail if run before the code change.
        # But for TDD, I'll write the test assuming the signature I want.

        results = [
            ("firmware1", "success", None),
            ("firmware2", "failure", "/path/to/log"),
            ("firmware3", "warning", "/path/to/log"),
        ]

        # If print_summary is not yet implemented, this test will fail with AttributeError
        self.reporter.print_summary(results)

        # Verify a Table was created and printed
        self.reporter.console.print.assert_called()
        # Check that rich.table.Table was instantiated
        # (This is hard to check exactly without more complex mocking, but we can check if console.print was called with something)

    def test_build_collects_results(self):
        # Mock executor and other dependencies for build()
        executor = MagicMock()
        reporter = MagicMock()
        reporter.console = MagicMock()

        firmware1 = MagicMock()
        firmware1.__str__.return_value = "firmware1"
        firmware2 = MagicMock()
        firmware2.__str__.return_value = "firmware2"

        # We need to construct a proper FirmwareList or mock it to behave like one
        # bkb.FirmwareList is available
        firmware_list = bkb.FirmwareList(branch="branch1", configurations=[firmware1, firmware2])
        firmwares = [firmware_list]

        on_compiled = MagicMock()

        # Mock executor.qmk_compile return values
        # Success
        proc1 = MagicMock()
        proc1.returncode = 0
        proc1.log_file = "log1"

        # Failure
        proc2 = MagicMock()
        proc2.returncode = 1
        proc2.log_file = "log2"

        executor.qmk_compile.side_effect = [proc1, proc2]

        # Mock read_firmware_filename_from_logs to succeed for the first one
        # We need to patch the function in the module
        original_read_logs = bkb.read_firmware_filename_from_logs
        bkb.read_firmware_filename_from_logs = MagicMock(return_value="firmware1.hex")

        try:
            bkb.build(executor, reporter, firmwares, on_compiled)

            # Verify print_summary was called
            self.assertTrue(reporter.print_summary.called)

            # Verify the arguments passed to print_summary
            # Expected: [("firmware1", "success", ...), ("firmware2", "failure", ...)]
            # Note: The actual implementation of build will determine the structure of results.
            # I'll decide on the structure now: List[Tuple[Firmware, str, Optional[Path]]]
            # str status: "success", "failure", "warning"

            call_args = reporter.print_summary.call_args[0][0]
            self.assertEqual(len(call_args), 2)
            self.assertEqual(call_args[0][0], firmware1)
            self.assertEqual(call_args[0][1], "success")
            self.assertEqual(call_args[1][0], firmware2)
            self.assertEqual(call_args[1][1], "failure")

        finally:
            bkb.read_firmware_filename_from_logs = original_read_logs

if __name__ == '__main__':
    unittest.main()
