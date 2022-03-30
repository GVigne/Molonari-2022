"""
    @author: Nicolas Flipo
    @date: 10.02.2021

    Contains 3 Classes related to heat :
    Heat which contains T, and fluxes
    PropMedia which contains the grain properties
    BoundaryConditionHeat which contains only Triv and Taq

"""

from codepyheat.factory import FactoryClass
from codepyheat.units import calcValMult, calcValAdd
from codepyheat import (printDir, printDirCard, caracParamTemplate, RHOS,
                        LAMBDAS, LAMBDAW, HEATCAPAS, CODE_HEAT, RHOW, HEATCAPAW,
                        POROSITY, weightedAveragePoro
                        )
import sys


class PropMedia(FactoryClass):
    """
        instantiate with
            - PropMedia(a_dict)
            - PropMedia.fromJsonFile(full path and file name)
            - PropMedia.fromJsonString(valid json string)

    """
    nameM = 'Undefined'
    lambd = LAMBDAS
    heatCapa = HEATCAPAS
    rho = RHOS

    def __init__(self, propM=None):
        if propM is not None:
            self.lambd = calcValMult(propM['sediment']['lambda'], "lambda")
            self.setHeatCapa(calcValMult(propM['sediment']
                                         ['specificHeatCapacity'],
                                         "specificHeatCapacity"
                                         )
                             )
            self.rho = calcValMult(propM['sediment']['rho'], "rho")

    def setLambda(self, lambd):
        self.lambd = lambd

    def getLambda(self):
        return self.lambd

    def setHeatCapa(self, heatCapa):
        self.heatCapa = heatCapa

    def getHeatCapa(self):
        return self.heatCapa

    def setRho(self, rho):
        self.rho = rho

    def getRho(self):
        return self.rho

    def setName(self, name):
        self.nameM = name

    def getName(self):
        return self.nameM

    def setAll(self, lambd, heatCapa, rho):
        self.lambd = lambd
        self.heatCapa = heatCapa
        self.rho = rho

    def getLambdaEq(self, lw=LAMBDAW, n=POROSITY):
        lambd = pow(
                (n * pow(lw, 0.5)+(1-n) * pow(self.lambd, 0.5)), 2
            )  # lw lambda water, n porosity
        return lambd

    def getHeatCapaEq(self, n):
        rhosCs = self.rho * self.heatCapa
        rhowCw = RHOW * HEATCAPAW
        rhomCm = weightedAveragePoro(rhowCw, rhosCs, n)
        return rhomCm

    def setNameM(self, name):
        self.nameM = name

    def getNameM(self):
        return self.nameM

    def printProp(self):
        print("\tThermal Properties of the phase (pure solid)", self.nameM)
        print(caracParamTemplate.format(
            '\t\tthermal conductivity:',
            self.lambd,
            'W m-1 K-1'))
        print(caracParamTemplate.format(
            '\t\tspecific heat capacity:',
            self.heatCapa,
            'm2 s-2 K-1'))
        print(caracParamTemplate.format('\t\tdensity:', self.rho, 'kg m-3'))


class Heat:
    def __init__(self):
        self.upperT = CODE_HEAT
        self.speciHeatFlux = CODE_HEAT
        self.heatFlux = CODE_HEAT
        self.speciAdv = CODE_HEAT
        self.speciCond = CODE_HEAT
        self.deltaT = CODE_HEAT
        self.deltaBil = CODE_HEAT
        self.type = 'regular'

    def setT(self, temperature):
        self.upperT = temperature

    def setSpeciHeatFlux(self, upperU):
        self.speciHeatFlux = self.upperT * upperU  # U in m.s-1

    def setHeatFluxFromQ(self, upperQ):
        self.heatFlux = self.upperT * upperQ  # Q in m3.s-1

    def setHeatFluxFromSurf(self, surf):
        self.heatFlux = self.speciHeatFlux * surf

    def setAllFlux(self, upperU, surf):
        self.setSpeciHeatFlux(upperU)
        self.setHeatFluxFromSurf(surf)

    def setAll(self, upperT, upperU, surf):
        self.setT(upperT)
        self.setSpeciHeatFlux(upperU)
        self.setHeatFluxFromSurf(surf)

    def setDirichletCell(self, dir, num):
        self.type = "BcDirichlet, face -> {}{}".format(
            printDir(dir),
            printDirCard(dir, num)
        )

    def setDirichletFace(self, upperT):
        self.type = 'BcDirichlet'
        self.upperT = upperT


class BoundaryConditionHeat(FactoryClass):
    """
        instantiate with
            - BoundaryConditionHeat(a_dict)
            - BoundaryConditionHeat.fromJsonFile(full path and file name)
            - BoundaryConditionHeat.fromJsonString(valid json string)

    """
    def __init__(self, bcs):
        # print('first level keys:',bcs.keys())
        # print('second level keys:',bcs['dH'].keys())
        self.tempRiv = calcValAdd(bcs['Triv'], "Triv")
        self.tempAq = calcValAdd(bcs['Taq'], "Taq")


class SinusFunction(FactoryClass):
    def __init__(self, bcs):
        self.ampli = calcValAdd(bcs['Tampli'], "Tampli")
        self.period = calcValMult(bcs['Period'], "Period")


class BoundConditionSinus(FactoryClass):
    def __init__(self, bcs):
        self.tempAv = calcValAdd(bcs['Taverage'], "Taverage")
        self.sinus.append(SinusFunction(bcs['sinus']))

class BoundConditionMultiSinus(FactoryClass):
    #sinus = []
    def __init__(self, bcs):
        self.sinus = []
        self.tempAv = calcValAdd(bcs['Taverage'], "Taverage")
        key = 'sinus'
        if key in bcs.keys():
            dTemp = bcs[key]
            for i in range(len(dTemp)):
                pt = dTemp[i]
                sinFun = SinusFunction(pt)
                self.sinus.append(sinFun)
        else :
            print('No temperature periodic signal specified. Impossible to proceed further')
            sys.exit()