"""
    @author: Nicolas Flipo
    @date: 13.02.2021

    Ensures units convertion with the two generic functions :
    calcValMult and calcValAdd
    The unit conversion relies on an eval defined in __convOpTable.json

"""

import json
import sys

from codepyheat import JSONPATH

NSECINMIN = 60
NSECINHOUR = 3600
NSECINDAY = 86400
NDAYINYEAR = 365
NDAYINMONTH = 30
ZEROCELSIUS = 273.15


# length units
def unitL(unit):
    if unit == 'm':
        val = 1
    elif unit == 'cm':
        val = 0.01
    elif unit == 'mm':
        val = 0.001
    else:
        val = 1
    return val


# hydraulic properties' units
def unitHyd(unit):
    val = 1
    if unit == 'cm/s':
        val = 0.01
    elif unit == 'm/d':
        val = 1/NSECINDAY
    elif unit == 'g/m3':
        val = 0.001
    elif unit == 'mg/l':
        val = 0.001
    return val


# thermal properties' units
def unitPropT(unit):
    val = 1
    if unit != 'W m-1 K-1' and 'J s-1 m-1 K-1' and 'kg m-3 s-3 K-1':  # SI
        # units of lambda
        if unit != 'm2 s-2 K-1':
            str = """ERROR Units of thermal properties are not in SI
                    They must be for :
                    \tthermal conductivity --> 'W m-1 K-1' or 'J s-1 m-1 K-1'\
                     or 'kg m-3 s-3 K-1'
                    \tspecific heat capacity -->  'm2 s-2 K-1'"""
            sys.exit(str)
    return val


# Temperature units
def unitT(unit):
    val = 0
    if unit == '°C':
        val = ZEROCELSIUS
    elif unit == '°F' or unit == 'F':
        sys.exit("Farenheit unit not supported by the code, please convert in\
                 either °C or K")
    return val

# length units
def unitTime(unit):
    if unit == 's':
        val = 1
    elif unit == 'm':
        val = NSECINMIN
    elif unit == 'h':
        val = NSECINDAY
    elif unit == 'j':
        val = NSECINDAY
    elif unit == 'd':
        val = NSECINDAY
    elif unit == 'month':
        val = NSECINDAY*NDAYINMONTH
    elif unit == 'yr':
        val = NSECINDAY*NDAYINYEAR
    else:
        val = 1
    return val

def calcValMult(dict, paramName):
    with open(JSONPATH + "__convOpTable.json") as jf:
        uConv = json.load(jf)
    val = float(dict['val'])
    key = 'unit'
    if key in dict.keys():
        val *= eval(uConv[paramName])(dict['unit'])
    return val


def calcValAdd(dict, paramName):
    with open(JSONPATH + "__convOpTable.json") as jf:
        uConv = json.load(jf)
    val = float(dict['val'])
    key = 'unit'
    if key in dict.keys():
        val += eval(uConv[paramName])(dict['unit'])
    return val
