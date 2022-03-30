from codepyheat.units import NSECINDAY, NSECINHOUR
from codepyheat.geometry import Column
from codepyheat import JSONPATH
from codepyheat.hydrogeol import BoundaryConditionHyd
from codepyheat.analSol import calcki
import matplotlib.pyplot as plt
import numpy as np
import math

# plotting Temperature boundary condition in the river
def plotRivt(valQ,ndt,tempRiv,dt,legend=True):
    t = []
    for i in range(ndt):
        t.append(i*dt/NSECINHOUR)

    fig, ax = plt.subplots(figsize=(6, 6))
    for id in range (len(valQ)):
        markers = [".","--","-."]
        l = len(markers)  
        plt.plot(t, tempRiv[id],markers[id%l],label=f"{valQ[id]} m/s")

    plt.ylabel("River temperature (K)")
    plt.xlabel("hours")
    plt.title("River temperature")
    if legend:
        plt.legend(loc='best', frameon=False)
    plt.show()

# step 3 plotting Temperature profiles

def plotTzt(rivBed,valQ,ndt,allT,dt,legend=True):
    z = rivBed.generateZAxis()
    for id in range (len(valQ)):
        markers = [".","--","-."]
        l = len(markers)
        fig, ax = plt.subplots(figsize=(6, 12))    
        for i in range(ndt):
            upperT = allT[id][i]
            #print("print h",i*dt/NSECINHOUR,upperT)
            plt.plot(upperT,z,markers[i%l],label=f"{i*dt/NSECINHOUR} hr")

        plt.ylabel("Depth (m)")
        plt.xlabel("Temperature (K)")
        plt.title("Temporal evolution of temperatures, q = {} m.s-1".format(valQ[id]))
        if legend:
            plt.legend(loc='best', frameon=False)
        plt.show()

# step 4 generating 2D graphs
def plotFrise(ndt,rivBed,allT,valQ):
    z = rivBed.generateZAxis()
    days = []
    for p in range(ndt):
        days.append(p)
    #generating zaxis   
    zaxis = np.zeros((len(z)+1))
    dz = rivBed.sidelen/2
    zaxis[0] = z[0] - dz
    for j in range(len(z)):
        zaxis[j+1] = z[j] + dz

    taxis = np.zeros((ndt+1))
    dz = -0.5
    taxis[0] = -dz
    for j in range(ndt):
        taxis[j+1] = j + dz

    cmin = np.min(allT)
    cmax = np.max(allT)
    print(cmin,cmax)
    for ii in range(len(valQ)):
        fig, ax = plt.subplots()
        mat=allT[ii].transpose()
        cmap=plt.get_cmap('RdBu')
        im = ax.pcolormesh(taxis,zaxis,mat, cmap=cmap.reversed())
        str = "Temperature profiles for q = {:3.2e} m.s-1".format(valQ[ii])
        ax.set_title(str)
        ax.set_xlabel("days")
        ax.set_ylabel("depth in m")
        fig.colorbar(im, ax=ax)
        plt.show()  


