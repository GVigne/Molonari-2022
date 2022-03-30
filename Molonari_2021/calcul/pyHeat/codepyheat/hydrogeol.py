"""
    @author: Nicolas Flipo
    @date: 10.02.2021

    Contains 3 Classes related to hydraulics in porous media:
    Hydro which contains hydraulic head, Darcy velocity, pore velocity
        and discharge
    PropHydro which contains permeability and porosity
    BoundaryConditionHydro which contains the head difference

"""

from codepyheat.factory import FactoryClass
from codepyheat.units import calcValMult
from codepyheat import printDir, printDirCard, caracParamTemplate, PERMEABILITY, POROSITY, CODE_HYD





class Hydro:
    def __init__(self):
        self.h = CODE_HYD
        self.upperU = CODE_HYD
        self.u = CODE_HYD
        self.upperQ = CODE_HYD
        self.type = 'regular'

    def setHydHead(self, H):
        self.h = H  # hydraulic head in [m]

    def setDarcyVel(self, upperU):
        self.upperU = upperU  # Darcy Velocity

    def setVel(self, upperU, n):
        self.u = upperU / n    # Real Velocity

    def setDischargeUS(self, upperU, surf):
        self.upperQ = upperU * surf   # discharge

    def setDischargeQ(self, upperQ):
        self.upperQ = upperQ  # discharge

    def setDirichletCell(self, dir, num):
        self.type = "BcDirichlet, face -> {}{}".format(
                printDir(dir), printDirCard(dir, num)
            )

    def setDirichletFace(self, H):
        self.type = 'BcDirichlet'
        self.h = H

    def calcU(self, gradH, upperK):
        self.upperU = -upperK*gradH


class PropHydro(FactoryClass):
    """
        instantiate with
            - PropHydro(a_dict)
            - PropHydro.fromJsonFile(full path and file name)
            - PropHydro.fromJsonString(valid json string)

    """
    nameH = 'Unknown'
    upperK = PERMEABILITY
    n = POROSITY

    def __init__(self, propH):
        self.upperK = calcValMult(propH['hydro']
                                  ['permeability'], "permeability"
                                  )
        self.n = calcValMult(propH['hydro']['porosity'], "porosity")

    def setPermeability(self, upperK):
        self.upperK = upperK

    def getPermeability(self):
        return self.upperK

    def setPorosity(self, n):
        self.n = n

    def getPorosity(self):
        return self.n

    def setNameH(self, name):
        self.nameH = name

    def getNameH(self):
        return self.nameH

    def printProp(self):
        print("\tHydraulic Properties of porous media", self.nameH)
        print(caracParamTemplate.format('\t\tpermeability or hydraulic conductivity', self.upperK, 'm s-1'))
        print(caracParamTemplate.format('\t\tporosity', self.n, '--'))


class BoundaryConditionHyd(FactoryClass):
    """
        instantiate with
            - BoundaryConditionHyd(a_dict)
            - BoundaryConditionHyd.fromJsonFile(full path and file name)
            - BoundaryConditionHyd.fromJsonString(valid json string)

    """
    def __init__(self, bcs):
        self.dh = calcValMult(bcs['dH'], "dH")
