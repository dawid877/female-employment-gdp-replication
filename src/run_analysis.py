import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = [
    "src/diagnostics.py",
    "src/sur_model.py",
    "src/compare_with_paper.py",
    "src/robustness_checks.py",]


def run_script(script_path):
    print(f"\nRunning {script_path}...")

    subprocess.run(
        [sys.executable, str(ROOT / script_path)],
        check=True,)


def main():
    for script in SCRIPTS:
        run_script(script)

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()