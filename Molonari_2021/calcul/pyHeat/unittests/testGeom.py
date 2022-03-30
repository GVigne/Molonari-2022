import unittest

from codepyheat.geometry import Point, Geometry, Face, Cell, Column
from codepyheat import X, Z, ONE, TWO
from codepyheat.units import unitL

CODE_HYD = -9999
CODE_HEAT = -3333

test_dict = {"depth": {"val": 80, "unit": "cm"}, "ncells": 2}


class Test(unittest.TestCase):

    def testColumnInit(self):
        """
            call different class methods to provide input to
            Column __init__ method

            .fromJsonString(a_json_string)    json string
            .fromFile(json_file)            full path
            .fromDict(a_dict)               just the dict

        """
        # test fromJsonFile
        # bogus file
        self.assertRaises(
            FileNotFoundError,
            Column.fromJsonFile,
            'humpsdibumsdy.json')
        # bogus file content
        self.assertRaises(
            ValueError,
            Column.fromJsonFile,
            'unittests/bad_json_file.json')
        # do we get a Column object if things go well
        self.assertEqual(
            str(type(Column.fromJsonFile("unittests/UnittestColumn.json"))),
            "<class 'codepyheat.geometry.Column'>")
        with open("unittests/UnittestColumn.json") as a_file:
            json_string = a_file.read()
        self.assertEqual(
            str(type(Column.fromJsonString(json_string))),
            "<class 'codepyheat.geometry.Column'>")
        self.assertEqual(
            str(type(Column.fromDict(test_dict))),
            "<class 'codepyheat.geometry.Column'>")

    def testInitPoint(self):
        p = Point(0.456, 8)
        self.assertEqual(p.x, 0.456)
        self.assertEqual(p.z, 8)

    def testInitGeometry(self):
        geom = Geometry(Point(0.456, 8), (0.2, 1))
        self.assertEqual(geom.center.x, 0.456)
        self.assertEqual(geom.center.z, 8)
        self.assertEqual(geom.lenTuple[X],0.2)
        self.assertEqual(geom.lenTuple[Z],1)
        self.assertEqual(type(geom.lenTuple),tuple)

    def testGetGeometryArea(self):
        geom = Geometry(Point(0.456, 8), (0.2, 1))
        self.assertEqual(geom.getArea(), 0.2)

    def testUnitL(self):
        self.assertEqual(unitL('mm'), 0.001)
        self.assertEqual(unitL('cm'), 0.01)
        self.assertEqual(unitL('m'), 1)
        self.assertEqual(unitL('whatever'), 1)

    def testInitFace(self):
        face = Face('345E', 1, 10)
        self.assertEqual(face.len, 1)
        self.assertEqual(face.id, '345E')
        self.assertEqual(face.dist, 10)
        self.assertEqual(face.hydro.h, CODE_HYD)
        self.assertEqual(face.hydro.upperU, CODE_HYD)
        self.assertEqual(face.hydro.u, CODE_HYD)
        self.assertEqual(face.hydro.upperQ, CODE_HYD)
        self.assertEqual(face.hydro.type, 'regular')
        self.assertEqual(face.heat.upperT, CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux, CODE_HEAT)
        self.assertEqual(face.heat.heatFlux, CODE_HEAT)
        self.assertEqual(face.heat.type, 'regular')

    def testInitCell(self):
        cell = Cell(214, Point(1, 2), (0.2, 1))
        self.assertEqual(cell.id,214)
        self.assertEqual(cell.geom.center.x,1)
        self.assertEqual(cell.geom.center.z,2)
        self.assertEqual(cell.geom.lenTuple[X],0.2)
        self.assertEqual(cell.geom.lenTuple[Z],1)
        face=cell.face[X][ONE]
        self.assertEqual(face.len,1)
        self.assertEqual(face.dist,0.2)
        self.assertEqual(face.id,'214XW')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[X][TWO]
        self.assertEqual(face.len,1)
        self.assertEqual(face.dist,0.2)
        self.assertEqual(face.id,'214XE')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][ONE]
        self.assertEqual(face.len,0.2)
        self.assertEqual(face.dist,1)
        self.assertEqual(face.id,'214ZS')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][TWO]
        self.assertEqual(face.len,0.2)
        self.assertEqual(face.dist,1)
        self.assertEqual(face.id,'214ZN')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        self.assertEqual(cell.hydro.h,CODE_HYD)
        self.assertEqual(cell.hydro.upperU,CODE_HYD)
        self.assertEqual(cell.hydro.u,CODE_HYD)
        self.assertEqual(cell.hydro.upperQ,CODE_HYD)
        self.assertEqual(cell.hydro.type,'regular')

    def testInitColumn(self):
        col = Column.fromJsonFile("unittests/UnittestColumn.json")
        self.assertEqual(col.depth,0.8)
        self.assertEqual(col.ncells,2)
        self.assertEqual(col.dh,CODE_HYD)
        self.assertEqual(col.tempRiv,CODE_HEAT)
        self.assertEqual(col.tempAq,CODE_HEAT)
        ls=col.ls
        for i in range(col.ncells):
            self.assertEqual(ls.x[i],0)
            self.assertEqual(ls.rhs[i],0)
            for j in range(col.ncells):
                self.assertEqual(ls.lhs[i][j],0)
        cell=col.cell[0]
        self.assertEqual(cell.id,0)
        self.assertEqual(cell.geom.center.x,0.2)
        self.assertAlmostEqual(cell.geom.center.z,0.6)
        self.assertEqual(cell.geom.lenTuple[X],0.4)
        self.assertEqual(cell.geom.lenTuple[Z],0.4)
        self.assertEqual(cell.hydro.h,CODE_HYD)
        self.assertEqual(cell.hydro.upperU,CODE_HYD)
        self.assertEqual(cell.hydro.u,CODE_HYD)
        self.assertEqual(cell.hydro.upperQ,CODE_HYD)
        self.assertEqual(cell.hydro.type,'regular')
        face=cell.face[X][ONE]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'0XW')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[X][TWO]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'0XE')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][ONE]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'0ZS')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][TWO]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'0ZN')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        cell=col.cell[1]
        self.assertEqual(cell.id,1)
        self.assertEqual(cell.geom.center.x,0.2)
        self.assertAlmostEqual(cell.geom.center.z,0.2)
        self.assertEqual(cell.geom.lenTuple[X],0.4)
        self.assertEqual(cell.geom.lenTuple[Z],0.4)
        self.assertEqual(cell.hydro.h,CODE_HYD)
        self.assertEqual(cell.hydro.upperU,CODE_HYD)
        self.assertEqual(cell.hydro.u,CODE_HYD)
        self.assertEqual(cell.hydro.upperQ,CODE_HYD)
        self.assertEqual(cell.hydro.type,'regular')
        face=cell.face[X][ONE]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'1XW')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[X][TWO]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'1XE')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][ONE]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'1ZS')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')
        face=cell.face[Z][TWO]
        self.assertEqual(face.len,0.4)
        self.assertEqual(face.dist,0.4)
        self.assertEqual(face.id,'1ZN')
        self.assertEqual(face.heat.upperT,CODE_HEAT)
        self.assertEqual(face.heat.speciHeatFlux,CODE_HEAT)
        self.assertEqual(face.heat.heatFlux,CODE_HEAT)
        self.assertEqual(face.heat.type,'regular')

    def testInitColumnHydrostatic(self):
        col = Column.fromJsonFile("unittests/UnittestColumn.json")
        col.initColumnHydrostatique(12)
        self.assertEqual(col.cell[0].hydro.h,12)
        self.assertEqual(col.cell[0].face[X][0].hydro.h,CODE_HYD)
        self.assertEqual(col.cell[0].face[X][1].hydro.h,CODE_HYD)
        self.assertEqual(col.cell[0].face[Z][0].hydro.h,12)
        self.assertEqual(col.cell[0].face[Z][1].hydro.h,12)
        self.assertEqual(col.cell[1].hydro.h,12)
        self.assertEqual(col.cell[1].face[X][0].hydro.h,CODE_HYD)
        self.assertEqual(col.cell[1].face[X][1].hydro.h,CODE_HYD)
        self.assertEqual(col.cell[1].face[Z][0].hydro.h,12)
        self.assertEqual(col.cell[1].face[Z][1].hydro.h,12)

    def testSetBcHyd(self):
        col = Column.fromJsonFile("unittests/UnittestColumn.json") 
        col.setBcHyd("unittests/UnittestBcHydro.json")
        self.assertEqual(col.dh,0.15)
        h=col.cell[0].hydro
        self.assertEqual(h.type,'BcDirichlet, face -> ZS')
        h=col.cell[0].face[Z][ONE].hydro
        self.assertEqual(h.type,'BcDirichlet')
        self.assertEqual(h.h,0.15)
        h=col.cell[1].face[Z][TWO].hydro
        self.assertEqual(h.type,'BcDirichlet')
        self.assertEqual(h.h,0)

    def testSetBcHeat(self):
        col = Column.fromJsonFile("unittests/UnittestColumn.json") 
        col.setBcT("unittests/UnittestBcTemp.json")
        self.assertEqual(col.tempRiv,273.15+29)
        self.assertEqual(col.tempAq,12)
        h=col.cell[0].heat
        self.assertEqual(h.type,'BcDirichlet, face -> ZS')
        h=col.cell[0].face[Z][ONE].heat
        self.assertEqual(h.type,'BcDirichlet')
        self.assertEqual(h.upperT,273.15+29)
        h=col.cell[1].face[Z][TWO].heat
        self.assertEqual(h.type,'BcDirichlet')
        self.assertEqual(h.upperT,12)

if __name__ == '__main__':
    unittest.main()