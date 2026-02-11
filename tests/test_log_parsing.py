import unittest
import sys
import os
from unittest.mock import MagicMock
from pathlib import Path

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestFirmwareParsing(unittest.TestCase):
    def test_read_firmware_filename_valid(self):
        """Verify correct filename extraction with new regex logic."""
        firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
        filename = "bastardkb_skeletyl_v2_elitec_default.hex"
        log_file = Path("test_log_perf.txt")
        content = f"Some preable\nCopying {filename} to qmk_firmware folder\nPostamble"

        try:
            with log_file.open("w") as f:
                f.write(content)

            result = bkb.read_firmware_filename_from_logs(firmware, log_file)
            self.assertEqual(str(result), filename)
        finally:
            if log_file.exists():
                log_file.unlink()

    def test_read_firmware_filename_invalid_prefix(self):
        """Verify mismatching filename prefix is ignored."""
        firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
        wrong_filename = "bastardkb_other_board.hex"
        log_file = Path("test_log_perf.txt")
        content = f"Copying {wrong_filename} to qmk_firmware folder"

        try:
            with log_file.open("w") as f:
                f.write(content)

            with self.assertRaises(FileNotFoundError):
                bkb.read_firmware_filename_from_logs(firmware, log_file)
        finally:
            if log_file.exists():
                log_file.unlink()

    def test_read_firmware_filename_invalid_extension(self):
        """Verify invalid extension (uppercase) is rejected."""
        firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
        filename = "bastardkb_skeletyl_v2_elitec_default.EXE"
        log_file = Path("test_log_perf.txt")
        content = f"Copying {filename} to qmk_firmware folder"

        try:
            with log_file.open("w") as f:
                f.write(content)

            with self.assertRaises(FileNotFoundError):
                bkb.read_firmware_filename_from_logs(firmware, log_file)
        finally:
            if log_file.exists():
                log_file.unlink()

    def test_read_firmware_filename_weird_extension(self):
        """Verify weird but valid extension (all digits)."""
        firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
        filename = "bastardkb_skeletyl_v2_elitec_default.123"
        log_file = Path("test_log_perf.txt")
        content = f"Copying {filename} to qmk_firmware folder"

        try:
            with log_file.open("w") as f:
                f.write(content)

            result = bkb.read_firmware_filename_from_logs(firmware, log_file)
            self.assertEqual(str(result), filename)
        finally:
            if log_file.exists():
                log_file.unlink()

    def test_read_firmware_filename_mixed_extension(self):
         """Verify mixed digits and letters (v1)."""
         firmware = bkb.Firmware(keyboard="skeletyl/v2/elitec", keymap="default")
         filename = "bastardkb_skeletyl_v2_elitec_default.v1"
         log_file = Path("test_log_perf.txt")
         content = f"Copying {filename} to qmk_firmware folder"

         try:
             with log_file.open("w") as f:
                 f.write(content)

             result = bkb.read_firmware_filename_from_logs(firmware, log_file)
             self.assertEqual(str(result), filename)
         finally:
             if log_file.exists():
                 log_file.unlink()

if __name__ == '__main__':
    unittest.main()
