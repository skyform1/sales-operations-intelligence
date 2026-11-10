import unittest
from executive_simulation import optimize, board_pack

class ExecutiveSimulationTests(unittest.TestCase):
    def test_budget_never_exceeded(self):
        for budget in (0,100000,350000,1000000):
            result=optimize(budget)
            self.assertLessEqual(result['recommended']['cost_usd'],budget)
            self.assertTrue(all(a['cost_usd']<=budget for a in result['alternatives']))
    def test_zero_budget(self):
        self.assertEqual(optimize(0)['recommended']['initiative_ids'],[])
    def test_risk_preferences_change_selection(self):
        a=optimize(350000,risk_weight=0)['recommended']
        b=optimize(350000,risk_weight=1)['recommended']
        self.assertNotEqual(a['illustrative_score_usd'],b['illustrative_score_usd'])
    def test_invalid_inputs(self):
        for kwargs in ({'budget_usd':-1},{'risk_weight':1.1},{'risk_weight':-.1}):
            with self.assertRaises(ValueError): optimize(**kwargs)
    def test_no_duplicated_ids(self):
        item={'id':'x','cost_usd':1,'impact_low_usd':0,'impact_high_usd':2}
        with self.assertRaises(ValueError): optimize(10,[item,item])
    def test_board_pack_flags_hypothetical(self):
        pack=board_pack([],350000)
        self.assertTrue(pack['metadata']['synthetic'])
        self.assertFalse(pack['metadata']['external_actions'])
        self.assertTrue(pack['approval_gates'])
        self.assertIn('downside',pack['forecast_sensitivity'])

if __name__=='__main__': unittest.main()
