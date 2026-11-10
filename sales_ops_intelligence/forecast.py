import csv, json
from collections import defaultdict
from datetime import date
from pathlib import Path
from generate_data import STAGES, generate, ROOT

START, END = date(2026, 10, 1), date(2026, 12, 31)

def forecast(rows):
    by_region = defaultdict(lambda: {'closed_won': 0.0, 'weighted_open': 0.0, 'open_pipeline': 0.0, 'open_count': 0})
    for row in rows:
        status = row['status']
        if status == 'Won':
            when = date.fromisoformat(row['actual_close_date'])
        elif status == 'Open':
            when = date.fromisoformat(row['expected_close_date'])
        else:
            continue
        if not START <= when <= END:
            continue
        amount = float(row['amount_usd'])
        result = by_region[row['region']]
        if status == 'Won':
            result['closed_won'] += amount
        else:
            result['weighted_open'] += amount * STAGES[row['stage']]
            result['open_pipeline'] += amount
            result['open_count'] += 1
    result = {}
    for region, values in sorted(by_region.items()):
        total = values['closed_won'] + values['weighted_open']
        result[region] = {**values, 'forecast_bookings_usd': round(total, 2),
                          'quarterly_target_usd': 7500000,
                          'attainment_pct': round(total / 7500000 * 100, 2)}
    return result

if __name__ == '__main__':
    path = ROOT/'data'/'opportunities.csv'
    if not path.exists(): generate()
    with path.open(newline='') as f: rows = list(csv.DictReader(f))
    result = forecast(rows)
    (ROOT/'outputs').mkdir(exist_ok=True)
    with (ROOT/'outputs'/'forecast.json').open('w') as f: json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
