import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from .analyzer import analyze_error

def run_script(script_path: str, script_args: Optional[List[str]] = None) -> int:

    script_args = script_args or []

    script_file = Path(script_path)
    if not script_file.exists():
        print(f"❌ Script not found:{script_file}")
        return 1

    cmd = [sys.executable, str(script_file)] + script_args

    print(f"▶ Executing:{' '.join(cmd)}\n")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = process.communicate()

    if stdout:
        print(stdout, end="")

    if process.returncode == 0:
        print("✅ The script has completed execution and no errors were detected.")
        return 0

    print("❌ The script execution encountered an error; the original stderr output is as follows:\n")
    if stderr:
        print(stderr)

    print("\n🤖 An error occurred while calling OpenAI for analysis, please wait...\n")

    explanation = analyze_error(stderr)
    print("💡 AI analysis results:\n")
    print(explanation)

    return process.returncode
