import unittest
from codepyheat.porousMedia import PropPorousMedia


class Test(unittest.TestCase):

    def testInitPropPorMedia(self):
        p = PropPorousMedia.fromJsonFile("unittests/UnittestParamColumn.json")
        # p.initProps("unittests/UnittestParamColumn.json")
        self.assertEqual(p.getUpperK(), 1e-5)
        self.assertEqual(p.getPorosity(), 0.15)
        self.assertEqual(p.getLambda(), 2)
        self.assertEqual(p.getHeatCapa(), 957)
        self.assertEqual(p.getRho(), 2600)
        self.assertEqual(p.getNameM(), "Soil Column")

    def testParamEff(self):
        p = PropPorousMedia.fromJsonFile("unittests/UnittestParamColumn.json")
        p.setEffectiveParams() # TODO later
        



if __name__ == '__main__':
    unittest.main()