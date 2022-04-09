import os, glob, shutil, sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic
import pandas as pd
from numpy import NaN
from datetime import datetime, timedelta

from sensors import PressureSensor, Shaft, Thermometer
from usefulfonctions import *
# from pyheatmy import *
from errors import *

class Point(object):
    
    '''
    classdocs
    '''

    def __init__(self, name="", pointDir="", psensor="", shaft="", rivBed=NaN, deltaH=NaN):
        self.name = name
        self.pointDir = pointDir
        self.psensor = psensor #nom du capteur de pression associé
        self.shaft = shaft #nom de la tige de température associée
        self.rivBed = rivBed
        self.deltaH = deltaH
        self.dftemp = pd.DataFrame()
        self.dfpress = pd.DataFrame()
    
    def getName(self):
        return self.name

    def getPointDir(self):
        return self.pointDir

    def getPressureSensor(self):
        return self.psensor

    def getShaft(self):
        return self.shaft    

    def loadPointFromDir(self):
        
        tempcsv = os.path.join(self.pointDir, "processed_data", "processed_temperatures.csv")
        presscsv = os.path.join(self.pointDir, "processed_data", "processed_pressures.csv")
        infocsv = os.path.join(self.pointDir, "info_data", "info.csv")
        
        df = pd.read_csv(infocsv, header=None, index_col=0)
        #self.oldName = df.iloc[0].at[1] 
        self.psensor = df.iloc[1].at[1]
        self.shaft = df.iloc[2].at[1]
        self.rivBed = float(df.iloc[5].at[1].replace(',','.'))
        self.deltaH = float(df.iloc[6].at[1].replace(',','.'))
        self.dftemp = readCSVWithDates(tempcsv)
        self.dfpress = readCSVWithDates(presscsv)
        self.tprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_temperatures.csv")
        self.pprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_pressures.csv")
        

    def loadPoint(self, pointModel): 
        try :
            item = QtGui.QStandardItem(self.name)
            item.setData(self, QtCore.Qt.UserRole)
            pointModel.appendRow(item)
            self.tprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_temperatures.csv")
            self.pprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_pressures.csv")
            item.appendRow(QtGui.QStandardItem(f"pressure sensor : {self.psensor}"))
            item.appendRow(QtGui.QStandardItem(f"shaft : {self.shaft}"))
            item.appendRow(QtGui.QStandardItem(f"rivBed = {self.rivBed:.2f}"))
            item.appendRow(QtGui.QStandardItem(f"offset = {self.deltaH:.2f}"))
        except Exception as e :
            shutil.rmtree(self.pointDir)
            raise e
    
    def delete(self):
        shutil.rmtree(self.pointDir)

    def processData(self, sensorDir):
        
        trawfile = os.path.join(self.pointDir, "raw_data", "raw_temperatures.csv")
        prawfile = os.path.join(self.pointDir, "raw_data", "raw_pressures.csv")
        tprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_temperatures.csv")
        pprocessedfile = os.path.join(self.pointDir, "processed_data", "processed_pressures.csv")

        # On charge les données
        dftemp = pd.read_csv(trawfile, skiprows=1)
        if dftemp.shape[1] < 6 :  # Idx + Date + Temp x4
            raise LoadingError("Too few columns in temperature file")
        dfpress = pd.read_csv(prawfile, skiprows=1)
        if dfpress.shape[1] < 4 : # Idx + Date + Tens + Temp
            raise LoadingError("Too few columns in pressure file")
        
        # On renomme (temporairement) les colonnes, on supprime les lignes sans valeur et on supprime l'index
        val_cols = ["Temp1", "Temp2", "Temp3", "Temp4"]
        all_cols = ["Idx", "Date Heure, GMT+01:00"] + val_cols
        for i in range(len(all_cols)) :
            dftemp.columns.values[i] = all_cols[i] 
        dftemp.dropna(subset=val_cols,inplace=True)
        dftemp.dropna(axis=1,inplace=True) # Remove last columns
        dftemp.drop(["Idx"],axis=1,inplace=True) # Remove first column
        val_cols = ["Tens", "Temp"]
        all_cols = ["Idx", "Date Heure, GMT+01:00"] + val_cols
        for i in range(len(all_cols)) :
            dfpress.columns.values[i] = all_cols[i]
        dfpress.dropna(subset=val_cols,inplace=True)
        dfpress.dropna(axis=1,inplace=True) # Remove last columns
        dfpress.drop(["Idx"],axis=1,inplace=True) # Remove first column
        
        # On convertie les dates au format yy/mm/dd HH:mm:ss
        convertDates(dftemp)
        convertDates(dfpress)

        # On vérifie qu'on a le même deltaT pour les deux fichiers
        # La référence sera l'écart entre les deux premières lignes pour chaque fichier 
        # --> Demander à l'utilisateur de vérifier que c'est ok
        dftemp_t0 = dftemp.iloc[0,0]
        dfpress_t0 = dfpress.iloc[0,0]
        deltaTtemp = dftemp.iloc[1,0] - dftemp_t0
        deltaTpress = dfpress.iloc[1,0] - dfpress_t0
        if deltaTtemp != deltaTpress :
            self.delete()
            raise TimeStepError(deltaTtemp, deltaTpress)
        else : 
            deltaT = deltaTtemp

        # On fait en sorte que les deux fichiers aient le même t0 et le même tf
        dftemp_tf = dftemp.iloc[-1,0]
        dfpress_tf = dfpress.iloc[-1,0]

        if dfpress_t0 < dftemp_t0 : 
            while dfpress_t0 != dftemp_t0:
                dfpress.drop(index=0, inplace=True)
                dfpress_t0 = dfpress.iloc[0,0]
        elif dfpress_t0 > dftemp_t0 : 
            while dfpress_t0 != dftemp_t0:
                dftemp.drop(index=0, inplace=True)
                dftemp_t0 = dftemp.iloc[0,0]

        if dfpress_tf > dftemp_tf:
            while dfpress_tf != dftemp_tf :
                dfpress.drop(dfpress.tail(1).index,inplace=True)
                dfpress_tf = dfpress.iloc[-1,0]
        elif dfpress_tf < dftemp_tf:
            while dfpress_tf != dftemp_tf :
                dftemp.drop(dftemp.tail(1).index,inplace=True)
                dftemp_tf = dftemp.iloc[-1,0]

        # On supprime les lignes qui ne respecteraient pas le deltaT
        i = 1
        while i<dftemp.shape[0]:
            if ( dftemp.iloc[i,0] - dftemp.iloc[i-1,0] ) % deltaT != timedelta(minutes=0) :
                dftemp.drop(dftemp.iloc[i].name,  inplace=True)
            else :
                i += 1
        i = 1
        while i<dfpress.shape[0]:
            if ( dfpress.iloc[i,0] - dfpress.iloc[i-1,0] ) % deltaT != timedelta(minutes=0) :
                dfpress.drop(dfpress.iloc[i].name,  inplace=True)
            else :
                i += 1
        
        # On convertie les températures en Kelvin
        celsiusToKelvin(dftemp)
        
        # On convertie les tensions en pression
        psensor = PressureSensor(self.psensor)
        info_csv = os.path.join(sensorDir, 'pressure_sensors', f'{self.psensor}.csv')
        psensor.setPressureSensorFromFile(info_csv)
        dfpress = psensor.tensionToPressure(dfpress)

        dftemp.to_csv(tprocessedfile, index=False)
        self.dftemp = dftemp

        dfpress.to_csv(pprocessedfile, index=False)
        self.dfpress = dfpress


    def cleanup(self, script, dft, dfp):

        scriptDir = self.pointDir + "/script.py"
        sys.path.append(self.pointDir)

        with open(scriptDir, "w") as f:
            f.write(script)
            f.close()

        from script import fonction

        os.remove(scriptDir)
        del sys.modules["script"]

        try :
            new_dft, new_dfp = fonction(dft, dfp)

            #exec(script)

            #On réécrit les csv:
            os.remove(self.tprocessedfile)
            os.remove(self.pprocessedfile)
            new_dft.to_csv(self.tprocessedfile, index=False)
            new_dfp.to_csv(self.pprocessedfile, index=False)

            self.dftemp = readCSVWithDates(self.tprocessedfile)
            self.dfpress = readCSVWithDates(self.pprocessedfile)

            return(new_dft, new_dfp)
        
        except Exception as e :
            raise e
    
    def reset(self):
        resultsDir = self.pointDir + "/results"
        DirectresultsDir = resultsDir + "/direct_model_results"
        MCMCresultsDir = resultsDir + "/MCMC_results"
        for fichier in os.listdir(DirectresultsDir) :
            os.remove(DirectresultsDir + "/" + fichier)
        for fichier in os.listdir(MCMCresultsDir) :
            os.remove(MCMCresultsDir + "/" + fichier)
    
    def setColumn(self, sensorDir):

        df = self.dftemp
        temperatures = df.drop(columns=df.columns[0], axis=1).to_numpy()
        df = self.dfpress
        pressures_and_temperatures = list(df.drop(columns=df.columns[0], axis=1).itertuples(index=False, name=None))

        # Assuming times are matching
        
        times = df[df.columns[0]]

        # Getting sensors info

        psensor = PressureSensor(self.psensor)
        infofile = os.path.join(sensorDir, 'pressure_sensors', f'{self.psensor}.csv')
        psensor.setPressureSensorFromFile(infofile)
        
        shaft = Shaft(self.shaft)
        infofile = os.path.join(sensorDir, 'shafts', f'{self.shaft}.csv')
        shaft.setShaftFromFile(infofile)

        thermometerName = shaft.getThermometer()
        thermometer = Thermometer(thermometerName)
        infofile = os.path.join(sensorDir, 'temperature_sensors', f'{thermometerName}.csv')
        thermometer.setThermometerFromFile(infofile)

        # Setting dictionnary

        col_dict = {
	        "river_bed": self.rivBed, 
            "depth_sensors": shaft.getDepths(),
	        "offset": self.deltaH,
            "dH_measures": list(zip(times, pressures_and_temperatures)),
	        "T_measures": list(zip(times, temperatures)),
            "sigma_meas_P": psensor.getSigma(),
            "sigma_meas_T": thermometer.getSigma()
            }
        
        col = Column.from_dict(col_dict)
        
        return col

