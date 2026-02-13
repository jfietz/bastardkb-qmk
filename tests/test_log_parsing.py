import unittest
import sys
import os
import re
from unittest.mock import MagicMock, mock_open, patch
from pathlib import Path

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()

    class MockPanel(MagicMock):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.title = kwargs.get('title', '')

    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogParsing(unittest.TestCase):
    def test_read_firmware_filename_success(self):
        """Verify extracting filename from valid log content."""
        firmware = MagicMock()
        # The expected output filename base
        firmware.output_filename = "bastardkb_skeletyl_v2_elitec_default"

        # Log content containing the success message
        log_content = """
QMK Firmware 0.16.9
Compiling: bastardkb/skeletyl/v2/elitec:default
Linking: .build/bastardkb_skeletyl_v2_elitec_default.elf
Creating load file for flashing: .build/bastardkb_skeletyl_v2_elitec_default.hex
Copying bastardkb_skeletyl_v2_elitec_default.hex to qmk_firmware folder
"""
        log_file = MagicMock(spec=Path)

        # Mock the open context manager
        with patch.object(log_file, "open", mock_open(read_data=log_content)):
            result = bkb.read_firmware_filename_from_logs(firmware, log_file)

        self.assertEqual(result, Path("bastardkb_skeletyl_v2_elitec_default.hex"))

    def test_read_firmware_filename_failure(self):
        """Verify FileNotFoundError is raised when pattern is not found."""
        firmware = MagicMock()
        firmware.output_filename = "bastardkb_skeletyl_v2_elitec_default"

        log_content = """
QMK Firmware 0.16.9
Compiling: bastardkb/skeletyl/v2/elitec:default
Error: compilation failed
"""
        log_file = MagicMock(spec=Path)

        with patch.object(log_file, "open", mock_open(read_data=log_content)):
            with self.assertRaises(FileNotFoundError):
                bkb.read_firmware_filename_from_logs(firmware, log_file)

if __name__ == '__main__':
    unittest.main()
