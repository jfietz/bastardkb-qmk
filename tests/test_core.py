import sys
import os
import unittest
from collections import namedtuple

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestCore(unittest.TestCase):
    def test_total_firmware_count_reduce_callback(self):
        """Verify the callback correctly counts firmwares without converting to list."""
        FirmwareList = bkb.FirmwareList
        Firmware = bkb.Firmware

        # Create a mock FirmwareList
        # configurations is a tuple
        fw_list = FirmwareList(
            branch="test",
            configurations=(
                Firmware("k1", "m1"),
                Firmware("k2", "m2"),
            )
        )

        # Test the callback
        count = bkb.total_firmware_count_reduce_callback(0, fw_list)
        self.assertEqual(count, 2)

        # Test accumulation
        count = bkb.total_firmware_count_reduce_callback(5, fw_list)
        self.assertEqual(count, 7)

if __name__ == '__main__':
    unittest.main()
