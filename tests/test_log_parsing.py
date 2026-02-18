import unittest
import sys
import os
import unittest.mock
from pathlib import Path

# Mock dependencies
sys.modules["pygit2"] = unittest.mock.MagicMock()
sys.modules["rich"] = unittest.mock.MagicMock()
sys.modules["rich.console"] = unittest.mock.MagicMock()
sys.modules["rich.live"] = unittest.mock.MagicMock()
sys.modules["rich.panel"] = unittest.mock.MagicMock()

# Ensure Panel is a class for isinstance checks and handles Mock args without InvalidSpecError
class MockPanel(unittest.mock.MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if args:
            self.renderable = args[0]

sys.modules["rich.panel"].Panel = MockPanel
sys.modules["rich.progress"] = unittest.mock.MagicMock()
sys.modules["rich.text"] = unittest.mock.MagicMock()

# Add root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

import bastardkb_build_releases as bkb

class TestLogParsing(unittest.TestCase):
    def test_read_firmware_filename_valid(self):
        """Test valid log parsing."""
        firmware = bkb.Firmware(keyboard="test/kb", keymap="default", keymap_alias="stock")
        # output_filename should be bastardkb_test_kb_stock
        expected_stem = "bastardkb_test_kb_stock"

        log_content = f"""Line 1
Copying {expected_stem}.hex to qmk_firmware folder
Done
"""
        log_file = unittest.mock.MagicMock(spec=Path)
        log_file.open = unittest.mock.mock_open(read_data=log_content)

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(str(result), f"{expected_stem}.hex")

    def test_read_firmware_filename_multiple_extensions(self):
        """Test parsing with multiple dots in filename (e.g. .uf2.bin - unlikely but possible)."""
        firmware = bkb.Firmware(keyboard="test/kb", keymap="default", keymap_alias="stock")
        expected_stem = "bastardkb_test_kb_stock"

        log_content = f"Copying {expected_stem}.uf2 to qmk_firmware folder\n"
        log_file = unittest.mock.MagicMock(spec=Path)
        log_file.open = unittest.mock.mock_open(read_data=log_content)

        result = bkb.read_firmware_filename_from_logs(firmware, log_file)
        self.assertEqual(str(result), f"{expected_stem}.uf2")

    def test_read_firmware_filename_not_found(self):
        """Test FileNotFoundError when line is missing."""
        firmware = bkb.Firmware(keyboard="test/kb", keymap="default", keymap_alias="stock")

        log_content = """Line 1
Copying nothing here
Done
"""
        log_file = unittest.mock.MagicMock(spec=Path)
        log_file.open = unittest.mock.mock_open(read_data=log_content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

    def test_read_firmware_filename_partial_match(self):
        """Test partial match (filename starts with stem but no dot)."""
        firmware = bkb.Firmware(keyboard="test/kb", keymap="default", keymap_alias="stock")
        expected_stem = "bastardkb_test_kb_stock"

        # Should NOT match because no dot
        log_content = f"Copying {expected_stem}NOTADOT to qmk_firmware folder\n"
        log_file = unittest.mock.MagicMock(spec=Path)
        log_file.open = unittest.mock.mock_open(read_data=log_content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

    def test_read_firmware_filename_short_match(self):
        """Test match where filename is exactly the stem (no extension)."""
        firmware = bkb.Firmware(keyboard="test/kb", keymap="default", keymap_alias="stock")
        expected_stem = "bastardkb_test_kb_stock"

        # Should NOT match because we require at least one char after stem (the dot)
        log_content = f"Copying {expected_stem} to qmk_firmware folder\n"
        log_file = unittest.mock.MagicMock(spec=Path)
        log_file.open = unittest.mock.mock_open(read_data=log_content)

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(firmware, log_file)

if __name__ == '__main__':
    unittest.main()