if __name__ == '__main__':
    # step 1 setting up the problem
    lambdm = 1
    rhomCm = lambdm / 2.5e-7
    dj = 1.25
    jf = 30
    dt = dj * NSECINDAY
    ndt = int( jf / dj )
    valQ = [1e-6, 0, -1e-6]  # m/s
    dico = {
        "depth": {
                "val": "8",
                "unit": "m"
            },
        "ncells": 200
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
        [allT[id], tempRiv[id]] = rivBed.calcTandTrivFromBcTSinus(JSONPATH + "periodicBC.json",ndt,dt) 
    #Calculating fluxes
        ncells = rivBed.ncells
        adv = np.zeros((len(valQ),ndt,ncells))
        cond = np.zeros((len(valQ),ndt,ncells))
        deltaT = np.zeros((len(valQ),ndt,ncells))
        deltaBil = np.zeros((len(valQ),ndt,ncells))
        [adv[id],cond[id],deltaT[id], deltaBil[id]] = rivBed.calcFluxFromBcTSinus(allT,tempRiv,valQ,ndt,dt,id)

        id += 1
        rivBed.resetParamAnalSolution()

    #Il reste à tracer les frises de flux en W.m-2
    
    # now executing step 3 and 4 with a temperature plot at the surface befor hand
    plotRivt(valQ,ndt,tempRiv,dt)
    plotTzt(rivBed,valQ,ndt,allT,dt)
    plotFrise(ndt,rivBed,allT,valQ)

  
    #step 5 penetrating depths :
    from codepyheat.units import NSECINHOUR

    kappa = rivBed.physProp.kappa
    alpha = rivBed.physProp.alpha
    upperK = rivBed.physProp.propH.upperK

    valQp = [1e-5, 1e-6, 1e-7, 1e-8]
    coef = [1, -1]  # downward, upward

    nhr = [0.5,1,2,3,4,5,6,12,24]
    for nj in [2,7,14,21,28]:
        nhr.append(nj*24)
    for nmonth in range(2,13,1):
        nhr.append(nmonth*24*30) 
    nhr.append(365*24)

    zp = np.zeros((len(coef),len(valQp),len(nhr)))
    kk=0
    for m in coef:
        ii = 0
        for q in valQp:
            print(q)
            grad = -q / upperK
            grad *= m
            jj = 0
            for p in nhr:
                vt = - alpha * grad
                #vt /= rivBed.depth
                gamma = ( 8 * math.pi *kappa ) / (p*NSECINHOUR)
                gamma = pow(gamma,2) + pow(vt,4)
                gamma = pow(gamma,0.5)
                numerator = 2 * kappa
                denom = (gamma + pow(vt,2))/2
                denom = pow(denom, 0.5)
                denom -= vt
                zp[kk][ii][jj] = numerator/denom
                #print("dh {}, vt {}, gamma {}, num {}, denom {}, zp {}".format(dh,vt,gamma,numerator,denom,zp[kk][ii][jj]))
                jj += 1
            ii += 1
            #print(m,q,ii,p)
        kk += 1

    #print(zp)
    #step 6 plotting penetrating depths


    fig, axs = plt.subplots(1, 2,figsize=(15, 12))
    markers = ["+",".","--","-."]
    l = len(markers)

    for kk in range(len(coef)):
        if kk == 0:
            str = 'Downward flow'
        else:
            str = 'Upward flow'
        axs[kk].set_title("{}".format(str))
        axs[kk].set_xlabel("hours")
        axs[kk].set_ylabel("Penetrating depth in m")
        axs[kk].set_ylim(2e5,1e-2)
        axs[kk].grid(True)
        ii = 0
        m=coef[kk]
        for q in valQp:
            axs[kk].loglog(nhr,zp[kk][ii],markers[ii],label=f"{q*m} m/s")   
            ii+=1
        axs[kk].legend(loc='best', frameon=False)

    plt.show()


    #step 7 propagation rates :
    #from codepyheat.units import NSECINHOUR
    pi = math.pi
    kappa = rivBed.physProp.kappa
    alpha = rivBed.physProp.alpha
    upperK = rivBed.physProp.propH.upperK

    valQpr = [1e-5, 1e-6, 1e-7, 1e-8, 0]
    pr = np.zeros((len(valQpr),len(nhr)))
    ii = 0
    for q in valQpr:
        jj = 0
        for p in nhr:
            period = p*NSECINHOUR
            if q > 1e-15:  
                vt = - alpha * q
                vt /= upperK 
                k1 = 1 / (2 * kappa)
                k2 = ( 8 * pi *kappa ) / period
                k3 = pow(vt, 4) + pow(k2, 2)
                k4 = pow(k3, 1/2)
                kb = k4 - pow(vt, 2)
                kb = calcki()(kb)
                b = k1 * kb
                valV = 2 * pi   
                valV /= period * b
                rivBed.resetParamAnalSolution()
            else:
                valV = 4 * pi * kappa
                valV /= period
                valV = valV**0.5
            pr[ii][jj] = valV
            jj += 1
        ii += 1

    fig, axs = plt.subplots(1, 1,figsize=(10, 6))
    markers = ["+",".","--","-.","-"]
    l = len(markers)
    for kk in range(len(valQpr)):
        axs.loglog(nhr,pr[kk],markers[kk],label=f"{valQpr[kk]} m/s")   
    axs.set_title("Propagation rate vs period")
    axs.set_xlabel("Period in hours")
    axs.set_ylabel("Propagation rate in m/s")
    axs.set_ylim(1e-7,1e-4)
    axs.grid(True)
    axs.legend(loc='best', frameon=False)

    plt.show()