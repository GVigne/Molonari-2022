import unittest

from codepyheat.heat import Heat, PropMedia, BoundaryConditionHeat
CODE_HEAT = -3333
ZCELSIUS = 273.15

class Test(unittest.TestCase):

    def testInitHeat(self):
        heat = Heat()
        self.assertEqual(heat.upperT, CODE_HEAT)
        self.assertEqual(heat.speciHeatFlux, CODE_HEAT)
        self.assertEqual(heat.heatFlux, CODE_HEAT)

    def testSetT(self):
        heat = Heat()
        heat.setT(273)
        self.assertEqual(heat.upperT, 273)

    def testSetSpeciHeatFlux(self):
        heat = Heat()
        heat.setT(10)
        heat.setSpeciHeatFlux(1e-6)
        self.assertAlmostEqual(heat.speciHeatFlux, 1e-5)

    def testSetHeatFluxFromQ(self):
        heat = Heat()
        heat.setT(10)
        heat.setHeatFluxFromQ(5e-3)
        self.assertAlmostEqual(heat.heatFlux, 5e-2)

    def testSetHeatFluxFromSurf(self):
        heat = Heat()
        heat.setT(10)
        heat.setSpeciHeatFlux(1e-6)
        heat.setHeatFluxFromSurf(300)
        self.assertAlmostEqual(heat.heatFlux, 3e-3)

    def testSetAllFlux(self):
        heat = Heat()
        heat.setT(10)
        heat.setAllFlux(1.5e-6, 300)
        self.assertAlmostEqual(heat.heatFlux, 4.5e-3)

    def testSetAll(self):
        heat = Heat()
        heat.setAll(10, 1.5e-7, 400)
        self.assertAlmostEqual(heat.heatFlux, 6e-4)

    def testSetDirichlet(self):
        h = Heat()
        h.setDirichletFace(0.15)
        self.assertEqual(h.upperT, 0.15)
        self.assertEqual(h.type, 'BcDirichlet')
        h.setDirichletCell(1, 0)
        self.assertEqual(h.type, 'BcDirichlet, face -> ZS')

    def testInitProp(self):
        p = PropMedia()
        self.assertAlmostEqual(p.lambd, 2)
        self.assertEqual(p.heatCapa, 1250)
        self.assertEqual(p.rho, 2500)

    def testSetL(self):
        p = PropMedia()
        p.setLambda(3)
        self.assertEqual(p.lambd, 3)
        self.assertEqual(p.heatCapa, 1250)
        self.assertEqual(p.rho, 2500)

    def testSetHC(self):
        p = PropMedia()
        p.setHeatCapa(2346)
        self.assertEqual(p.lambd,2)
        self.assertEqual(p.heatCapa,2346)
        self.assertEqual(p.rho,2500)

    def testSetRho(self):
        p = PropMedia()
        p.setRho(4567)
        self.assertEqual(p. lambd,2)
        self.assertEqual(p. heatCapa,1250)
        self.assertEqual(p. rho,4567)

    def testGetLbdEq(self):
        p = PropMedia()
        self.assertAlmostEqual(
            p.getLambdaEq(0.598, 0.2), 1.6538777117310037
            ) # using LAMBDAW = 0.598


    def testSetName(self):
        p = PropMedia()
        p.setNameM('Easy')
        self.assertEqual(p.nameM, 'Easy')


    def testInitBc(self):
        bc=BoundaryConditionHeat.fromJsonFile("unittests/UnittestBcTemp.json")
        self.assertEqual(bc.tempRiv, ZCELSIUS+29)
        self.assertEqual(bc.tempAq, 12)


if __name__ == '__main__':
    unittest.main()