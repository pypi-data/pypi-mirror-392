import subprocess
import sys
from pathlib import Path

def ferb_run():
    script = Path(__file__).parent / "ferbCode.py"

    if not script.exists():
        raise FileNotFoundError(f"Cannot find: {script}")

    subprocess.run([sys.executable, str(script)])