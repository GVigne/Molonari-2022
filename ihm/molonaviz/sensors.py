from numpy import NaN
import numpy as np
import pandas as pd
import os, ast
from PyQt5 import QtWidgets, QtGui, QtCore, uic

class PressureSensor(object):
    
    '''
    classdocs
    '''

    def __init__(self, name="", intercept=NaN, dudh=NaN, dudt=NaN, sigma=NaN, datalogger="", calibrationDate=None):
        self.name = name
        self.intercept = intercept
        self.dudh = dudh
        self.dudt = dudt
        self.sigma = sigma
        self.datalogger = datalogger
        self.calibrationDate = calibrationDate
    
    def getSigma(self):
        return self.sigma

    def tensionToPressure(self, df):
        """
        classdoc
        """
        columnsNames = list(df.head(0))

        times = columnsNames[0]
        tension = columnsNames[1]
        temperature = columnsNames[2]

        df = df.astype({temperature : np.float, tension : np.float})
        a, b, c = self.intercept, self.dudh, self.dudt
        # La formule s'applique sur des °C
        df['Pression différentielle (m)'] = (1/b)*(df[tension] - c*df[temperature] - a)
        df[temperature] = df[temperature] + 273.15 #conversion en Kelvin
        df.drop([tension], axis=1, inplace=True)
        df = df[[times, 'Pression différentielle (m)', temperature]] #on réordonne les colonnes
        df.rename(columns={temperature: 'Température (K)'}, inplace=True)
        return df

        
    def setPressureSensorFromFile(self, csv):
        try :
            df = pd.read_csv(csv, header=None, index_col=0)
        except Exception :
            print("Couldn't load sensor file ", csv)
        try :
            self.name = df.iloc[0].at[1] #pas nécessaire ici puisqu'on a déjà le nom
            self.datalogger = df.iloc[1].at[1]
            self.calibrationDate = df.iloc[2].at[1] #à convertir au format date ?
            self.intercept = float(df.iloc[3].at[1].replace(',','.'))
            self.dudh = float(df.iloc[4].at[1].replace(',','.'))
            self.dudt = float(df.iloc[5].at[1].replace(',','.'))
            self.sigma = float(df.iloc[6].at[1].replace(',','.'))
        except Exception:
            print("Couldn't set pressure sensor from ", csv)
    
    def loadPressureSensor(self, csv, sensorModel):

        self.setPressureSensorFromFile(csv)
                    
        item = QtGui.QStandardItem(self.name)
        item.setData(self, QtCore.Qt.UserRole) 
        sensorModel.appendRow(item)
        item.appendRow(QtGui.QStandardItem(f"datalogger : {self.datalogger}"))
        item.appendRow(QtGui.QStandardItem(f"calibration date : {self.calibrationDate}"))
        item.appendRow(QtGui.QStandardItem(f"intercept = {self.intercept:.2f}"))
        item.appendRow(QtGui.QStandardItem(f"dudh = {self.dudh:.2f}"))
        item.appendRow(QtGui.QStandardItem(f"dudt = {self.dudt:.2f}"))
        item.appendRow(QtGui.QStandardItem(f"sigma = {self.sigma:.2f}"))



class Shaft(object):

    def __init__(self, name="", datalogger="", tSensorName="", depths=None):
        self.name = name
        self.datalogger = datalogger
        self.tSensorName = tSensorName
        self.depths = depths
    
    def getDepths(self):
        return self.depths
    
    def getThermometer(self):
        return self.tSensorName
    
    def setShaftFromFile(self, csv):
        try :
            df = pd.read_csv(csv, header=None)
        except :
            print("Couldn't load shaft ", csv)
        try :
            self.name = df.iloc[0].at[1] #pas nécessaire ici puisqu'on a déjà le nom
            self.datalogger = df.iloc[1].at[1]
            self.tSensorName = df.iloc[2].at[1] 
            self.depths = ast.literal_eval(df.iloc[3].at[1])
        except Exception:
            print("Couldn't set shaft from ", csv)
        
    def loadShaft(self, csv, sensorModel):
        self.setShaftFromFile(csv)
        item = QtGui.QStandardItem(self.name)
        item.setData(self, QtCore.Qt.UserRole) 
        sensorModel.appendRow(item)
        item.appendRow(QtGui.QStandardItem(f"datalogger : {self.datalogger}"))
        item.appendRow(QtGui.QStandardItem(f"thermometers type : {self.tSensorName}"))
        item.appendRow(QtGui.QStandardItem(f"thermometers depths (m) : {self.depths}"))



class Thermometer(object):

    def __init__(self, name="", consName="", ref="", sigma=NaN):
        self.name = name
        self.consName = consName
        self.ref = ref
        self.sigma = sigma
    
    def getSigma(self):
        return self.sigma
    
    def setThermometerFromFile(self, csv):
        try :
            df = pd.read_csv(csv, header=None, index_col=0)
        except :
            print("Couldn't load thermometer ", csv)
        try :
            self.consName = df.iloc[0].at[1] 
            self.ref = df.iloc[1].at[1]
            self.name = df.iloc[2].at[1] #pas nécessaire ici puisqu'on a déjà le nom
            self.sigma = float(df.iloc[3].at[1].replace(',','.'))
        except Exception:
            print("Couldn't set thermometer from ", csv)

    def loadThermometer(self, csv, sensorModel):

        self.setThermometerFromFile(csv)
                    
        item = QtGui.QStandardItem(self.name)
        item.setData(self, QtCore.Qt.UserRole) 
        sensorModel.appendRow(item)
        item.appendRow(QtGui.QStandardItem(f"manufacturer name : {self.consName}"))
        item.appendRow(QtGui.QStandardItem(f"manufacturer ref : {self.ref}"))
        item.appendRow(QtGui.QStandardItem(f"sigma (°C) : {self.sigma}"))

        
   
    

