import unittest
import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Ensure dependencies are mocked before importing the module
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    # Use a simpler mock for Panel to avoid initialization issues if possible,
    # though strict Panel tests might still fail elsewhere.
    # For this test file, we don't use Panel, so basic MagicMock is fine.
    sys.modules["rich.panel"].Panel = MagicMock
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestPerformanceImprovements(unittest.TestCase):
    def setUp(self):
        self.firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
        self.log_file = Path("test_log_perf.txt")

    def tearDown(self):
        if self.log_file.exists():
            self.log_file.unlink()

    def test_read_firmware_filename_valid(self):
        """Verify correct filename extraction with new regex logic."""
        filename = "bastardkb_skeletyl_v2_elitec_default.hex"
        # Content mimics real log
        content = f"Some preable\nCopying {filename} to qmk_firmware folder\nPostamble"

        with self.log_file.open("w") as f:
            f.write(content)

        result = bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)
        self.assertEqual(str(result), filename)

    def test_read_firmware_filename_invalid_prefix(self):
        """Verify mismatching filename prefix is ignored."""
        wrong_filename = "bastardkb_other_board.hex"
        content = f"Copying {wrong_filename} to qmk_firmware folder"

        with self.log_file.open("w") as f:
            f.write(content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)

    def test_read_firmware_filename_invalid_extension(self):
        """Verify invalid extension (uppercase) is rejected."""
        filename = "bastardkb_skeletyl_v2_elitec_default.EXE"
        content = f"Copying {filename} to qmk_firmware folder"

        with self.log_file.open("w") as f:
            f.write(content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)

    def test_read_firmware_filename_weird_extension(self):
        """Verify weird but valid extension (all digits)."""
        filename = "bastardkb_skeletyl_v2_elitec_default.123"
        content = f"Copying {filename} to qmk_firmware folder"

        with self.log_file.open("w") as f:
            f.write(content)

        result = bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)
        self.assertEqual(str(result), filename)

    def test_read_firmware_filename_mixed_extension(self):
         """Verify mixed digits and letters (v1)."""
         # "v1" -> islower() = True.
         filename = "bastardkb_skeletyl_v2_elitec_default.v1"
         content = f"Copying {filename} to qmk_firmware folder"

         with self.log_file.open("w") as f:
             f.write(content)

         result = bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)
         self.assertEqual(str(result), filename)

if __name__ == '__main__':
    unittest.main()
