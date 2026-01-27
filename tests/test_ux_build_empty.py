import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestUXBuildEmpty(unittest.TestCase):
    def tearDown(self):
        # Clean up the module from sys.modules to ensure isolation for other tests
        if 'bastardkb_build_releases' in sys.modules:
            del sys.modules['bastardkb_build_releases']

    def test_build_warns_on_empty_firmware_list(self):
        # Mock dependencies in sys.modules for the duration of this test
        with patch.dict(sys.modules, {
            "pygit2": MagicMock(),
            "rich": MagicMock(),
            "rich.console": MagicMock(),
            "rich.live": MagicMock(),
            "rich.panel": MagicMock(),
            "rich.progress": MagicMock(),
            "rich.text": MagicMock(),
        }):
            # Ensure we re-import the module to pick up the mocks
            if 'bastardkb_build_releases' in sys.modules:
                del sys.modules['bastardkb_build_releases']

            import bastardkb_build_releases as bkb

            # Setup mocks for arguments
            executor = MagicMock()
            reporter = MagicMock()
            firmwares = [] # Empty list
            on_firmware_compiled = MagicMock()

            # Call build
            bkb.build(executor, reporter, firmwares, on_firmware_compiled)

            # Assert warning was called
            reporter.warn.assert_called_with("[bold yellow]No firmwares found matching the filter criteria.[/bold yellow]")

if __name__ == '__main__':
    unittest.main()
