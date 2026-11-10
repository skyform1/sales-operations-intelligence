import sys, unittest, tempfile
from unittest.mock import patch
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generate_data import generate, ROOT
from sales_planning import read_csv
from quality import audit

class QualityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root_patch = patch("generate_data.ROOT", Path(self.tmp.name))
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_clean_generated_data(self):
        generate(seed=42,count=2400)
        result=audit(read_csv(Path(self.tmp.name)/'data'/'sellers.csv'),read_csv(Path(self.tmp.name)/'data'/'opportunities.csv'))
        self.assertTrue(result['passed'],result['issues'])
        self.assertLess(result['actual_attainment_pct'],150)
    def test_orphan_detection(self):
        generate(seed=42,count=10)
        sellers=read_csv(Path(self.tmp.name)/'data'/'sellers.csv')
        opps=read_csv(Path(self.tmp.name)/'data'/'opportunities.csv')
        opps[0]['seller_id']='UNKNOWN'
        self.assertFalse(audit(sellers,opps)['passed'])
    def test_duplicate_detection(self):
        generate(seed=42,count=10)
        sellers=read_csv(Path(self.tmp.name)/'data'/'sellers.csv')
        opps=read_csv(Path(self.tmp.name)/'data'/'opportunities.csv')
        self.assertFalse(audit(sellers,opps+[opps[0]])['passed'])
