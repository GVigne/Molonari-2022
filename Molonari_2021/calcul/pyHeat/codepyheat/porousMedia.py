"""
    @author: Nicolas Flipo
    @date: 10.02.2021

    Class PorousMedia is built upon the classes PropHydro in hydrogeol.py
        and PropMedia in heat.py
    It implements the calculation of effective and equivalent parameters
        for porous media

"""

from codepyheat.factory import FactoryClass
from codepyheat.hydrogeol import PropHydro
from codepyheat.heat import PropMedia, BoundConditionSinus
from codepyheat import (caracParamTemplate, RHOW, CODE_HYD,
                        LAMBDAW, HEATCAPAW, POROSITY, RHOS,
                        weightedAveragePoro, CODE_HEAT)
from codepyheat import JSONPATH
import sys
import os


class PropPorousMedia(FactoryClass):
    kappa = CODE_HYD

    def __init__(self, paths):
        if ('hydroFile' in paths):
            self.propH = PropHydro.fromJsonFile(JSONPATH + paths['hydroFile'])
        else:
            self.propH = PropHydro.fromDict(paths['hydroParam'])
        if ('sedFile' in paths):
            self.propM = PropMedia.fromJsonFile(JSONPATH + paths['sedFile'])
        else:
            self.propM = PropMedia.fromDict(paths['sedParam'])
        self.propM.nameM = paths['name']
        self.a = []  # NF for analytical solution
        self.b = []  # NF for analytical solution
        
    def printProps(self):
        self.propH.printProp()
        self.propM.printProp()
        self.printParamEq()
        self.printParamEffective()

    def setEffectiveParams(self):
        rhowCw = RHOW * HEATCAPAW
        rhomCm = self.propM.getHeatCapaEq(self.propH.n)
        self.kappa = (
            self.propM.getLambdaEq(LAMBDAW, self.propH.n)
            / (rhowCw)
        )
        self.alpha = (rhowCw / rhomCm * self.propH.upperK)

    def getKappa(self):
        # self.setEffectiveParams() # I don't think it is necessary
        return self.kappa

    def getAlpha(self):
        # self.setEffectiveParams() # I don't think it is necessary
        return self.alpha

    def setPermeability(self, upperK):
        return self.propH.setPermeability(upperK)

    def getUpperK(self):
        return self.propH.upperK

    def setPorosity(self, porosity):
        self.propH.setPorosity(porosity)

    def getPorosity(self):
        return self.propH.getPorosity()

    def setLambda(self, lambd):
        self.propM.setLambda(lambd)

    def getLambda(self):
        return self.propM.getLambda()

    def getLambdaEq(self, lw, porosity):
        return self.propM.getLambdaEq(lw, porosity)

    def setHeatCapa(self, hc):
        self.propM.setHeatCapa(hc)

    def getHeatCapa(self):
        return self.propM.getHeatCapa()

    def setRho(self, rho):
        self.propM.rho = rho

    def getRho(self):
        return self.propM.rho

    def setNameM(self, name):
        self.propM.setName = name

    def getNameM(self):
        return self.propM.getName()

    def printParamEffective(self):
        self.setEffectiveParams()
        print("\teffective parameters of {}:".format(self.propM.nameM))
        print(caracParamTemplate.format(
            '\t\teffective thermal conductivity',
            self.getKappa(), 'm2 s-1')
        )
        print(caracParamTemplate.format(
            '\t\teffective advective parameter',
            self.getAlpha(), 'm s-1')
        )

    def printParamEq(self):
        print('\tequivalent parameters of ', self.propM.nameM, ':')
        print(caracParamTemplate.format(
            '\t\tequivalent thermal conductivity: ',
            self.propM.getLambdaEq(LAMBDAW, self.propH.n),
            'W m-1 K-1'))
        print(caracParamTemplate.format(
            '\t\tequivalent heat capacity: ',
            self.propM.getHeatCapaEq(self.propH.n),
            'W m-1 K-1'))

    # This method calculates the solid properties based on equivalent properties
    # It therefore provides an indirect way of specifying equivalent properties
    def getSedPropFromEquivProp(self, lambdm, rhomCm, n=POROSITY, rhos=RHOS):
        print('targeted values for porous medium:\n')
        print('\tlambdam: ', lambdm)
        print('\trhomCm: ', rhomCm)
        lambds = pow((pow(lambdm, 0.5) - n * pow(LAMBDAW, 0.5)) / (1 - n), 2)
        cs = (rhomCm - n * HEATCAPAW * RHOW) / ((1 - n)*rhos)
        dico = {
            "sediment": {
                "lambda" : { "val" : lambds},
                "specificHeatCapacity" : { "val" : cs},
                "rho" : { "val" : rhos}               
            }
        }
        self.propM = PropMedia(dico)


if __name__ == '__main__':
    lambdm = 1
    rhomCm = lambdm / 2.5e-7
    propM = getSedPropFromEquivProp(lambdm, rhomCm)
    propM.printProp()

