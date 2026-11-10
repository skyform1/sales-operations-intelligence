import csv, random
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).parent
STAGES = {'Prospecting': 0.10, 'Qualified': 0.25, 'Proposal': 0.50, 'Negotiation': 0.75}
REGIONS = ['North America', 'EMEA', 'APAC', 'LATAM']

def generate(seed=42, count=2400):
    rng = random.Random(seed)
    (ROOT / 'data').mkdir(exist_ok=True)
    sellers = []
    for i in range(80):
        sellers.append({'seller_id': f'S{i+1:03d}', 'region': REGIONS[i // 20], 'quarterly_quota_usd': 375000})
    with (ROOT/'data'/'sellers.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(sellers[0])); w.writeheader(); w.writerows(sellers)
    rows = []
    for i in range(count):
        seller = rng.choice(sellers)
        status = rng.choices(['Open', 'Won', 'Lost'], weights=[0.65, 0.20, 0.15])[0]
        stage = rng.choice(list(STAGES)) if status == 'Open' else ('Closed Won' if status == 'Won' else 'Closed Lost')
        close = date(2026, 10, 1) + timedelta(days=rng.randint(0, 89))
        rows.append({'opportunity_id': f'O{i+1:05d}', 'seller_id': seller['seller_id'], 'region': seller['region'],
                     'amount_usd': rng.randrange(15000, 95001, 5000), 'status': status, 'stage': stage,
                     'expected_close_date': close.isoformat(), 'actual_close_date': close.isoformat() if status != 'Open' else ''})
    with (ROOT/'data'/'opportunities.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows

if __name__ == '__main__':
    generate()
    print('Generated 80 sellers and 2,400 synthetic opportunities.')
