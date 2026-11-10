"""Scenario-based forecast stress test; probabilities are assumptions, not learned estimates."""
import csv, json
from datetime import date
from pathlib import Path
from generate_data import ROOT, STAGES
from forecast import START, END

SCENARIOS = {
    'downside': {'probability_multiplier': .35, 'in_quarter_close_rate': .65},
    'base': {'probability_multiplier': .60, 'in_quarter_close_rate': .85},
    'upside': {'probability_multiplier': .90, 'in_quarter_close_rate': 1.00},
}
TARGET = 30_000_000

def analyze(rows, target=TARGET, scenarios=SCENARIOS):
    if target <= 0: raise ValueError('Target must be positive')
    won = 0.0
    open_rows = []
    for row in rows:
        amount = float(row['amount_usd'])
        if amount < 0: raise ValueError('Negative deal value')
        if row['status'] == 'Won' and row['actual_close_date']:
            if START <= date.fromisoformat(row['actual_close_date']) <= END:
                won += amount
        elif row['status'] == 'Open' and row['expected_close_date']:
            if START <= date.fromisoformat(row['expected_close_date']) <= END:
                if row['stage'] not in STAGES: raise ValueError('Unknown stage')
                open_rows.append((amount, STAGES[row['stage']]))
    results = {}
    for name, s in scenarios.items():
        mult, close = s['probability_multiplier'], s['in_quarter_close_rate']
        if not (0 <= mult <= 1 and 0 <= close <= 1):
            raise ValueError('Scenario factors must be in [0,1]')
        expected_open = sum(a * min(1, p * mult) * close for a,p in open_rows)
        projected = won + expected_open
        results[name] = {'closed_won_usd': round(won,2),
                         'risk_adjusted_open_usd': round(expected_open,2),
                         'projected_bookings_usd': round(projected,2),
                         'attainment_pct': round(projected / target * 100,2),
                         'target_gap_usd': round(projected - target,2)}
    return {'target_usd':target, 'scenario_assumptions':scenarios,
            'results':results, 'note':'Sensitivity analysis, not a confidence interval or validated forecast. Factors are hypothetical.'}

if __name__ == '__main__':
    with (ROOT/'data'/'opportunities.csv').open(newline='') as f: rows=list(csv.DictReader(f))
    report=analyze(rows)
    (ROOT/'outputs'/'forecast_risk.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report['results'],indent=2))
