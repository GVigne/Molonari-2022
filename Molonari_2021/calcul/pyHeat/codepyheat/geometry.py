"""
    @author: Nicolas Flipo
    @date: 11.02.2021

    contains the main class Column that contains everything needed to
        run a simulation.
    Column is the most import class of pyHeat

    Classes Point, Geometry are important for the mesh definition,
        and maybe raster type plots
    Classes Cell and Face are functional objects that contains state
        variable Classes (Hydro and Heat)

    For this file to work autonomously, it is required to add the parent
        directory to the environment variable PYTHONPATH:
        export PYTHONPATH = $PYTHONPATH:<parent_dir>

    The Column is orientated downwards with the origin being the top

"""

import sys
import numpy as np
import pathlib
import matplotlib.pyplot as plt
import math

from codepyheat.factory import FactoryClass
from codepyheat import (X, Z, NDIM, N, S, complement, printDir, printDirCard,
                        caracItSteadyTemplate, caracParamTemplate, CODE_HEAT,
                        CODE_HYD, JSONPATH, BcHydPermTemplate, BcTempPermTemplate,
                        RHOW, HEATCAPAW)
from codepyheat.units import calcValMult, NSECINDAY
from codepyheat.heat import Heat, BoundaryConditionHeat, BoundConditionMultiSinus
from codepyheat.hydrogeol import Hydro, BoundaryConditionHyd 
from codepyheat.porousMedia import PropPorousMedia, LAMBDAW
from codepyheat.linearAlgebra import LinSys
from codepyheat.analSol import AnalSolution, AnalSolutionDiff, calcki


class Point:

    def __init__(self, x, z):
        self.x = x
        self.z = z

    def __str__(self) -> str:
        return "({},{}  {})".format(self.x, self.z, super.__str__(self))


class Geometry:
    area = 0

    def __init__(self, center, lenTuple):
        self.center = center
        self.lenTuple = lenTuple

    def getArea(self):
        if self.area == 0:
            self.area = self.lenTuple[X]*self.lenTuple[Z]
        return self.area
        # return self.lenTuple[X]*self.lenTuple[Z]


class Face:
    def __init__(self, id, length, dist):
        self.len = length
        self.dist = dist  # dist to next cell center
        # used for physical problem solving
        self.hydro = Hydro()
        self.heat = Heat()
        self.id = id


class Cell:
    def __init__(self, id, Center, SideLenTuple):
        self.id = id
        self.geom = Geometry(Center, SideLenTuple)
        self.face = [[], []]
        for i in range(NDIM):
            # self.face[i] = []
            for j in range(NDIM):
                idFace = "{}{}{}".format(id, printDir(i), printDirCard(i, j))
                self.face[i].append(
                    Face(idFace, SideLenTuple[complement(i)], SideLenTuple[i])
                )
        self.hydro = Hydro()
        self.heat = Heat()

    def getFace(self, dir, num):
        return self.face[dir][num]


