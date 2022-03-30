import unittest
import sys
sys.path.insert(0,'..')

from codepyheat.linearAlgebra import LinSys
NDIM = 2
CODE_HYD=-9999
class Test(unittest.TestCase):

    def testInitLinSys(self):
        ls=LinSys(NDIM)
        for i in range(NDIM):
            self.assertEqual(ls.x[i],0)
            self.assertEqual(ls.rhs[i],0)
            for j in range(NDIM):
                self.assertEqual(ls.lhs[i][j],0)

    def testSetLHSVal(self):
        ls=LinSys(NDIM)
        ls.setLhsVal(0,1,4.5)
        ls.setLhsVal(1,1,CODE_HYD)
        self.assertEqual(ls.lhs[0][0],0)
        self.assertEqual(ls.lhs[0][1],4.5)
        self.assertEqual(ls.lhs[1][0],0)
        self.assertEqual(ls.lhs[1][1],0)

    def testSetRHSVal(self):
        ls=LinSys(NDIM)
        ls.setRhsVal(0,1e-6)
        self.assertEqual(ls.rhs[0],1e-6)
        self.assertEqual(ls.rhs[1],0)

    def testSolve(self):
        ls=LinSys(NDIM)
        ls.setRhsVal(0,1e-6)
        ls.setRhsVal(1,2e-6)
        ls.setLhsVal(0,0,0.5)
        ls.setLhsVal(1,1,4)
        ls.solveSysLin()
        self.assertAlmostEqual(ls.x[0],2e-6)
        self.assertAlmostEqual(ls.x[1],5e-7)


if __name__ == '__main__':
    unittest.main()