
import unittest
import sys
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

# Mock dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()

    # Custom Mock for Panel to avoid InvalidSpecError
    def MockPanel(*args, **kwargs):
        m = MagicMock()
        m.title = kwargs.get("title", "")
        return m

    sys.modules["rich.panel"].Panel = MockPanel
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogParsing(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.log_file = Path(self.temp_dir.name) / "build.log"

        # Create a log file with content
        with self.log_file.open("w") as f:
            for i in range(100):
                f.write(f"Some compilation line {i}\n")
            f.write("Copying bastardkb_skeletyl_v1_elitec_default.hex to qmk_firmware folder\n")

        self.firmware = bkb.Firmware(
            keyboard="skeletyl/v1/elitec",
            keymap="default",
            keymap_alias=None,
            env_vars=[]
        )
        # Expected filename: bastardkb_skeletyl_v1_elitec_default

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_correctness_actual(self):
        # Verify the actual implementation finds the file
        result = bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)
        self.assertEqual(result.name, "bastardkb_skeletyl_v1_elitec_default.hex")

    def test_failure_handling(self):
        # Test file not found
        with self.log_file.open("w") as f:
            f.write("No match here\n")

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)

    def test_partial_match_rejection(self):
        # Test that partial matches are rejected
        with self.log_file.open("w") as f:
            f.write("Copying bastardkb_skeletyl_v1_elitec_default_extra.hex to qmk_firmware folder\n")

        with self.assertRaises(FileNotFoundError):
            bkb.read_firmware_filename_from_logs(self.firmware, self.log_file)

if __name__ == '__main__':
    unittest.main()
