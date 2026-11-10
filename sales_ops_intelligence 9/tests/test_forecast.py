import sys, unittest, tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from forecast import forecast
from generate_data import generate

class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root_patch = patch("generate_data.ROOT", Path(self.tmp.name))
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_closed_won_and_weighted_open(self):
        rows = [
            dict(region='EMEA', status='Won', amount_usd='100', actual_close_date='2026-11-01'),
            dict(region='EMEA', status='Open', amount_usd='200', stage='Proposal', expected_close_date='2026-12-01'),
            dict(region='EMEA', status='Lost', amount_usd='900'),
            dict(region='EMEA', status='Won', amount_usd='500', actual_close_date='2027-01-01')]
        self.assertEqual(forecast(rows)['EMEA']['forecast_bookings_usd'], 200)
    def test_reproducible_generation(self):
        self.assertEqual(generate(seed=42, count=5), generate(seed=42, count=5))
    def test_all_regions(self):
        rows = generate(seed=42, count=2400)
        self.assertEqual(len(forecast(rows)), 4)

if __name__ == '__main__': unittest.main()
