import unittest
import os
import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

# Mock external dependencies if not already mocked
if "pygit2" not in sys.modules or not isinstance(sys.modules["pygit2"], MagicMock):
    sys.modules["pygit2"] = MagicMock()

if "rich" not in sys.modules or not isinstance(sys.modules["rich"], MagicMock):
    sys.modules["rich"] = MagicMock()
    sys.modules["rich.console"] = MagicMock()
    sys.modules["rich.live"] = MagicMock()
    sys.modules["rich.panel"] = MagicMock()
    sys.modules["rich.progress"] = MagicMock()
    sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestLogging(unittest.TestCase):
    def setUp(self):
        # Mock Reporter dependencies
        self.mock_console = patch('bastardkb_build_releases.Console').start()
        # Mock RotatingFileHandler specifically in the module
        self.mock_handler_cls = patch('bastardkb_build_releases.RotatingFileHandler').start()
        self.mock_handler_instance = self.mock_handler_cls.return_value
        # Ensure it has a level attribute as it might be accessed
        self.mock_handler_instance.level = 0

        self.mock_chmod = patch('os.chmod').start()
        self.mock_mkdir = patch('pathlib.Path.mkdir').start()
        self.mock_touch = patch('pathlib.Path.touch').start()

        # Mock tempfile.mkdtemp to avoid creating real temp dirs for the progress logger
        patch('tempfile.mkdtemp', return_value='/tmp/mock_log_dir').start()

    def tearDown(self):
        patch.stopall()

    @patch.dict(os.environ, {}, clear=True)
    def test_log_dir_default(self):
        """Test default log directory is ~/.local/state/bastardkb-qmk"""
        # Mock Path.home()
        with patch('pathlib.Path.home', return_value=Path('/home/user')):
            reporter = bkb.Reporter(verbose=False)

            # Verify directory creation
            expected_dir = Path('/home/user/.local/state/bastardkb-qmk')
            self.mock_mkdir.assert_called_with(parents=True, exist_ok=True)

            # Verify permissions set on directory (0o700)
            # We expect os.chmod to be called on the directory
            # Depending on implementation order, we check any call
            self.mock_chmod.assert_any_call(expected_dir, 0o700)

            # Verify log file path passed to handler
            expected_log = expected_dir / "bastardkb_build_releases.py.log"
            self.mock_handler_cls.assert_called_with(
                filename=expected_log,
                encoding="utf-8",
                maxBytes=1024 * 1024,
                backupCount=5,
            )

            # Verify file permissions set (0o600)
            # Since the file doesn't exist in our mock environment, touch(mode=0o600) is called
            self.mock_touch.assert_called_with(mode=0o600)

    @patch.dict(os.environ, {'XDG_STATE_HOME': '/custom/state'}, clear=True)
    def test_log_dir_xdg(self):
        """Test log directory respects XDG_STATE_HOME"""
        reporter = bkb.Reporter(verbose=False)

        expected_dir = Path('/custom/state/bastardkb-qmk')
        self.mock_mkdir.assert_called_with(parents=True, exist_ok=True)
        self.mock_chmod.assert_any_call(expected_dir, 0o700)

        expected_log = expected_dir / "bastardkb_build_releases.py.log"
        self.mock_handler_cls.assert_called_with(
            filename=expected_log,
            encoding="utf-8",
            maxBytes=1024 * 1024,
            backupCount=5,
        )
        self.mock_touch.assert_called_with(mode=0o600)

if __name__ == '__main__':
    unittest.main()
