import unittest
from contract_ops import generate_contracts,route_approval,analyze_contracts,seller_productivity
class ContractTests(unittest.TestCase):
    def test_routing(self):
        c={'manager_required':True,'finance_required':True,'legal_required':True}
        self.assertEqual(route_approval(c),['Sales Manager','Finance','Legal'])
    def test_standard(self):
        self.assertEqual(route_approval({'manager_required':False,'finance_required':False,'legal_required':False}),['Standard automated review'])
    def test_deterministic(self):
        opp=[{'opportunity_id':'O00011','seller_id':'S001','region':'EMEA','amount_usd':'300000','status':'Open','stage':'Negotiation'}]
        a=generate_contracts(opp)
        self.assertEqual(a,generate_contracts(opp))
        self.assertTrue(a[0]['legal_required'])
        self.assertEqual(a[0]['status'],'Blocked')
    def test_summary(self):
        self.assertEqual(analyze_contracts([])['count'],0)
    def test_productivity(self):
        opp=[{'seller_id':'S001','status':'Won'},{'seller_id':'S001','status':'Lost'},{'seller_id':'S001','status':'Open'}]
        rows=seller_productivity(opp,[])
        self.assertEqual(rows[0]['win_rate_closed_pct'],50)
if __name__=='__main__':unittest.main()
