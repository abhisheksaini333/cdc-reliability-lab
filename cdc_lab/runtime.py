
from pathlib import Path
import subprocess, json, urllib.request, urllib.error, time
ROOT = Path(__file__).resolve().parents[1]

def command(args, input=None, timeout=120):
    result = subprocess.run(args, cwd=ROOT, input=input, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode:
        raise RuntimeError("command failed (exit %s): %s" % (result.returncode, result.stderr[-3000:]))
    return result.stdout

def compose(*args, input=None, timeout=120):
    return command(["docker", "compose", "-p", "cdc-2022-validation", *args], input, timeout)
