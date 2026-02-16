import unittest
import sys
import os
from unittest.mock import MagicMock, mock_open
from pathlib import Path

# Mock dependencies
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()
if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    sys.modules["rich.panel"].Panel = MagicMock
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogParsing(unittest.TestCase):
    def test_read_firmware_filename_success(self):
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_test_keyboard_via"

        log_content = "Some log line\nCopying bastardkb_test_keyboard_via.hex to qmk_firmware folder\nAnother line"

        log_file = MagicMock()
        m_open = mock_open(read_data=log_content)
        log_file.open = m_open

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(result, Path("bastardkb_test_keyboard_via.hex"))

    def test_read_firmware_filename_bin(self):
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_test_keyboard_via"

        log_content = "Copying bastardkb_test_keyboard_via.bin to qmk_firmware folder"

        log_file = MagicMock()
        log_file.open = mock_open(read_data=log_content)

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(result, Path("bastardkb_test_keyboard_via.bin"))

    def test_read_firmware_filename_not_found(self):
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_test_keyboard_via"

        log_content = "Some log line\nNo copying here\n"

        log_file = MagicMock()
        log_file.open = mock_open(read_data=log_content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

    def test_read_firmware_filename_mismatch(self):
        # This checks if the regex accidentally matches a different firmware (if we make it generic later)
        # For the original implementation, it shouldn't match.
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_test_keyboard_via"

        log_content = "Copying bastardkb_other_keyboard_via.hex to qmk_firmware folder"

        log_file = MagicMock()
        log_file.open = mock_open(read_data=log_content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

if __name__ == '__main__':
    unittest.main()
