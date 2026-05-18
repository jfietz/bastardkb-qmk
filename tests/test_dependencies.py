import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add root to sys.path to import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases as bkb

class TestDependencies(unittest.TestCase):
    def test_check_dependencies_success(self):
        """Verify check_dependencies passes when all tools are present."""
        reporter = MagicMock()

        # We need to mock shutil.which to return a path (truthy) for both 'git' and 'qmk'
        with patch('shutil.which') as mock_which:
            mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}"

            if hasattr(bkb, 'check_dependencies'):
                bkb.check_dependencies(reporter)
                # Should not call fatal or exit
                reporter.fatal.assert_not_called()
            else:
                self.fail("check_dependencies function not found in module")

    def test_check_dependencies_missing_qmk(self):
        """Verify check_dependencies fails when qmk is missing."""
        reporter = MagicMock()

        with patch('shutil.which') as mock_which:
            # return None for qmk, path for git
            def side_effect(cmd):
                if cmd == 'qmk': return None
                return f"/usr/bin/{cmd}"
            mock_which.side_effect = side_effect

            with self.assertRaises(SystemExit) as cm:
                if hasattr(bkb, 'check_dependencies'):
                    bkb.check_dependencies(reporter)
                else:
                    self.fail("check_dependencies function not found in module")

            self.assertEqual(cm.exception.code, 1)
            reporter.fatal.assert_called_once()
            args, _ = reporter.fatal.call_args
            self.assertIn("qmk", args[0])

    def test_check_dependencies_missing_git(self):
        """Verify check_dependencies fails when git is missing."""
        reporter = MagicMock()

        with patch('shutil.which') as mock_which:
            def side_effect(cmd):
                if cmd == 'git': return None
                return f"/usr/bin/{cmd}"
            mock_which.side_effect = side_effect

            with self.assertRaises(SystemExit) as cm:
                if hasattr(bkb, 'check_dependencies'):
                    bkb.check_dependencies(reporter)
                else:
                    self.fail("check_dependencies function not found in module")

            self.assertEqual(cm.exception.code, 1)
            reporter.fatal.assert_called_once()
            args, _ = reporter.fatal.call_args
            self.assertIn("git", args[0])
