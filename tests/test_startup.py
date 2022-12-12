import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from cdc_lab import config, pipeline, runtime, startup


class ComposeReached(RuntimeError):
    pass


class StartupTests(unittest.TestCase):
    def test_private_runtime_directory_exists_before_compose_up(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config.create_env(root / '.env')
            def compose(*args, **kwargs):
                directory = root / '.runtime'
                self.assertTrue(directory.is_dir(), 'Bind source must exist before Docker can create it')
                self.assertEqual(os.getuid(), directory.stat().st_uid)
                self.assertEqual(0o700, stat.S_IMODE(directory.stat().st_mode))
                raise ComposeReached()
            with patch.object(runtime, 'ROOT', root), patch.object(runtime, 'compose', side_effect=compose):
                with self.assertRaises(ComposeReached):
                    startup.start()

    def test_existing_directory_is_private_and_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / '.runtime'; directory.mkdir(mode=0o755)
            with patch.object(runtime, 'ROOT', root):
                self.assertEqual(directory, pipeline.prepare_runtime())
                self.assertEqual(0o700, stat.S_IMODE(directory.stat().st_mode))
                with patch('os.getuid', return_value=os.getuid() + 1):
                    with self.assertRaisesRegex(PermissionError, 'invoking user'):
                        pipeline.prepare_runtime()
                directory.rmdir(); directory.symlink_to(root, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, 'symlink'):
                    pipeline.prepare_runtime()
