"""Phase 5: reproducible integrity checks for the synthetic CRM model."""
import json
from collections import Counter
from sales_planning import read_csv, allocate_quotas, performance, QUARTER_TARGET
from forecast import forecast
from generate_data import ROOT, REGIONS, STAGES

def audit(sellers, opportunities):
    issues = []
    seller_ids = [s['seller_id'] for s in sellers]
    opp_ids = [o['opportunity_id'] for o in opportunities]
    if len(set(seller_ids)) != len(seller_ids): issues.append('Duplicate seller IDs')
    if len(set(opp_ids)) != len(opp_ids): issues.append('Duplicate opportunity IDs')
    known = set(seller_ids)
    regions = {s['seller_id']:s['region'] for s in sellers}
    for o in opportunities:
        if o['seller_id'] not in known: issues.append('Orphan opportunity: '+o['opportunity_id']); continue
        if o['region'] != regions[o['seller_id']]: issues.append('Region mismatch: '+o['opportunity_id'])
        if o['status'] not in ('Open','Won','Lost'): issues.append('Invalid status: '+o['opportunity_id'])
        if o['status']=='Open' and o['stage'] not in STAGES: issues.append('Invalid stage: '+o['opportunity_id'])
        if float(o['amount_usd']) <= 0: issues.append('Nonpositive deal amount: '+o['opportunity_id'])
        if o['status']=='Won' and not o['actual_close_date']: issues.append('Missing won close date: '+o['opportunity_id'])
    planned = allocate_quotas(sellers)
    rows = performance(sellers, opportunities, planned)
    total_actual = sum(r['actual_bookings_usd'] for r in rows)
    total_projected = sum(r['projected_bookings_usd'] for r in rows)
    total_quota = sum(r['planned_quota_usd'] for r in planned)
    forecast_total = sum(v['forecast_bookings_usd'] for v in forecast(opportunities).values())
    if abs(total_quota-QUARTER_TARGET)>0.01: issues.append('Quota reconciliation failed')
    if abs(total_projected-forecast_total)>0.1: issues.append('Forecast reconciliation failed')
    if total_projected < total_actual: issues.append('Projected bookings below actual')
    return {'passed':not issues,'issues':issues,'seller_count':len(sellers),'opportunity_count':len(opportunities),
            'status_counts':dict(Counter(o['status'] for o in opportunities)),
            'quarter_target_usd':QUARTER_TARGET,'closed_won_bookings_usd':round(total_actual,2),
            'projected_bookings_usd':round(total_projected,2),
            'actual_attainment_pct':round(total_actual/QUARTER_TARGET*100,2),
            'projected_attainment_pct':round(total_projected/QUARTER_TARGET*100,2),
            'forecast_reconciliation_delta_usd':round(total_projected-forecast_total,2)}

if __name__=='__main__':
    report=audit(read_csv(ROOT/'data'/'sellers.csv'),read_csv(ROOT/'data'/'opportunities.csv'))
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs'/'quality_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if not report['passed']: raise SystemExit(1)
