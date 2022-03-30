import unittest
from codepyheat.units import calcValMult,calcValAdd
import json

class Test(unittest.TestCase):

    def testCalcValMult(self):
        with open("unittests/UnittestParamHyd.json") as jf:
            params = json.load(jf)
        jf.close()
        self.assertAlmostEqual(calcValMult(params['hydro']['permeability'],"permeability"),5e-6)
        with open("unittests/UnittestParamSed.json") as jf2:
            params = json.load(jf2)
        jf2.close()
        self.assertAlmostEqual(calcValMult(params['sediment']['rho'],"rho"),3e-3)
        self.assertAlmostEqual(calcValMult(params['sediment']['lambda'],"lambda"),2)
        self.assertAlmostEqual(calcValMult(params['sediment']['specificHeatCapacity'],"specificHeatCapacity"),957)
        with open("unittests/UnittestBcTemp.json") as jf2:
            params = json.load(jf2)
        self.assertAlmostEqual(calcValAdd(params['Triv'],"Triv"),302.15)
        self.assertAlmostEqual(calcValAdd(params['Taq'],"Taq"),12)


if __name__ == '__main__':
    unittest.main()