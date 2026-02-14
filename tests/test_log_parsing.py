import unittest
import sys
import os
from unittest.mock import MagicMock, patch, mock_open
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
            for key, value in kwargs.items():
                setattr(self, key, value)
    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogParsing(unittest.TestCase):
    def test_read_firmware_filename_from_logs_success(self):
        """Verify read_firmware_filename_from_logs extracts correct filename."""
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_skeletyl_default"

        log_content = "Compiling...\nCopying bastardkb_skeletyl_default.hex to qmk_firmware folder\nDone."
        log_file = MagicMock()

        m = mock_open(read_data=log_content)
        log_file.open.side_effect = m

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(result, Path("bastardkb_skeletyl_default.hex"))

    def test_read_firmware_filename_from_logs_not_found(self):
        """Verify read_firmware_filename_from_logs raises FileNotFoundError if not found."""
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_skeletyl_default"

        log_content = "Compiling...\nNo copy message here.\nDone."
        log_file = MagicMock()

        m = mock_open(read_data=log_content)
        log_file.open.side_effect = m

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

    def test_read_firmware_filename_from_logs_mismatch(self):
        """Verify read_firmware_filename_from_logs ignores mismatching filenames."""
        # This test ensures we don't accidentally pick up a wrong file if the regex is too broad
        # and we remove the filename check.
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_skeletyl_default"

        # Suppose log has a weird entry that matches the pattern but for a different file
        # (Unlikely in real logs but good for robustness checking)
        log_content = "Copying bastardkb_other_keyboard.hex to qmk_firmware folder\n"
        log_file = MagicMock()

        m = mock_open(read_data=log_content)
        log_file.open.side_effect = m

        # Should raise FileNotFoundError because the found file doesn't match the expected firmware
        # With the current implementation (regex with re.escape(firmware.output_filename)), it won't match at all.
        # With the new implementation, it will match the regex but fail the check.
        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

if __name__ == '__main__':
    unittest.main()
