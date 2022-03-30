"""

    @author: Nicolas Flipo
    @date: 11.02.2021

    main file of pyHeat1D
    Everything is based on the Column class in geometry.py
        1.  initialisation from a JSON file
        2.  setting up the properties of the porous medium with JSON files
        3.  setting up the boundary conditions (hydraulique and thermal) with
            JSON files
        4.  solving the problem and printing and plotting the results
        5.  setting up other parameter values and solving again
        6.  forcing the reading of equivalent parameters of the porous medium and launch a new calculation

"""
from codepyheat.units import NSECINDAY, NSECINHOUR
from codepyheat.geometry import Column
from codepyheat import JSONPATH
import matplotlib.pyplot as plt
import numpy as np

# step 1
rivBed = Column.fromJsonFile(JSONPATH + "configColumn.json")
rivBed.printProps()

# step 2
rivBed.setHomogeneousPorMed(JSONPATH + "paramColumn.json")
rivBed.physProp.printProps()

# step 3
rivBed.setBcHyd(JSONPATH + "configBcHydro.json")
rivBed.setBcT(JSONPATH + "configBcTemp.json")
rivBed.printBcHydSteady()
rivBed.printBcTempSteady()

# step 4 solving the problem and printing and plotting the results
upperK = rivBed.physProp.propH.upperK
porosity = rivBed.physProp.propH.n
lambd = rivBed.physProp.propM.getLambdaEq(n=porosity)
rivBed.runForwardModelSteadyState(upperK, lambd, porosity)
#rivBed.solveHydSteadyHeatSteady()
#rivBed.printT()
#rivBed.plotT()

# step 5 running forward model with other parameter values
#generate the z axis
z = rivBed.generateZAxis()
for l in (2,4,6,8) :
    # plt.plot(rivBed.runForwardModelSteadyState(1e-5, l, 0.1,False,False,False),np.linspace(0,-1,100),label=f"lambdas={l}")
    plt.plot(rivBed.runForwardModelSteadyState(1e-5, l, 0.1,False,False,False),z,label=f"lambdas={l}")
    
plt.legend()
plt.ylabel("hauteur colonne (m)")
plt.xlabel("Température de l'eau (K)")
plt.title("Profil de température en fonction de la conductivité thermique")
plt.show()
#rivBed.runForwardModelSteadyState(1e-5, 2, 0.1)

#rivBed.runForwardModelSteadyState(1e-7, 2, 0.1)
# rivBed.iterativePlotT(caracItSteadyTemplate.format(rivBed.physProp.upperK,rivBed.physProp.lambd,rivBed.physProp.n))

print('End of simulation pyHeat steady')


#step 6 force the model with equivalent parameters
lambdm = 1
rhomCm = lambdm / 2.5e-7

rivBed.physProp.getSedPropFromEquivProp(lambdm,rhomCm)
rivBed.physProp.printProps()
rivBed.solveHydSteadyHeatSteady()
rivBed.printT()
rivBed.plotT()

#step 7 calculate analytical solution
dj = 5
jf = 30
dt = dj * NSECINDAY
ndt = int( jf / dj )
allT = rivBed.calcTFromBcTSinus(JSONPATH + "periodicBC.json",ndt,dt)

for i in range(ndt):
    upperT = allT[i]
    #print("print h",i*dt/NSECINHOUR,upperT)
    plt.plot(upperT,z,label=f"{i*dt/NSECINHOUR} hr")
    
plt.legend()
plt.ylabel("longueur colonne (m)")
plt.xlabel("Température de l'eau (K)")
plt.title("Températures au cours du temps")
plt.show()
