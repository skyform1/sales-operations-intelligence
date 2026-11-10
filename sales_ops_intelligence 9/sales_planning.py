"""Deterministic quota, territory and compensation planning for synthetic sales data."""
import csv
import json
from collections import defaultdict
from pathlib import Path
from forecast import START, END
from generate_data import ROOT, REGIONS, STAGES

REGION_POTENTIAL = {'North America': 1.30, 'EMEA': 1.10, 'APAC': 0.95, 'LATAM': 0.75}
ANNUAL_TARGET = 120_000_000
QUARTER_TARGET = ANNUAL_TARGET / 4


def read_csv(path):
    with Path(path).open(newline='') as f:
        return list(csv.DictReader(f))


def allocate_quotas(sellers, regional_weights=None, target=QUARTER_TARGET):
    """Allocate quarterly target proportionally to region potential and seller capacity.

    Rounding residual is assigned to final seller to reconcile exactly to target.
    """
    weights = regional_weights or REGION_POTENTIAL
    if not sellers or target < 0:
        raise ValueError('Sellers must be nonempty and target nonnegative')
    scored = []
    for seller in sellers:
        capacity = float(seller.get('capacity_fte', 1.0))
        weight = float(weights[seller['region']])
        if capacity <= 0 or weight <= 0:
            raise ValueError('Capacity and regional potential must be positive')
        scored.append((seller, capacity * weight))
    total_weight = sum(score for _, score in scored)
    remaining_cents = round(target * 100)
    result = []
    for index, (seller, score) in enumerate(scored):
        cents = round(target * 100 * score / total_weight) if index < len(scored) - 1 else remaining_cents
        remaining_cents -= cents
        result.append({**seller, 'planned_quota_usd': cents / 100, 'capacity_fte': float(seller.get('capacity_fte', 1.0)), 'territory_potential_index': float(weights[seller['region']])})
    return result


def performance(sellers, opportunities, planned):
    """Compute actual and projected bookings; exclude deals outside the quarter."""
    won, open_weighted, pipeline = defaultdict(float), defaultdict(float), defaultdict(float)
    for o in opportunities:
        sid = o['seller_id']
        status = o['status']
        if status == 'Won' and o.get('actual_close_date') and START.isoformat() <= o['actual_close_date'] <= END.isoformat():
            won[sid] += float(o['amount_usd'])
        elif status == 'Open' and START.isoformat() <= o['expected_close_date'] <= END.isoformat():
            amount = float(o['amount_usd'])
            open_weighted[sid] += amount * STAGES[o['stage']]
            pipeline[sid] += amount
    quotas = {s['seller_id']: float(s['planned_quota_usd']) for s in planned}
    result = []
    for seller in sellers:
        sid = seller['seller_id']
        q = quotas[sid]
        actual, projected = won[sid], won[sid] + open_weighted[sid]
        result.append({'seller_id': sid, 'region': seller['region'], 'planned_quota_usd': round(q, 2),
                       'actual_bookings_usd': round(actual, 2), 'weighted_open_usd': round(open_weighted[sid], 2),
                       'projected_bookings_usd': round(projected, 2), 'open_pipeline_usd': round(pipeline[sid], 2),
                       'actual_attainment_pct': round(100 * actual / q, 2) if q else 0,
                       'projected_attainment_pct': round(100 * projected / q, 2) if q else 0})
    return result


def commission(bookings, quota, base_rate=0.08, accelerator=1.5, cap=None):
    """Pay 8% on bookings through quota, 12% above quota (default); no payout on forecasts."""
    if bookings < 0 or quota <= 0 or base_rate < 0 or accelerator < 0:
        raise ValueError('Invalid compensation inputs')
    normal = min(bookings, quota) * base_rate
    accelerated = max(bookings - quota, 0) * base_rate * accelerator
    payout = normal + accelerated
    return round(min(payout, cap) if cap is not None else payout, 2)


def compensation_scenarios(rows):
    scenarios = {'standard_8pct_1_5x': (0.08, 1.5), 'flat_8pct': (0.08, 1.0), 'accelerated_8pct_2x': (0.08, 2.0)}
    return {name: {'total_payout_usd': round(sum(commission(r['actual_bookings_usd'], r['planned_quota_usd'], rate, accel) for r in rows), 2),
                   'seller_payouts_usd': {r['seller_id']: commission(r['actual_bookings_usd'], r['planned_quota_usd'], rate, accel) for r in rows}}
            for name, (rate, accel) in scenarios.items()}


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['region']].append(row)
    out = {}
    for region in REGIONS:
        records = groups[region]
        quota = sum(r['planned_quota_usd'] for r in records)
        actual = sum(r['actual_bookings_usd'] for r in records)
        projected = sum(r['projected_bookings_usd'] for r in records)
        out[region] = {'sellers': len(records), 'quota_usd': round(quota, 2), 'actual_bookings_usd': round(actual, 2),
                       'projected_bookings_usd': round(projected, 2), 'actual_attainment_pct': round(actual / quota * 100, 2) if quota else 0,
                       'projected_attainment_pct': round(projected / quota * 100, 2) if quota else 0}
    return out


def run():
    sellers = read_csv(ROOT / 'data/sellers.csv')
    opportunities = read_csv(ROOT / 'data/opportunities.csv')
    planned = allocate_quotas(sellers)
    rows = performance(sellers, opportunities, planned)
    scenarios = compensation_scenarios(rows)
    outputs = ROOT / 'outputs'
    outputs.mkdir(exist_ok=True)
    with (outputs / 'seller_performance.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with (outputs / 'sales_planning.json').open('w') as f:
        json.dump({'assumptions': {'quarter': '2026-Q4', 'annual_target_usd': ANNUAL_TARGET, 'quarter_target_usd': QUARTER_TARGET,
                                  'territory_potential': REGION_POTENTIAL, 'commission_base_rate': 0.08, 'commission_accelerator': 1.5},
                   'regions': summarize(rows), 'compensation': {k: {'total_payout_usd': v['total_payout_usd']} for k, v in scenarios.items()}}, f, indent=2)
    return rows

if __name__ == '__main__':
    print(json.dumps(summarize(run()), indent=2))
