'''
Created on 7 janv. 2021

@author: fors
'''

# importing os and shutil module 
import os
import shutil

import pandas as pd

from datetime import date

from PyQt5 import QtWidgets, QtCore
from fileutil import DirExists, ConvertDates
from sensor import Sensor
from point import Point
from geometry import Geometry

class Study(object):
    '''
    classdocs
    '''

    def __init__(self, name, rootDir, descrDir, rawDir, processedDir, sensorDir):
        self.name = name
        self.rootDir = rootDir
        self.descrDir = descrDir
        self.rawDir = rawDir
        self.processedDir = processedDir
        self.sensorDir = sensorDir
        self.resultDir = "results"
        
    # https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
    @classmethod
    def createDefault(cls):
        name="Default"
        rootDir = os.path.join(os.path.expanduser("~"),"molonari_data")
        descrDir = "desc_data"
        rawDir = "raw_data"
        processedDir = "processed_data"
        sensorDir = "sensor_data"
        return cls(name,rootDir,descrDir,rawDir,processedDir,sensorDir)
    
    @classmethod
    def createOpen(cls, arg):
        rootDir = arg
        pathStudy = os.path.join(rootDir, "study.txt")
        name = ""
        descrDir = ""
        rawDir = ""
        processedDir = ""
        sensorDir = ""
        try:
            file = open(pathStudy,"r")
            lines = file.readlines()
            for line in lines:
                if line.split('=')[0].strip() == "Name":
                    name = line.split('=')[1].strip()
                if line.split('=')[0].strip() == "DescrDir":
                    descrDir = line.split('=')[1].strip()
                if line.split('=')[0].strip() == "RawDir":
                    rawDir = line.split('=')[1].strip()
                if line.split('=')[0].strip() == "ProcessedDir":
                    processedDir = line.split('=')[1].strip()
                if line.split('=')[0].strip() == "SensorDir":
                    sensorDir = line.split('=')[1].strip()
        except IOError:
            return Study.createDefault()
        file.close()
        if not DirExists(sensorDir) or not os.listdir(sensorDir):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Sensor Directory must not be empty!')
            return Study.createDefault()
        return cls(name,rootDir,descrDir,rawDir,processedDir,sensorDir)
        
    def isValid(self,checkStudy=True):
        if not DirExists(self.rootPath()):
            return False
        if not DirExists(self.descrPath()):
            return False
        if not DirExists(self.rawPath()):
            return False
        if not DirExists(self.processedPath()):
            return False
        if not DirExists(self.sensorDir) or not os.listdir(self.sensorDir):
            return False
        if not DirExists(self.resultPath()):
            return False
        if checkStudy:
            study = Study.createOpen(self.rootPath())
            if not study.isValid(False):
                return False
        return True

    def create(self):
        # Create directories
        if DirExists(self.rootPath()) and os.listdir(self.rootPath()):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Root Directory must be empty!')
            return False
        if not DirExists(self.rootPath()):
            os.mkdir(self.rootPath())
        os.mkdir(self.descrPath())
        os.mkdir(self.rawPath())
        os.mkdir(self.processedPath())
        if not DirExists(self.sensorDir) or not os.listdir(self.sensorDir):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Sensor Directory must not be empty!')
            return False
        os.mkdir(self.resultPath())
        # Write study.txt file
        return self.save()

    def save(self):
        if not self.isValid(False):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Study is corrupted!')
            return False
        pathStudy = self.rootPath(True)
        try:
            file = open(pathStudy,"w")
            file.write("Name = {}\n"        .format(self.name))
            file.write("DescrDir = {}\n"    .format(self.descrDir))
            file.write("RawDir = {}\n"      .format(self.rawDir))
            file.write("ProcessedDir = {}\n".format(self.processedDir))
            file.write("SensorDir = {}\n"   .format(self.sensorDir))
        except IOError:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Geometry file not writable!')
            return False
        file.close()
        return True
    
    def saveAs(self, newStudy):
        if DirExists(newStudy.rootPath()) and os.listdir(newStudy.rootPath()):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Root Directory must be empty!')
            return False
        if DirExists(newStudy.rootPath()):
            shutil.rmtree(newStudy.rootPath())
        shutil.copytree(self.rootPath(), newStudy.rootPath())
        self.name = newStudy.name
        self.rootDir = newStudy.rootPath()
        self.descrDir = newStudy.descrDir
        self.rawDir = newStudy.rawDir
        self.processedDir = newStudy.processedDir
        self.sensorDir = newStudy.sensorDir
        return self.edit(newStudy)
    
    def edit(self, newStudy):
        self.name = newStudy.name
        if self.rootDir != newStudy.rootDir:
            os.rename(self.rootDir, newStudy.rootDir)
            self.rootDir = newStudy.rootDir
        if self.descrDir != newStudy.descrDir:
            newPath = os.path.join(self.rootDir,newStudy.descrDir)
            os.rename(self.descrPath(), newPath)
            self.descrDir = newStudy.descrDir
        if self.rawDir != newStudy.rawDir:
            newPath = os.path.join(self.rootDir,newStudy.rawDir)
            os.rename(self.rawPath(), newPath)
            self.rawDir = newStudy.rawDir
        if self.processedDir != newStudy.processedDir:
            newPath = os.path.join(self.rootDir,newStudy.processedDir)
            os.rename(self.processedPath(), newPath)
            self.processedDir = newStudy.processedDir
        if self.sensorDir != newStudy.sensorDir:
            self.sensorDir = newStudy.sensorDir
        if self.resultDir != newStudy.resultDir:
            newPath = os.path.join(self.rootDir,newStudy.resultDir)
            os.rename(self.resultPath(), newPath)
            self.resultDir = newStudy.resultDir
        return self.save()
    
    def loadSensor(self, sensorName):
        sensor = Sensor(sensorName)
        pathCalib = os.path.join(self.sensorDir, sensorName, "calibfit_{}.csv".format(sensorName))
        try:
            file = open(pathCalib,"r")
            lines = file.readlines()
            for line in lines:
                if line.split(';')[0].strip() == "Intercept":
                    sensor.intercept = line.split(';')[1].strip()
                if line.split(';')[0].strip() == "dU/dH":
                    sensor.dudh = line.split(';')[1].strip()
                if line.split(';')[0].strip() == "dU/dT":
                    sensor.dudt = line.split(';')[1].strip()
        except IOError:
            # TODO Trace log
            print ("Error with sensor {}".format(sensorName))
        return sensor
    
    def loadPoint(self, pointName, sensorModel):
        pathGeom = self.descrPath(pointName, 1) # Geometry
        geometry = Geometry.load(pathGeom, sensorModel)
        lastDate = date.today()
        pathRaw = self.rawPath(pointName)
        files = os.listdir(pathRaw)
        for file in files:
            tok = file.split('_')
            if len(tok) == 4 and len(tok[3].split('.')) == 2 and tok[3].split('.')[1] == "csv" :
                lastDate = QtCore.QDateTime.fromString(tok[3].split('.')[0], "yyyy-MM-dd")
            else:
                QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Unknown raw file!')
        point = Point(pointName, lastDate, geometry)
        return point
    
    def importPoint(self, point, src):
        pathDescr = self.descrPath(point)
        pathRaw = self.rawPath(point)
        pathProcessed = self.processedPath(point)
        if DirExists(pathDescr) or DirExists(pathRaw) or DirExists(pathProcessed):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Point already existing!')
            return False
        try:
            os.mkdir(pathDescr)
            point.geometry.write(self.descrPath(point, 1)) # Geometry
            shutil.copy(src.noticeFile, self.descrPath(point, 2)) # Notice
            shutil.copy(src.installFile, self.descrPath(point, 3)) # Installation
            for f in src.auxFiles:
                shutil.copy(f, pathDescr)
                
            os.mkdir(pathRaw)
            path = self.rawPath(point, 1)
            shutil.copyfile(src.rawTempFile, path)
            path = self.rawPath(point, 2)
            shutil.copyfile(src.rawPressFile, path)
            
            os.mkdir(pathProcessed)
            
            os.mkdir(self.resultPath(point))
            
        except IOError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cannot import point:\n\n{}'.format(e))
            self.removePoint(point)
            return False
        except TypeError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cannot import point:\n\n{}'.format(e))
            self.removePoint(point)
            return False
        return True
    
    def removePoint(self, point):
        pathDescr = self.descrPath(point)
        pathRaw = self.rawPath(point)
        pathProcessed = self.processedPath(point)
        pathResult = self.resultPath(point)
        if DirExists(pathDescr):
            shutil.rmtree(pathDescr)
        if DirExists(pathRaw):
            shutil.rmtree(pathRaw)
        if DirExists(pathProcessed):
            shutil.rmtree(pathProcessed)
        if DirExists(pathResult):
            shutil.rmtree(pathResult)
            
    def processPoint(self, point):
        pathRaw = self.rawPath(point)
        pathProcessed = self.processedPath(point)
        if not DirExists(pathRaw) or not DirExists(pathProcessed):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Point is corrupted!')
            self.removePoint(point)
            return False
        try:
            # Process temperatures file
            pathSrc = self.rawPath(point, 1)
            dft = pd.read_csv(pathSrc, skiprows=0, header=1)
            td = point.geometry.tempDepths
            #1 Keep index column
            #2 Date column
            dft.iloc[:,1] = ConvertDates(dft.iloc[:,1])
            dft.rename(columns={dft.columns[1]:'Time'},inplace=True)
            #3 Temperature columns
            nt = len(td)
            for i in range(nt):
                # Convert into kelvin
                dft.iloc[:,2+i] = dft.iloc[:,2+i] + 273.15
                dft.rename(columns={dft.columns[2+i]:'Temp.(K)-{}cm'.format(td[i])},inplace=True)
            #4 Drop remaining columns
            dft = dft.iloc[:,:nt+2]
            
            # Process pression file
            pathSrc = self.rawPath(point, 2)
            dfp = pd.read_csv(pathSrc, skiprows=0, header=1)
            #1 Keep index column
            #2 Date column
            dfp.iloc[:,1] = ConvertDates(dfp.iloc[:,1])
            dfp.rename(columns={dfp.columns[1]:'Time'},inplace=True)
            #3 Tension column: convert tension into head differential
            sensor = point.geometry.sensor
            # Cucchi 2018, Eq2   and   Mail N. Flipo 17/03/2021
            # U = (ΔH - ξ0 - ξ2 T) / ξ1
            #     intercept = a
            #     du/dH = b
            #     dU/dT = c
            # Hence: a = -ξ0/ξ1, b = 1/ξ1, c= -ξ2/ξ1
            # Finally: ξ1 = 1/b, ξ0 = -a/b, ξ2 = -c/b
            a = float(sensor.intercept)
            b = float(sensor.dudh)
            c = float(sensor.dudt)
            # Eq2
            dfp.iloc[:,2] = -(a/b) + (1/b) * dfp.iloc[:,2] -(c/b) * dfp.iloc[:,3]
            dfp.rename(columns={dfp.columns[2]:'Head Diff.(m)'},inplace=True)
            #4 Temperature columns: convert into kelvin
            dfp.iloc[:,3] = dfp.iloc[:,3] + 273.15
            dfp.rename(columns={dfp.columns[3]:'Temp.(K)'},inplace=True)
            #5 Drop remaining columns
            dfp = dfp.iloc[:,:4]
            
            # Check that time resolutions are the same in both files
            dtt1 = dft.iloc[0,1]
            dtp1 = dfp.iloc[0,1]
            dtt2 = dft.iloc[1,1]
            dtp2 = dfp.iloc[1,1]
            # Check time increment
            if (dtt2 - dtt1 != dtp2 - dtp1):
                QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Wrong time resolution!')
                return False
            
            # Make start time the same in both files
            if (dtt1 > dtp1):
                i = dfp[dfp.iloc[:,1]==dtt1].index.values[0]
                dfp = dfp.iloc[i:] # Remove first lines in dfp
            else:
                i = dft[dft.iloc[:,1]==dtp1].index.values[0]
                dft = dft.iloc[i:] # Remove first lines in dft
                
            # TODO : make stop time the same ?
            
            # Save processed files
            pathDest = self.processedPath(point, 1)
            dft.to_csv(pathDest,index=False)
            pathDest = self.processedPath(point, 2)
            dfp.to_csv(pathDest,index=False)
        except IOError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cannot process point:\n\n{}'.format(e))
            self.removePoint(point)
            return False
        except TypeError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cannot process point:\n\n{}'.format(e))
            self.removePoint(point)
            return False
        return True
    
    def cleanupPoint(self, point, script):
        pathProcessed = self.processedPath(point)
        if not DirExists(pathProcessed):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Point is corrupted!')
            self.removePoint(point)
            return False
        try:
            # Cleanup
            patht = self.processedPath(point, 1)
            pathp = self.processedPath(point, 2)

            # TODO : This doesn't work and I don't know why
            #dft = pd.read_csv(patht, header=0)
            #dfp = pd.read_csv(pathp, header=0)
            #exec(script) # TODO : execute safely by restricting available functions
            #dft.to_csv(patht,index=False)
            #dfp.to_csv(pathp,index=False)
            
            # Create the full script and execute
            fullscript  = "import numpy as np\n"
            fullscript += "import pandas as pd\n"
            fullscript += "patht='{}'\n".format(patht)
            fullscript += "pathp='{}'\n".format(pathp)
            fullscript += "dft = pd.read_csv(patht, header=0)\n"
            fullscript += "dfp = pd.read_csv(pathp, header=0)\n"
            fullscript += "{}\n".format(script)
            fullscript += "dft.to_csv(patht,index=False)\n"
            fullscript += "dfp.to_csv(pathp,index=False)\n"
            exec(fullscript)
            
        except IOError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error',f'Cannot cleanup point:\n\n{e}')
            return False
        except AttributeError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cleanup script error:\n\n{}'.format(e))
            return False
        except TypeError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cleanup script error:\n\n{}'.format(e))
            return False
        except ValueError as e:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cleanup script error:\n\n{}'.format(e))
            return False
        return True
    
    def rootPath(self, study=False):
        path = self.rootDir
        if study:
            path = os.path.join(path, "study.txt")
        return path
    
    # file: 0 = no file, 1 = geometry, 2 = notice, 3 = installation 
    def descrPath(self, point=None, file=0):
        path = os.path.join(self.rootDir,self.descrDir)
        if point:
            if isinstance(point, Point):
                path = os.path.join(path, point.name)
            else:
                path = os.path.join(path, point)
            if file == 1:
                path = os.path.join(path, "geometrie.txt")
            if file == 2:
                path = os.path.join(path, "notice.txt")
            if file == 3:
                path = os.path.join(path, "install.png")
        return path
    
    # file: 0 = no file, 1 = temperature, 2 = pressure 
    def rawPath(self, point=None, file=0):
        path = os.path.join(self.rootDir,self.rawDir)
        if point:
            if isinstance(point, Point):
                path = os.path.join(path, point.name)
                if file == 1:
                    path = os.path.join(path, point.tempFileName())
                if file == 2:
                    path = os.path.join(path, point.pressFileName())
            else:
                path = os.path.join(path, point)
        return path
    
    # file: 0 = no file, 1 = temperature, 2 = pressure
    def processedPath(self, point=None, file=0):
        path = os.path.join(self.rootDir,self.processedDir)
        if point:
            if isinstance(point, Point):
                path = os.path.join(path, point.name)
                if file == 1:
                    path = os.path.join(path, point.tempFileName())
                if file == 2:
                    path = os.path.join(path, point.pressFileName())
            else:
                path = os.path.join(path, point)
        return path
        
    # file: 0 = no file, 1 = river temp(t), 2 = vertical heat flux, 3 = temperature profiles
    def resultPath(self, point=None, file=0):
        path = os.path.join(self.rootDir,self.resultDir)
        if point:
            if isinstance(point, Point):
                path = os.path.join(path, point.name)
                if file == 1:
                    path = os.path.join(path, point.riverTempFileName())
                if file == 2:
                    path = os.path.join(path, point.tempProFileName())
                if file == 3:
                    path = os.path.join(path, point.waterVelFileName())
                if file == 4:
                    path = os.path.join(path, point.heatFlxFileName())
            else:
                path = os.path.join(path, point)
        return path