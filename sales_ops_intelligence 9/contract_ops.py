"""Synthetic contracting and seller-operations workflow; not legal advice."""
import csv
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from generate_data import ROOT
from sales_planning import read_csv

THRESHOLDS = {'standard_discount_max': 0.10, 'manager_discount_max': 0.20, 'legal_value_threshold': 200000}

def generate_contracts(opportunities):
    """Deterministic contract scenarios for won and open deals; no random state."""
    contracts=[]
    for o in opportunities:
        if o['status'] not in ('Won','Open') or o['stage'] not in ('Proposal','Negotiation','Closed Won'):
            continue
        n=int(o['opportunity_id'][1:]); amount=float(o['amount_usd'])
        discount=[0,0.05,0.12,0.18,0.25][n%5]
        exception=(n%11==0)
        initiated=date(2026,10,1)+timedelta(days=n%75)
        days=[2,5,9,16,28][n%5]+(8 if exception else 0)
        state='Signed' if o['status']=='Won' else ('Blocked' if exception else 'In Review')
        contracts.append({'contract_id':f'C{n:05d}','opportunity_id':o['opportunity_id'], 'seller_id':o['seller_id'], 'region':o['region'],
          'deal_value_usd':amount,'discount_pct':discount*100,'nonstandard_terms':exception,
          'submitted_date':initiated.isoformat(),'review_days':days,'status':state,
          'legal_required':exception or amount>=THRESHOLDS['legal_value_threshold'],
          'finance_required':discount>THRESHOLDS['manager_discount_max'],
          'manager_required':discount>THRESHOLDS['standard_discount_max']})
    return contracts

def route_approval(contract):
    steps=[]
    if contract['manager_required']: steps.append('Sales Manager')
    if contract['finance_required']: steps.append('Finance')
    if contract['legal_required']: steps.append('Legal')
    return steps or ['Standard automated review']

def analyze_contracts(contracts):
    if not contracts: return {'count':0,'avg_review_days':0,'delayed_count':0,'blocked_count':0,'approval_queue':{},'regional':{}}
    regions=defaultdict(list); queues=defaultdict(int)
    for c in contracts:
        regions[c['region']].append(c)
        if c['status']!='Signed':
            for step in route_approval(c): queues[step]+=1
    return {'count':len(contracts),'avg_review_days':round(sum(c['review_days'] for c in contracts)/len(contracts),2),
            'delayed_count':sum(c['review_days']>14 for c in contracts),
            'blocked_count':sum(c['status']=='Blocked' for c in contracts),
            'approval_queue':dict(sorted(queues.items())),
            'regional':{r:{'contracts':len(rows),'avg_review_days':round(sum(x['review_days'] for x in rows)/len(rows),2),
                          'delayed_pct':round(100*sum(x['review_days']>14 for x in rows)/len(rows),2)} for r,rows in sorted(regions.items())}}

def seller_productivity(opportunities,contracts):
    sellers=defaultdict(lambda:{'opportunities':0,'won':0,'open':0,'contract_reviews':0,'delayed_contracts':0})
    for o in opportunities:
        row=sellers[o['seller_id']]; row['opportunities']+=1
        if o['status']=='Won':row['won']+=1
        if o['status']=='Open':row['open']+=1
    for c in contracts:
        row=sellers[c['seller_id']];row['contract_reviews']+=1
        if c['review_days']>14:row['delayed_contracts']+=1
    return [{'seller_id':sid,**r,'win_rate_closed_pct':round(100*r['won']/max(1,r['won']+r['opportunities']-r['won']-r['open']),2),
             'delayed_contract_pct':round(100*r['delayed_contracts']/max(1,r['contract_reviews']),2)} for sid,r in sorted(sellers.items())]

def run():
    opportunities=read_csv(ROOT/'data/opportunities.csv')
    contracts=generate_contracts(opportunities)
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    with (out/'contracts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(contracts[0]));w.writeheader();w.writerows(contracts)
    with (out/'seller_productivity.csv').open('w',newline='') as f:
        rows=seller_productivity(opportunities,contracts);w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary=analyze_contracts(contracts)
    (out/'contract_ops.json').write_text(json.dumps({'assumptions':THRESHOLDS,'summary':summary},indent=2))
    return summary
if __name__=='__main__':print(json.dumps(run(),indent=2))
