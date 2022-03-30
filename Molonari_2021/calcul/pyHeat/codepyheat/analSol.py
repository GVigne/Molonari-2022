"""
    @author: Nicolas Flipo
    @date: 17.03.2021

    Solves the analytical solution of Stallman65

"""
import math

class AnalSolution():
    def __init__(self,a,b,tempAmp,tempAv,period):
        self.val = stallman65(a,b,tempAmp,tempAv,period)
        self.tempRiv = bcPeriodic(tempAmp,tempAv,period)

class AnalSolutionDiff():
    def __init__(self,a,tempAmp,tempAv,period):
        self.val = carslaw59(a,tempAmp,tempAv,period)
        self.tempRiv = bcPeriodic(tempAmp,tempAv,period)

def stallman65(a,b,tempAmp,tempAv,period):
    return lambda z, t: tempAv + tempAmp * math.exp(-a * z) * math.cos((2 * math.pi * t)/period - b * z)

def carslaw59(a,tempAmp,tempAv,period):
    return lambda z, t: tempAv + tempAmp * math.exp(-a * z) * math.cos((2 * math.pi * t)/period - a * z)

def bcPeriodic(tempAmp,tempAv,period):
    return lambda z, t: tempAv + tempAmp * math.cos((2 * math.pi * t)/period)
    

def calcki():
    return lambda x: pow(x/2, 1/2)
   
