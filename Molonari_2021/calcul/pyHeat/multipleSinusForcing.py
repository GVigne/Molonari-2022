from codepyheat.units import NSECINDAY, NSECINHOUR
from codepyheat.geometry import Column
from codepyheat import JSONPATH
from codepyheat.hydrogeol import BoundaryConditionHyd
from codepyheat.heat import BoundConditionMultiSinus
from maintransitoire import plotTzt, plotFrise, plotRivt
import matplotlib.pyplot as plt
import numpy as np

#test forcing
dicoMultP = {
    "Taverage": {
        "val": 12,
        "unit": "°C"
    },
    "sinus": [ {
            "Tampli": {
                "val": 6,
                "unit": "K"
            },  
            "Period": {
                "val": 1,
                "unit": "yr"
            }
        },
        {
            "Tampli": {
                "val": 1,
                "unit": "K"
            },  
            "Period": {
                "val": 1,
                "unit": "j"
            }
        }
        ]
}

# step 1 setting up the problem
lambdm = 1
rhomCm = lambdm / 2.5e-7
dj = 0.25
jf = 366
dt = dj * NSECINDAY
ndt = int( jf / dj )

valQ = [1e-6, 0, -1e-6]  # m/s

dico = {
    "depth": {
            "val": "10",
            "unit": "m"
        },
    "ncells": 250
}
rivBed = Column(dico)
rivBed.setHomogeneousPorMed(JSONPATH + "paramColumn.json")
rivBed.printProps()
rivBed.physProp.getSedPropFromEquivProp(lambdm,rhomCm)
rivBed.physProp.printProps()
upperK = rivBed.physProp.propH.upperK
allT = np.zeros((len(valQ),ndt,rivBed.ncells))
tempRiv = np.zeros((len(valQ),ndt))

# step 2 problem solving 
id = 0
for q in valQ:
    grad = -q / upperK
    dh = -grad * rivBed.depth
    dicoBc =  {
        "dH" : {
            "val": dh,
            "unit": "m"
            }
    }
    bchyd = BoundaryConditionHyd(dicoBc)
    rivBed.setBcHydObj(bchyd)
    rivBed.printBcHydSteady()
    bcts = BoundConditionMultiSinus(dicoMultP)
    [allT[id], tempRiv[id]] = [rivBed.calcTFromBcTSinusObj(bcts, ndt, dt), rivBed.calcBcTSinusObj(bcts, ndt, dt)]  
    print(tempRiv[id])      
    id += 1
    rivBed.resetParamAnalSolution()

plotRivt(valQ,ndt,tempRiv,dt,False)
plotTzt(rivBed,valQ,ndt,allT,dt,False)
plotFrise(ndt,rivBed,allT,valQ)
