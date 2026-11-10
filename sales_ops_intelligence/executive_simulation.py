"""Phase 7: transparent, illustrative executive allocation exercise.
Impact values are hypotheses, not causal estimates or forecast adjustments.
"""
from itertools import combinations
import json
from generate_data import ROOT
from forecast_risk import analyze
from sales_planning import read_csv

INITIATIVES = [
 {'id':'deal_desk','name':'Deal desk process redesign','cost_usd':180000,'impact_low_usd':120000,'impact_high_usd':560000,'owner':'Legal / Revenue Operations','risk':'Contract cycle changes may not accelerate signed bookings','weeks':8},
 {'id':'pipeline_hygiene','name':'Pipeline quality and forecast review','cost_usd':90000,'impact_low_usd':0,'impact_high_usd':240000,'owner':'Sales Operations','risk':'Improves forecast quality; incremental bookings are not guaranteed','weeks':4},
 {'id':'seller_enablement','name':'Seller enablement pilot','cost_usd':140000,'impact_low_usd':50000,'impact_high_usd':420000,'owner':'Sales Enablement','risk':'Adoption and productivity effects are uncertain','weeks':10},
 {'id':'territory_review','name':'Territory and quota fairness review','cost_usd':110000,'impact_low_usd':0,'impact_high_usd':300000,'owner':'Sales Finance','risk':'Redistribution may shift credit rather than create bookings','weeks':6},
 {'id':'approval_automation','name':'Approval workflow automation pilot','cost_usd':220000,'impact_low_usd':70000,'impact_high_usd':650000,'owner':'Product / Legal','risk':'Integration and policy approvals may delay implementation','weeks':12},
]

def optimize(budget_usd=350000, initiatives=None, risk_weight=.5):
    """Rank affordable portfolios by assumed risk-weighted incremental bookings.
    No causal inference; assumes additive independent effects for demonstration.
    """
    if budget_usd < 0 or not 0 <= risk_weight <= 1: raise ValueError('Invalid budget or risk weight')
    initiatives = INITIATIVES if initiatives is None else initiatives
    ids=[i['id'] for i in initiatives]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate initiative IDs')
    for i in initiatives:
        if i['cost_usd'] < 0 or i['impact_low_usd'] > i['impact_high_usd'] or i['impact_low_usd'] < 0:
            raise ValueError('Invalid initiative assumptions')
    options=[]
    for k in range(len(initiatives)+1):
        for group in combinations(initiatives,k):
            cost=sum(x['cost_usd'] for x in group)
            if cost>budget_usd: continue
            low=sum(x['impact_low_usd'] for x in group)
            high=sum(x['impact_high_usd'] for x in group)
            score=risk_weight*low+(1-risk_weight)*high
            options.append({'initiative_ids':[x['id'] for x in group], 'cost_usd':cost,
                            'unallocated_usd':budget_usd-cost,'assumed_low_impact_usd':low,
                            'assumed_high_impact_usd':high,'illustrative_score_usd':round(score,2)})
    options.sort(key=lambda x:(-x['illustrative_score_usd'],x['cost_usd'],x['initiative_ids']))
    return {'budget_usd':budget_usd,'risk_weight':risk_weight,'recommended':options[0],
            'alternatives':options[1:6], 'eligible_portfolios':len(options),
            'assumptions':'Illustrative additive impacts; no observed causal uplift, no implementation dependency constraints.'}

def board_pack(opportunities, budget_usd=350000, risk_weight=.5):
    risk=analyze(opportunities)
    allocation=optimize(budget_usd,risk_weight=risk_weight)
    return {'metadata':{'scenario':'Fictional 2026-Q4 executive allocation exercise','synthetic':True,
                        'decision_status':'Proposal only','external_actions':False},
            'forecast_sensitivity':risk['results'],'allocation':allocation,
            'decision_request':'Select a pilot portfolio within the discretionary budget, conditional on finance/legal validation.',
            'approval_gates':['Validate actual contract and pipeline data','Finance confirms incremental budget and cost accounting',
                              'Legal/compliance approves relevant workflow changes','Assign owners, measurable leading indicators and stop/go criteria'],
            'measurement_plan':{'baseline':'Capture historical approval times, forecast error, adoption and conversion by cohort',
                                'pilot':'Use phased rollout and comparison cohorts where feasible',
                                'review':'Evaluate measured outcomes at 30/60/90 days; do not attribute all movement to interventions'},
            'limitations':['Hypothetical impact bands are not estimates derived from CRM data',
                           'Effects are assumed additive; overlapping initiatives could double count benefits',
                           'Sensitivity forecasts are not calibrated or validated',
                           'Selection is a decision aid, not an automatically approved investment']}

def run():
    rows=read_csv(ROOT/'data/opportunities.csv')
    pack=board_pack(rows)
    (ROOT/'outputs'/'executive_simulation.json').write_text(json.dumps(pack,indent=2))
    return pack

if __name__=='__main__':
    print(json.dumps(run()['allocation']['recommended'],indent=2))
