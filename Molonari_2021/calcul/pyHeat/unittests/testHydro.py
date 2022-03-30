import unittest
from codepyheat.hydrogeol import Hydro, PropHydro, BoundaryConditionHyd, CODE_HYD


class Test(unittest.TestCase):

    def testInitH(self):
        hydro = Hydro()
        self.assertEqual(hydro.h,CODE_HYD)
        self.assertEqual(hydro.upperU,CODE_HYD)
        self.assertEqual(hydro.u,CODE_HYD)
        self.assertEqual(hydro.type,"regular")
        self.assertAlmostEqual(hydro.upperQ,CODE_HYD) 

    def testSetH(self):
        hydro = Hydro()
        hydro.setHydHead(100)
        self.assertEqual(hydro.h,100)

    def testSetDarcyVel(self):
        hydro = Hydro()
        hydro.setDarcyVel(1e-6)
        self.assertAlmostEqual(hydro.upperU,1e-6)

    def testSetVel(self):
        hydro = Hydro()
        hydro.setVel(1e-6,0.1)
        self.assertAlmostEqual(hydro.u,1e-5)

    def testSetDischargeUS(self):
        hydro = Hydro()
        hydro.setDischargeUS(1e-6,1e4)
        self.assertAlmostEqual(hydro.upperQ,1e-2)

    def testSetDischarge(self):
        hydro = Hydro()
        hydro.setDischargeQ(0.0089)
        self.assertAlmostEqual(hydro.upperQ,0.0089)

    def testSetDirichlet(self):
        hydro = Hydro()
        hydro.setDirichletFace(0.15)
        self.assertEqual(hydro.h,0.15)
        self.assertEqual(hydro.type,'BcDirichlet')
        hydro.setDirichletCell(1,0)
        self.assertEqual(hydro.type,'BcDirichlet, face -> ZS')

    def testCalcQ(self):
        hydro = Hydro()
        hydro.calcU(-0.5, 2e-7)
        self.assertAlmostEqual(hydro.upperU,1e-7)


    def testSetPermeability(self):
        prop = PropHydro.fromJsonFile('unittests/UnittestParamHyd.json')
        prop.setPermeability(4.5e-6)
        self.assertEqual(prop.upperK,4.5e-6)

    def testSetPorosity(self):
        prop = PropHydro.fromJsonFile('unittests/UnittestParamHyd.json')
        prop.setPorosity(0.5)
        self.assertEqual(prop.n,0.5)

    def testInitBc(self):
        bc = BoundaryConditionHyd.fromJsonFile(
            "unittests/UnittestBcHydro.json"
            )
        self.assertEqual(bc.dh, 0.15)

    def testInitProp(self):
        prop = PropHydro.fromJsonFile('unittests/UnittestParamHyd.json')
        self.assertEqual(prop.upperK, 5e-6)
        self.assertEqual(prop.n, 0.12)


if __name__ == '__main__':
    unittest.main()
