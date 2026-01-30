import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Mock dependencies BEFORE import
sys.modules["pygit2"] = MagicMock()
sys.modules["rich"] = MagicMock()
sys.modules["rich.console"] = MagicMock()
sys.modules["rich.live"] = MagicMock()
sys.modules["rich.panel"] = MagicMock()
sys.modules["rich.progress"] = MagicMock()
sys.modules["rich.text"] = MagicMock()

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bastardkb_build_releases

class TestParallelDefault(unittest.TestCase):
    @patch('argparse.ArgumentParser')
    def test_default_parallel_is_cpu_count(self, mock_argparse):
        # Setup mock parser
        mock_parser = MagicMock()
        mock_argparse.return_value = mock_parser

        # Mock sys.argv to avoid side effects
        with patch.object(sys, 'argv', ['bastardkb_build_releases.py', '--dry-run']):
            mock_args = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            from pathlib import Path
            mock_args.verbose = False
            mock_args.repository = Path('.')
            mock_args.output_dir = MagicMock()
            mock_args.dry_run = True
            mock_args.parallel = 1
            mock_args.filter = ".*"

            # Mock Repository to pass checks
            mock_repo_cls = sys.modules["pygit2"].Repository
            mock_repo = MagicMock()
            mock_repo_cls.return_value = mock_repo
            mock_repo.is_bare = True

            try:
                bastardkb_build_releases.main()
            except SystemExit:
                pass
            except Exception as e:
                # If it fails for other reasons, we might still have caught the add_argument call
                print(f"Caught exception: {e}")
                pass

            # Find the call for --parallel
            found = False
            for call in mock_parser.add_argument.call_args_list:
                args, kwargs = call
                if '-j' in args or '--parallel' in args:
                    self.assertEqual(kwargs.get('default'), os.cpu_count() or 1, "Default value for --parallel should be os.cpu_count() or 1")
                    found = True
                    break

            self.assertTrue(found, "--parallel argument not found")

if __name__ == '__main__':
    unittest.main()
