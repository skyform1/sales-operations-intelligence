import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sales_planning import allocate_quotas, performance, commission, summarize

class SalesPlanningTests(unittest.TestCase):
    def setUp(self):
        self.sellers = [{'seller_id':'S1','region':'EMEA'}, {'seller_id':'S2','region':'LATAM'}]
    def test_allocation_reconciles(self):
        planned = allocate_quotas(self.sellers, target=1000000)
        self.assertAlmostEqual(sum(s['planned_quota_usd'] for s in planned), 1000000)
        self.assertGreater(planned[0]['planned_quota_usd'], planned[1]['planned_quota_usd'])
    def test_commission_accelerator(self):
        self.assertEqual(commission(150,100),14.0)
        self.assertEqual(commission(100,100),8.0)
        self.assertEqual(commission(50,100),4.0)
    def test_forecast_not_paid(self):
        opportunities = [dict(seller_id='S1', status='Open', stage='Negotiation', amount_usd='1000', expected_close_date='2026-12-01'),
                         dict(seller_id='S1', status='Won', amount_usd='100', actual_close_date='2026-11-01')]
        planned = allocate_quotas(self.sellers, target=1000)
        result = performance(self.sellers, opportunities, planned)[0]
        self.assertEqual(result['actual_bookings_usd'], 100)
        self.assertEqual(result['projected_bookings_usd'], 850)
        self.assertEqual(commission(result['actual_bookings_usd'], result['planned_quota_usd']), 8.0)
    def test_out_of_quarter_excluded(self):
        opportunities = [dict(seller_id='S1',status='Won',amount_usd='100',actual_close_date='2027-01-01')]
        self.assertEqual(performance(self.sellers, opportunities, allocate_quotas(self.sellers))[0]['actual_bookings_usd'], 0)
    def test_invalid_quota(self):
        with self.assertRaises(ValueError): commission(100,0)

if __name__ == '__main__': unittest.main()
