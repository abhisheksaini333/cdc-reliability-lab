import subprocess, unittest
class CLI(unittest.TestCase):
    def test_help(self):
        result = subprocess.run(['python3','-m','cdc_lab.cli','--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertIn('init-env',result.stdout)

    def test_recovery_options_are_available(self):
        for action,flag in [('submit','--restore'),('savepoint','--stop')]:
            result=subprocess.run(['python3','-m','cdc_lab.cli',action,'--help'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0)
            self.assertIn(flag,result.stdout)
