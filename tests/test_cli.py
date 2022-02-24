import subprocess, unittest
class CLI(unittest.TestCase):
    def test_help(self):
        result = subprocess.run(['python3','-m','cdc_lab.cli','--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertIn('init-env',result.stdout)
