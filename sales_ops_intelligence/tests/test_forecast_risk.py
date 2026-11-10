import unittest
from forecast_risk import analyze

def row(status,amount,stage='Qualified',when='2026-11-01'):
    return {'status':status,'amount_usd':str(amount),'stage':stage,
            'actual_close_date':when if status=='Won' else '',
            'expected_close_date':when if status=='Open' else ''}

class ForecastRiskTests(unittest.TestCase):
    def test_no_double_count_won(self):
        x=analyze([row('Won',100),row('Open',100)],target=100)
        self.assertEqual(x['results']['base']['closed_won_usd'],100)
        self.assertEqual(x['results']['base']['projected_bookings_usd'],112.75)
    def test_monotonic_scenarios(self):
        x=analyze([row('Open',1000)],target=500)['results']
        self.assertLessEqual(x['downside']['projected_bookings_usd'],x['base']['projected_bookings_usd'])
        self.assertLessEqual(x['base']['projected_bookings_usd'],x['upside']['projected_bookings_usd'])
    def test_outside_quarter_excluded(self):
        x=analyze([row('Won',100,when='2027-01-01')],target=100)
        self.assertEqual(x['results']['base']['projected_bookings_usd'],0)
    def test_invalid_assumptions(self):
        with self.assertRaises(ValueError): analyze([],scenarios={'bad':{'probability_multiplier':1.2,'in_quarter_close_rate':1}})
    def test_negative_amount(self):
        with self.assertRaises(ValueError): analyze([row('Open',-1)])
