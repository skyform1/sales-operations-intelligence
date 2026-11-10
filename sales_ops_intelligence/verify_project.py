"""Reproducible standard-library verification for portfolio reviewers."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEPS = ['generate_data.py','forecast.py','sales_planning.py','contract_ops.py','decision_intelligence.py','forecast_risk.py','executive_simulation.py','quality.py']

def main():
    for script in STEPS:
        print(f'RUN {script}', flush=True)
        subprocess.run([sys.executable, str(ROOT/script)], cwd=ROOT, check=True)
    print('RUN unit tests', flush=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'], cwd=ROOT, check=True)
    report = ROOT/'outputs'/'quality_report.json'
    if report.exists():
        print('QUALITY REPORT:', report.read_text()[:1500])
    print('PASS: full reproducibility workflow')

if __name__ == '__main__': main()
