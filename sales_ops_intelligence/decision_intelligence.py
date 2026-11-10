"""Phase 4: deterministic, explainable executive decision support on synthetic data.
Recommendations are proposals only; no external actions are executed.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from contract_ops import analyze_contracts, generate_contracts
from sales_planning import (QUARTER_TARGET, REGION_POTENTIAL, allocate_quotas,
                            commission, performance, read_csv, summarize)
from generate_data import ROOT


def decision_brief(sellers, opportunities, contracts=None, target=QUARTER_TARGET, weights=None,
                   delayed_threshold_days=14, commission_rate=0.08, accelerator=1.5):
    if target <= 0 or delayed_threshold_days <= 0:
        raise ValueError('Target and delay threshold must be positive')
    if not 0 <= commission_rate <= 1 or accelerator < 1:
        raise ValueError('Invalid commission assumptions')
    weights = weights if weights is not None else REGION_POTENTIAL
    contracts = generate_contracts(opportunities) if contracts is None else contracts
    planned = allocate_quotas(sellers, weights, target)
    seller_rows = performance(sellers, opportunities, planned)
    regions = summarize(seller_rows)
    contract_summary = analyze_contracts(contracts)
    actual = round(sum(r['actual_bookings_usd'] for r in seller_rows), 2)
    projected = round(sum(r['projected_bookings_usd'] for r in seller_rows), 2)
    open_weighted = round(projected - actual, 2)
    comp = round(sum(commission(r['actual_bookings_usd'], r['planned_quota_usd'], commission_rate, accelerator) for r in seller_rows), 2)
    delayed = [c for c in contracts if c['status'] != 'Signed' and float(c['review_days']) > delayed_threshold_days]
    pending = [c for c in contracts if c['status'] != 'Signed']
    recommendations = []

    def add(rid, priority, heading, rationale, evidence, action, uncertainty, owner):
        recommendations.append({'id':rid,'priority':priority,'title':heading,'rationale':rationale,
                                'evidence':evidence,'proposed_action':action,'uncertainty':uncertainty,
                                'suggested_owner':owner,'approval_status':'Proposed'})

    if projected < target:
        add('REV-001','High','Review projected bookings shortfall',
            'The synthetic projected bookings total is below the quarterly target.',
            {'projected_usd':projected,'target_usd':target,'shortfall_usd':round(target-projected,2)},
            'Review stage-level pipeline quality, coverage and close dates before changing quota or staffing.',
            'Stage probabilities are assumed and not calibrated against historical outcomes.','Revenue Operations')
    if projected >= target:
        add('REV-002','Medium','Validate forecast overattainment',
            'Projected bookings exceed the quarterly target; unrealistic synthetic attainment may distort planning.',
            {'projected_usd':projected,'target_usd':target,'attainment_pct':round(projected/target*100,2)},
            'Backtest stage probabilities and recalibrate pipeline generation and targets before making staffing decisions.',
            'Synthetic bookings are not evidence of actual commercial performance.','Revenue Operations')
    for region, r in sorted(regions.items()):
        if r['projected_attainment_pct'] < 80:
            add('REG-'+region.replace(' ','-').upper(),'High',f'Investigate {region} projected attainment',
                'Regional projected attainment is below the illustrative 80% review threshold.',
                {'region':region,'projected_attainment_pct':r['projected_attainment_pct'],'quota_usd':r['quota_usd']},
                'Validate territory opportunity, seller capacity, pipeline coverage and quota fairness.',
                'Territory potential is synthetic; low attainment does not establish seller underperformance.','Regional Sales Operations')
    if delayed:
        add('CTR-001','High','Triage delayed unsigned contracts',
            'Unsigned contracts exceed the illustrative review-time threshold.',
            {'delayed_unsigned_count':len(delayed),'pending_contract_count':len(pending),
             'delayed_unsigned_value_usd':round(sum(float(c['deal_value_usd']) for c in delayed),2),
             'delay_threshold_days':delayed_threshold_days},
            'Review approval ownership and bottlenecks; escalate only after verifying contract status and policy.',
            'Contract durations and statuses are simulated; deal value is not equivalent to recoverable revenue.','Deal Desk / Legal')
    add('COMP-001','Medium','Review commission cost sensitivity',
        'Commission expense is calculated from closed-won bookings using an illustrative plan.',
        {'commission_expense_usd':comp,'base_rate':commission_rate,'accelerator':accelerator},
        'Compare commission scenarios against budget and check eligibility, clawbacks and crediting rules.',
        'No compensation contract, payout eligibility or payroll data is modeled.','Sales Finance')
    priority_order={'High':0,'Medium':1,'Low':2}
    recommendations.sort(key=lambda x:(priority_order[x['priority']],x['id']))
    return {'metadata':{'quarter':'2026-Q4','data_type':'synthetic','model_type':'deterministic_rules',
                        'approval_required':True,'forecast_calibrated':False},
            'kpis':{'quarterly_target_usd':target,'closed_won_bookings_usd':actual,
                    'weighted_open_pipeline_usd':open_weighted,'projected_bookings_usd':projected,
                    'actual_attainment_pct':round(actual/target*100,2),
                    'projected_attainment_pct':round(projected/target*100,2),
                    'commission_expense_usd':comp,'pending_contracts':len(pending),
                    'delayed_unsigned_contracts':len(delayed)},
            'regions':regions,'contract_operations':contract_summary,
            'recommendations':recommendations,
            'limitations':['Stage probabilities and regional potential are uncalibrated assumptions.',
                           'Synthetic contracts are not real approval events.',
                           'Proposals are not executed and require human verification.']}


def scenario_comparison(sellers, opportunities, contracts=None, target=QUARTER_TARGET):
    cases=[('Baseline',target,0.08,1.5),('Target +10%',target*1.10,0.08,1.5),
           ('Flat commission',target,0.08,1.0),('Accelerator 2x',target,0.08,2.0)]
    result=[]
    for name,t,rate,accel in cases:
        k=decision_brief(sellers,opportunities,contracts,t,commission_rate=rate,accelerator=accel)['kpis']
        result.append({'scenario':name,'target_usd':t,'projected_usd':k['projected_bookings_usd'],
                       'projected_attainment_pct':k['projected_attainment_pct'],
                       'commission_expense_usd':k['commission_expense_usd']})
    return result


def approval_record(recommendation_id, decision, reviewer, reason, allowed_ids):
    """Construct auditable human review event; does not execute proposed action."""
    if recommendation_id not in allowed_ids:
        raise ValueError('Unknown recommendation ID')
    if decision not in ('Approved for further review','Rejected','Needs evidence'):
        raise ValueError('Invalid decision')
    if not reviewer.strip() or not reason.strip():
        raise ValueError('Reviewer and rationale are required')
    return {'recommendation_id':recommendation_id,'decision':decision,
            'reviewer':reviewer.strip(),'rationale':reason.strip(),
            'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'executed':False}


def run():
    sellers=read_csv(ROOT/'data/sellers.csv')
    opps=read_csv(ROOT/'data/opportunities.csv')
    contracts=generate_contracts(opps)
    brief=decision_brief(sellers,opps,contracts)
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    (out/'executive_brief.json').write_text(json.dumps(brief,indent=2))
    (out/'scenario_comparison.json').write_text(json.dumps(scenario_comparison(sellers,opps,contracts),indent=2))
    return brief

if __name__=='__main__':
    brief=run()
    print(json.dumps({'kpis':brief['kpis'],'recommendations':len(brief['recommendations'])},indent=2))
