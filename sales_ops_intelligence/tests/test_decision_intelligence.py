import unittest
from decision_intelligence import decision_brief, approval_record, scenario_comparison

SELLERS=[{'seller_id':'S1','region':'EMEA','capacity_fte':'1'}]
OPPS=[{'opportunity_id':'O00001','seller_id':'S1','region':'EMEA','status':'Won','stage':'Closed Won','amount_usd':'100', 'actual_close_date':'2026-10-15','expected_close_date':'2026-10-15'},
      {'opportunity_id':'O00002','seller_id':'S1','region':'EMEA','status':'Open','stage':'Proposal','amount_usd':'100', 'actual_close_date':'','expected_close_date':'2026-11-15'}]

class DecisionTests(unittest.TestCase):
    def test_forecast_separates_actual_and_projected(self):
        b=decision_brief(SELLERS,OPPS,contracts=[],target=1000)
        self.assertEqual(b['kpis']['closed_won_bookings_usd'],100)
        self.assertGreater(b['kpis']['projected_bookings_usd'],100)
        self.assertEqual(b['kpis']['pending_contracts'],0)
    def test_shortfall_recommendation_evidence(self):
        b=decision_brief(SELLERS,OPPS,contracts=[],target=1000)
        r=next(x for x in b['recommendations'] if x['id']=='REV-001')
        self.assertAlmostEqual(r['evidence']['shortfall_usd'],1000-b['kpis']['projected_bookings_usd'])
    def test_delayed_unsigned_only(self):
        c=[{'status':'In Review','review_days':20,'deal_value_usd':200,'region':'EMEA','manager_required':False,'finance_required':False,'legal_required':False},
           {'status':'Signed','review_days':30,'deal_value_usd':400,'region':'EMEA'}]
        b=decision_brief(SELLERS,OPPS,contracts=c,target=1000)
        self.assertEqual(b['kpis']['delayed_unsigned_contracts'],1)
        self.assertEqual(next(r for r in b['recommendations'] if r['id']=='CTR-001')['evidence']['delayed_unsigned_value_usd'],200)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):decision_brief(SELLERS,OPPS,target=0)
        with self.assertRaises(ValueError):decision_brief(SELLERS,OPPS,target=1000,commission_rate=-1)
    def test_approval_requires_human_reason(self):
        with self.assertRaises(ValueError):approval_record('REV-001','Rejected','','no',['REV-001'])
        with self.assertRaises(ValueError):approval_record('REV-999','Rejected','Analyst','No',['REV-001'])
        r=approval_record('REV-001','Needs evidence','Analyst','Recheck probabilities',['REV-001'])
        self.assertFalse(r['executed'])
    def test_scenario_tradeoffs(self):
        rows=scenario_comparison(SELLERS,OPPS,contracts=[],target=100)
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]['projected_usd'],rows[1]['projected_usd'])
        self.assertLess(rows[1]['projected_attainment_pct'],rows[0]['projected_attainment_pct'])
        self.assertLessEqual(rows[2]['commission_expense_usd'],rows[3]['commission_expense_usd'])

if __name__=='__main__':unittest.main()
