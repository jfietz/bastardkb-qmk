import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock missing dependencies
sys.modules['pygit2'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.live'] = MagicMock()
sys.modules['rich.panel'] = MagicMock()
sys.modules['rich.progress'] = MagicMock()
sys.modules['rich.text'] = MagicMock()

# Ensure Panel is a class so that isinstance checks (if any) might work or at least it's callable
class MockPanel:
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get('title', '')
sys.modules['rich.panel'].Panel = MockPanel

import bastardkb_build_releases as bkb

class TestDependencies(unittest.TestCase):
    def setUp(self):
        self.reporter = MagicMock()

    @patch('shutil.which')
    def test_missing_qmk(self, mock_which):
        # Mock qmk missing, git present
        def side_effect(cmd):
            if cmd == 'qmk':
                return None
            return '/usr/bin/git'
        mock_which.side_effect = side_effect

        # Verify SystemExit is raised
        with self.assertRaises(SystemExit) as cm:
            bkb.check_dependencies(self.reporter)

        self.assertEqual(cm.exception.code, 1)
        # Verify reporter.fatal was called with appropriate message
        self.reporter.fatal.assert_called()
        args, _ = self.reporter.fatal.call_args
        self.assertIn("qmk", args[0])

    @patch('shutil.which')
    def test_missing_git(self, mock_which):
        # Mock qmk present, git missing
        def side_effect(cmd):
            if cmd == 'qmk':
                return '/usr/bin/qmk'
            if cmd == 'git':
                return None
            return None
        mock_which.side_effect = side_effect

        with self.assertRaises(SystemExit) as cm:
            bkb.check_dependencies(self.reporter)

        self.assertEqual(cm.exception.code, 1)
        self.reporter.fatal.assert_called()
        args, _ = self.reporter.fatal.call_args
        self.assertIn("git", args[0])

    @patch('shutil.which')
    def test_all_dependencies_present(self, mock_which):
        mock_which.return_value = '/usr/bin/executable'

        # Should not raise exception
        try:
            bkb.check_dependencies(self.reporter)
        except SystemExit:
            self.fail("check_dependencies raised SystemExit unexpectedly!")

if __name__ == '__main__':
    unittest.main()