class Column(FactoryClass):
    """
        instantiate with
            - Column(a_dict)
            - Column.fromJsonFile(full path and file name)
            - Column.fromJsonString(valid json string)

    """
    def __init__(self, a_dict):

        depth = calcValMult(a_dict['depth'], "depth")
        ncells = a_dict['ncells']

        self.depth = depth
        self.ncells = ncells
        self.sidelen = depth/ncells
        self.allocAndInitGeomCells()
        self.mergeFaces()
        self.dh = CODE_HYD  # Hydraulic gradient driving the flow in the
        # Column. The elevation reference is the bottom of the column
        self.tempRiv = CODE_HEAT
        self.tempAq = CODE_HEAT
        self.ls = LinSys(self.ncells)
        self.nperiod = CODE_HEAT


    def printProps(self):
        print('Caracteristics of the soil column:')
        print('\tdepth {} m'.format(self.depth))
        print('\tdepth', self.depth, 'm')
        print('\t', self.ncells, 'cells of side size', self.depth/self.ncells,
              'm')

    def allocAndInitGeomCells(self):
        sidelen = self.depth / self.ncells
        # print('side size', sidelen, 'm')
        xcoord = 0
        self.cell = []
        ncells = self.ncells
        for i in range(ncells):
            zcoord = i * sidelen  
            side_length = (sidelen, sidelen)
            self.cell.append(Cell(i, Point(xcoord + side_length[X]/2, zcoord +
                             side_length[Z]/2), side_length))

    def mergeFaces(self):
        ncells = self.ncells
        for i in range(1,ncells,1):
            self.cell[i-1].face[Z][S]=self.cell[i].face[Z][N]

    def initColumnHydrostatique(self, H):
        for i in range(self.ncells):
            cell = self.cell[i]
            cell.hydro.h = H
            for k in range(NDIM):
                cell.face[Z][k].hydro.h = H

    def setBcHyd(self, name):
        bchyd = BoundaryConditionHyd.fromJsonFile(name)
        self.setBcHydObj(bchyd)
        
    def setBcHydObj(self, bchyd):
        self.dh = bchyd.dh
        cell = self.cell[0]
        cell.hydro.setDirichletCell(Z, N)  # NF changing orientation, N instead of S
        face = cell.getFace(Z, N)  # NF changing orientation, N instead of S
        # face.hydro.setDirichletFace(0)  # NF changing orientation 
        face.hydro.setDirichletFace(self.dh)  # NF changing orientation 
        cell = self.cell[self.ncells - 1]
        cell.hydro.setDirichletCell(Z, S)  # NF changing orientation, S instead of N
        face = cell.getFace(Z, S)  # NF changing orientation, S instead of N
        # face.hydro.setDirichletFace(self.dh)  # NF changing orientation
        face.hydro.setDirichletFace(0)  # NF changing orientation

    def setBcT(self, name):
        bcT = BoundaryConditionHeat.fromJsonFile(name)
        self.setBcTObj(bcT)
        
    def setBcTObj(self, bcT):
        self.tempAq = bcT.tempAq
        self.tempRiv = bcT.tempRiv
        cell = self.cell[0]
        cell.heat.setDirichletCell(Z, N)  # NF changing orientation, N instead of S
        face = cell.getFace(Z, N)  # NF changing orientation, N instead of S
        # face.heat.setDirichletFace(self.tempAq)  # NF changing orientation
        face.heat.setDirichletFace(self.tempRiv)  # NF changing orientation
        cell = self.cell[self.ncells - 1]
        cell.heat.setDirichletCell(Z, S)  # NF changing orientation, S instead of N
        face = cell.getFace(Z, S)  # NF changing orientation, S instead of N
        # face.heat.setDirichletFace(self.tempRiv)  # NF changing orientation
        face.heat.setDirichletFace(self.tempAq)  # NF changing orientation

    def setHomogeneousPorMed(self, name):
        propPorMed = PropPorousMedia.fromJsonFile(name)
        self.setHomogeneousPorMedObj(propPorMed)
        
    def setHomogeneousPorMedObj(self, propPorMed):
        # propPorMed.printProps()
        self.physProp = propPorMed

    def solveDarcy(self):
        gradH = self.calcGrad()
        for i in range(self.ncells):
            self.cell[i].hydro.calcU(gradH, self.physProp.getUpperK())

    def solveHydSteadyHeatSteady(self):
        self.solveDarcy()
        self.fillLinSysT()
        self.ls.solveSysLin()
        upperT = []
        # print(self.ls.x)
        for i in range(self.ncells):
            cell = self.cell[i]
            cell.heat.upperT = self.ls.x[i]
            upperT.append(cell.heat.upperT)
            cell.heat.specificHeatFlux = cell.heat.upperT * cell.hydro.upperU  
        upperT = list(np.concatenate(upperT).flat)  # NF creates a real vector 
        # and not a list of arrays of dim 1
        return upperT

    def fillLinSysT(self):
        self.solveDarcy()
        kappa = self.physProp.kappa
        kappa /= self.sidelen
        kappa *= 2
        ls = self.ls
        for i in range(self.ncells):
            l1 = l2 = l3 = r = CODE_HYD
            cell = self.cell[i]
            q = cell.hydro.upperU
            if cell.hydro.type == 'regular':
                l3 = q - kappa  # i+1
                l2 = 2 * kappa  # i
                l1 = - (q + kappa)  # i-1
                r = 0
            else:
                l2 = 3 * kappa  # i
                if cell.hydro.type == 'BcDirichlet, face -> ZN':  # NF changing orientation, N instead of S
                    l3 = q - kappa  # i+1
                    r = (q + 2 * kappa) * cell.face[Z][N].heat.upperT  # NF changing orientation, N instead of S
                elif cell.hydro.type == 'BcDirichlet, face -> ZS':  # NF changing orientation, S instead of N
                    l1 = - (q + kappa)  # i-1
                    r = - (q - 2*kappa) * cell.face[Z][S].heat.upperT   # NF changing orientation, S instead of N
                    # Calculate it explicitly
            ls.setLhsVal(i, i-1, l1)
            ls.setLhsVal(i, i, l2)
            ls.setLhsVal(i, i+1, l3)
            ls.setRhsVal(i, r)

    def setNameOutputT(self, it):
        pathlib.Path("./output").mkdir(parents=True, exist_ok=True)
        if it != "NONE":
            str = "./output/T{}.csv".format(it)
        else:
            str = "./output/T0.csv".format(it)
        return str

    def printFileT(self, file):
        original_stdout = sys.stdout
        sys.stdout = file
        for i in range(self.ncells):
            cell = self.cell[i]
            # print(-i*cell.geom.lenTuple[Z], ',', float(cell.heat.upperT))  # NF changing orientation
            print(-cell.geom.center.z, ',', float(cell.heat.upperT))  # NF changing orientation
        file.close()
        sys.stdout = original_stdout

    def printT(self):
        str = 'NONE'
        self.iterativePrintT(str)

    def iterativePrintT(self, it):
        with open(self.setNameOutputT(it), 'w') as file:
            self.printFileT(file)

    def plotT(self):
        str = 'NONE'
        self.iterativePlotT(str)


    def iterativePlotT(self, it):
        data = np.genfromtxt(self.setNameOutputT(it), delimiter=',')
        plt.plot(data[:, 1], data[:, 0])
        plt.xlabel("Température in K")
        plt.ylabel("depth in m")
        plt.show()

    def setParamSteady(self, upperK, lambd, porosity, verbose):
        physP = self.physProp
        physP.setPermeability(upperK)
        if verbose:
            print("\tPhysical properties :")
            print(caracParamTemplate.format('\t\tpermeability:',
                  physP.getUpperK(), 'm s-1'))

        physP.setPorosity(porosity)     # Used in the lambda_eq formula
        if verbose:
            print(caracParamTemplate.format(
                '\t\tporosity', physP.getPorosity(), '--')
            )

        physP.setLambda(lambd)
        if verbose:
            print(caracParamTemplate.format(
                '\t\tequivalent thermal conductivity:',
                physP.getLambdaEq(LAMBDAW, physP.getPorosity()),
                'W m-1 K-1')
            )

        physP.setEffectiveParams()  # calculates kappa

    def generateZAxis(self):
        z = []
        for i in range(self.ncells):
            cell = self.cell[i]
            z.append(-cell.geom.center.z)
        return z

    def runForwardModelSteadyState(
            self,
            upperK,
            lambd,
            porosity,
            verbose=True,
            export=True,
            draw=True):

        """
            parameters of the sensitivity analysis and bayesian inversion:
            - permeability, thermal conductivity, porosity
        """

        if verbose:
            print("Running pyHeat in steady state with the following specs:")
            self.printBcHydSteady()
            self.printBcTempSteady()

        self.setParamSteady(upperK, lambd, porosity, verbose)
        upperT = self.solveHydSteadyHeatSteady()     # runs the fwd model
        if export:
            physP = self.physProp
            it = caracItSteadyTemplate.format(
                physP.getUpperK(), physP.getLambda(), physP.getPorosity()
            )
            self.iterativePrintT(it)
            if draw:
                # impossible to draw without export.
                # Draw is therefore conditional to the export
                self.iterativePlotT(it)   
        return upperT

    def calcGrad(self):
        return - self.dh / self.depth  # attention orientation vers le bas, il faut changer le signe

    def setParamAnalSolution(self,period):
        pi = math.pi
        alpha = self.physProp.alpha 
        kappa = self.physProp.kappa 
        gradH = self.calcGrad() # attention orientation vers le bas, il faut changer le signe
        vt =  - alpha * gradH
        
        if (abs(self.dh) > 0):        
            k1 = 1 / (2 * kappa)
            k2 = ( 8 * pi *kappa ) / period
            k3 = pow(vt, 4) + pow(k2, 2)
            k4 = pow(k3, 1/2)
            ka = k4 + pow(vt, 2)
            ka = calcki()(ka)
            kb = k4 - pow(vt, 2)
            kb = calcki()(kb)
            b = k1 * kb
            a = k1 * (ka - vt)
        else:
            a = b = pow(math.pi / (kappa * period), 1/2)
        #print(a,b,vt)
        self.physProp.b.append(b) 
        self.physProp.a.append(a)   

    def resetParamAnalSolution(self):
        self.physProp.b=[]
        self.physProp.a=[]

    def calcTFromBcTSinus(self, name, ndt, dt):
        bcts = BoundConditionMultiSinus.fromJsonFile(name)
        self.tempRiv = self.tempAq = bcts.tempAv
        return self.calcTFromBcTSinusObj(bcts, ndt, dt)

    def calcTandTrivFromBcTSinus(self, name, ndt, dt):
        bcts = BoundConditionMultiSinus.fromJsonFile(name)
        #print("checking the BCheat dict",bcts)
        self.tempRiv = self.tempAq = bcts.tempAv
        return [self.calcTFromBcTSinusObj(bcts, ndt, dt), self.calcBcTSinusObj(bcts, ndt, dt)]

    def calcTFromBcTSinusObj(self, bcts, ndt, dt,verbose=True):
        allT = np.zeros((ndt,self.ncells))
        psinus = bcts.sinus
        lsin = len(psinus)
        self.nperiod = lsin
        tempAv = bcts.tempAv # initialisation for the first signal, set to 0 after
        for i in range(lsin):
            self.setParamAnalSolution(psinus[i].period)
            if verbose:
                print("\t\tsetting up paramAnalSol for T calc, with tav {} ampli {}  period {}".format(tempAv,psinus[i].ampli,psinus[i].period))
            if (abs(self.dh) > 0):
                tempZT = AnalSolution(self.physProp.a[i],self.physProp.b[i],psinus[i].ampli,tempAv,psinus[i].period)
            else:
                tempZT = AnalSolutionDiff(self.physProp.a[i],psinus[i].ampli,tempAv,psinus[i].period)
            for idt in range(ndt):
                t = idt * dt
                for j in range(self.ncells):
                    cell = self.cell[j]
                    #cell.heat.upperT = tempZT.val(cell.geom.center.z,t)
                    #allT[idt][j] += cell.heat.upperT
                    allT[idt][j] += tempZT.val(cell.geom.center.z,t)
            tempAv = 0
        return allT


    def calcBcTSinusObj(self, bcts, ndt, dt,verbose=True):
        self.resetParamAnalSolution()
        rivT = np.zeros((ndt))
        psinus = bcts.sinus
        lsin = len(psinus)
        self.nperiod = lsin
        tempAv = bcts.tempAv # initialisation for the first signal, set to 0 after
        self.tempAq = tempAv
        for i in range(lsin):
            self.setParamAnalSolution(psinus[i].period)
            if verbose:
                print("\t\tsetting up Triv, with tav {} ampli {}  period {}".format(tempAv,psinus[i].ampli,psinus[i].period))
            if (abs(self.dh) > 0):
                tempZT = AnalSolution(self.physProp.a[i],self.physProp.b[i],psinus[i].ampli,tempAv,psinus[i].period)
            else:
                tempZT = AnalSolutionDiff(self.physProp.a[i],psinus[i].ampli,tempAv,psinus[i].period)
            for idt in range(ndt):
                t = idt * dt
                cell = self.cell[0]
                rivT[idt] += tempZT.tempRiv(cell.geom.center.z-cell.geom.lenTuple[Z],t)
            tempAv = 0
        return rivT

    def calcFluxFromBcTSinus(self,allT,tempRiv,valQ,ndt,dt,id):
        ncells = self.ncells
        adv = np.zeros((ndt,ncells))
        cond = np.zeros((ndt,ncells))
        deltaT = np.zeros((ndt,ncells))
        deltaBil = np.zeros((ndt,ncells))
        tempAq = self.tempAq
        ncells = self.ncells
        physProp = self.physProp
        rhomCm = physProp.propM.getHeatCapaEq(physProp.propH.n)
        wAdv = RHOW * HEATCAPAW
        height = self.sidelen
        for i in range(ndt):
            tRiv = tempRiv[id][i]
            self.solveDarcy()

            #First calculating adv fluxes at faces
            for j in range(ncells):
                cell = self.cell[j]
                q = cell.hydro.upperU
                hj = cell.heat
                if i>0:
                    hj.deltaT = -hj.upperT
                hj.upperT = allT[id][i][j]
                if i>0:
                    hj.deltaT += hj.upperT
                    hj.deltaT /= dt
                    deltaT[i][j] = hj.deltaT * rhomCm * height # in W.m-2
                    hj.deltaT = deltaT[i][j]
                if j > 0:
                    upperT = hj.upperT + self.cell[j-1].heat.upperT
                    upperT /= 2
                    cell.face[Z][N].heat.upperT = upperT
                    cell.face[Z][N].heat.speciAdv = - q * upperT
                    gradT = cell.heat.upperT - self.cell[j-1].heat.upperT
                    gradT /= self.sidelen
                    gradT *= - physProp.propM.getLambdaEq(LAMBDAW, physProp.propH.n)
                    cell.face[Z][N].heat.speciCond =  gradT
                else:
                    cell.face[Z][N].heat.upperT = tRiv
                    cell.face[Z][N].heat.speciAdv =  q * tRiv
                    cell.face[Z][N].heat.speciCond =  0
                cell.face[Z][N].heat.speciAdv *= -wAdv
            cell.face[Z][S].heat.upperT =  tempAq
            cell.face[Z][S].heat.speciAdv =  q * tempAq
            cell.face[Z][S].heat.speciAdv *= -wAdv
            cell.face[Z][S].heat.speciCond = cell.face[Z][N].heat.speciCond

            #Second mass balances at cell centers
            for j in range(ncells):
                cell = self.cell[j]
                hj=cell.heat
                hj.speciAdv = cell.face[Z][N].heat.speciAdv - cell.face[Z][S].heat.speciAdv
                adv[i][j] = hj.speciAdv
                hj.speciCond = cell.face[Z][N].heat.speciCond - cell.face[Z][S].heat.speciCond
                cond[i][j] = hj.speciCond
                hj.speciHeatFlux = hj.speciAdv + hj.speciCond
                hj.deltaBil = hj.deltaT - hj.speciHeatFlux
                deltaBil[i][j] = hj.deltaBil 
        print("Max error of Heat Balance closure for ItValQ {} at time {} s : {} W.m-2 (up,down excluded)\n".format(id,i*dt,np.amax(abs(deltaBil[i][1:-1]))))
        print("Max error of Heat Balance closure for ItValQ {} at time {} s : {} W.m-2\n".format(id,i*dt,np.amax(abs(deltaBil[i]))))
        #print(adv[i],cond[i],deltaT[i], deltaBil[i])
        return [adv,cond,deltaT,deltaBil]

    def printBcHydSteady(self):
        print(BcHydPermTemplate.format(self.dh))

    def printBcTempSteady(self):
        print(BcTempPermTemplate.format(self.tempRiv,self.tempAq))

    

if __name__ == '__main__':
    col = Column.fromJsonFile(JSONPATH + 'configColumn.json')
    col.printProps()
