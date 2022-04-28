from sensors import PressureSensor, Shaft, Thermometer
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery
import os, glob, shutil, errno
import pandas as pd
import glob
from Database.mainDb import MainDb

from usefulfonctions import *
from point import Point
from errors import *
import sqlite3


class Study():
    """
    """
    def __init__(self, name: str="", rootDir: str="", sensorDir: str=""):
        self.name = name
        self.rootDir = rootDir
        self.sensorDir = sensorDir
        self.create_folders()
    
    def getName(self):
        return self.name
    
    def getRootDir(self):
        return self.rootDir
    
    def getSensorDir(self):
        return self.sensorDir

    def create_folders(self):
        """
        Initialise the overall structure, as well as the SQL database
        """
        #New Folder and its database
        os.mkdir(self.rootDir)
        self.path_to_db = os.path.join(self.rootDir,f"{self.name}.sqlite")
        con = sqlite3.connect(self.path_to_db)
        con.close()

        os.mkdir(os.path.join(self.rootDir,"Cleanup_scripts"))
        os.mkdir(os.path.join(self.rootDir,"Notices"))
        os.mkdir(os.path.join(self.rootDir,"Images"))

    def open_connection(self):
        """
        Open connection to the database
        """
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.path_to_db)
        self.con.open()
        #This shouldn't be closed until the moment the app is closed

    def create_tables(self):
        self.mainDb = MainDb(self.con)
        self.mainDb.createTables()
    
    def setup_sensors(self):
        """
        Insert into the database the information concerning this study. Previously, this was the "Convert to SQL" button.
        """
        try :
            self.mainDb.laboDb.insert()
            self.mainDb.studyDb.insert(self.currentStudy) 
        except Exception :
            raise LoadingError('SQL, study or labo')
        try :
            self.mainDb.thermometerDb.insert(self.currentStudy.getThermometersDb())
        except Exception :
            raise LoadingError("SQL, thermometers")
        try :
            self.mainDb.pressureSensorDb.insert(self.currentStudy.getPressureSensorsDb())
        except Exception :
            raise LoadingError("SQL, pressure sensors")
        try : 
            self.mainDb.shaftDb.insert(self.currentStudy.getShaftsDb())
        except Exception :
            raise LoadingError("SQL, shafts")
        try :
            self.mainDb.samplingPointDb.insert(self.currentStudy)
        except Exception :
            raise LoadingError('SQL, points')
        try :
            self.mainDb.rawMeasuresTempDb.insert(self.currentStudy)
            self.mainDb.rawMeasuresPressDb.insert(self.currentStudy)
            self.mainDb.cleanedMeasuresDb.insert(self.currentStudy)
        except Exception :
            raise LoadingError('SQL, Measures')
    
    def getThermometersDb(self):
        sdir = os.path.join(self.sensorDir, "temperature_sensors", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        thermometers = []
        for file in files:
            thermometer = Thermometer()
            thermometer.setThermometerFromFile(file)
            thermometers.append(thermometer)
        return thermometers
    
    def getPressureSensorsDb(self):
        sdir = os.path.join(self.sensorDir, "pressure_sensors", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        pressure_sensors = []
        for file in files:
            psensor = PressureSensor()
            psensor.setPressureSensorFromFile(file)
            pressure_sensors.append(psensor)
        return pressure_sensors

    def getShaftsDb(self):
        sdir = os.path.join(self.sensorDir, "shafts", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        shafts = []
        for file in files:
            shaft = Shaft()
            shaft.setShaftFromFile(file)
            shafts.append(shaft)
        return shafts    
   
    def getPointsDb(self):
        rdir = self.rootDir
        dirs = [ name for name in os.listdir(rdir) if os.path.isdir(os.path.join(rdir, name)) ] #no file
        dirs = list(filter(('.DS_Store').__ne__, dirs))
        #permet de ne pas prendre en compte les fichiers '.DS_Store'
        
        points = []
        for mydir in dirs:
            pointDir = os.path.join(self.rootDir, mydir)
            name = os.path.basename(pointDir)
            point = Point(name, pointDir)
            point.loadPointFromDir()
            points.append(point)
        return points

    def close_connection(self):
        """
        This shouldn't be called unless the app or the study is closed. Else, connection should be "global"
        """
        self.con.close()
    
    def __del__(self):
        self.con.close()


class Study(object):
    
    '''
    classdocs : to be written
    '''

    def __init__(self, name: str="", rootDir: str="", sensorDir: str=""):
        self.name = name
        self.rootDir = rootDir
        self.sensorDir = sensorDir
    
    def getName(self):
        return self.name
    
    def getRootDir(self):
        return self.rootDir
    
    def getSensorDir(self):
        return self.sensorDir

    def saveStudyToText(self):
        pathStudyText = os.path.join(self.rootDir, f"{clean_filename(self.name)}.txt")
        with open(pathStudyText, "w") as studyText :
            studyText.write(f"Name: {self.name} \n")
            studyText.write(f"SensorsDirectory: {self.sensorDir}")

    def loadStudyFromText(self):
        """
        Le fichier texte doit se présenter sous la forme suivante :
        Name: Nom de l'étude
        SensorsDir: Chemin d'accès du dossier capteurs
        """
        os.chdir(self.rootDir)
        textFiles = glob.glob("*.txt")
        filesNumber = len(textFiles)
        if  filesNumber != 1:
            raise TextFileError(filesNumber)
        else : 
            textFile = textFiles[0]
            with open(textFile, 'r') as studyText:
                lines = studyText.read().splitlines() 
                nameLine = lines[0]
                sensorDirLine = lines[1]
                name = nameLine.split(' ', 1)[1]
                sensorDir = sensorDirLine.split(' ', 1)[1]
            self.name = name
            self.sensorDir = sensorDir
            if not os.path.isdir(sensorDir):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), sensorDir)
    
    def addPoint(self, name: str, infofile: str, prawfile: str, trawfile: str, noticefile: str, configfile: str):

        """
        Crée, remplit le répertoire du point et retourne l'objet point
        """
    
        pointDir = os.path.join(self.rootDir, name) #le dossier porte le nom du point
        
        try :
            df_info = pd.read_csv(infofile, header=None, index_col=0)
            psensor = df_info.iloc[1].at[1]
            shaft = df_info.iloc[2].at[1]
            rivBed = float(df_info.iloc[5].at[1].replace(',','.'))
            deltaH = float(df_info.iloc[6].at[1].replace(',','.'))
            
            point = Point(name, pointDir, psensor, shaft, rivBed, deltaH)

            os.mkdir(pointDir)
            rawDataDir = os.path.join(pointDir, "raw_data")
            processedDataDir = os.path.join(pointDir, "processed_data")
            infoDataDir = os.path.join(pointDir, "info_data")
            resultsDir = os.path.join(pointDir, "results")

            os.mkdir(rawDataDir)
            shutil.copyfile(prawfile, os.path.join(rawDataDir, "raw_pressures.csv"))
            shutil.copyfile(trawfile, os.path.join(rawDataDir, "raw_temperatures.csv"))

            os.mkdir(infoDataDir)
            shutil.copyfile(infofile, os.path.join(infoDataDir, "info.csv"))
            shutil.copyfile(noticefile, os.path.join(infoDataDir, "notice.txt"))
            shutil.copyfile(configfile, os.path.join(infoDataDir, "config.png"))
            
            os.mkdir(processedDataDir)  
            point.processData(self.sensorDir)

            os.mkdir(resultsDir)
            resultsDirMCMC = os.path.join(pointDir, "results", "MCMC_results")
            resultsDirDirectModel = os.path.join(pointDir, "results", "direct_model_results")
            os.mkdir(resultsDirMCMC)
            os.mkdir(resultsDirDirectModel)
            return point

        except FileExistsError as e :
            raise CustomError(f"{str(e)}\nPlease choose a different point name") 
            return

        except Exception as e :
            shutil.rmtree(pointDir)
            raise e
    
    
    # Fonctions utiles seulement dans le cadre de l'utilisation de l'interface graphique : 

    def loadPressureSensors(self, sensorModel: QtGui.QStandardItemModel):
        sdir = os.path.join(self.sensorDir, "pressure_sensors", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        for file in files:
            psensor = PressureSensor()
            psensor.loadPressureSensor(file, sensorModel)
        
    
    def loadShafts(self, sensorModel: QtGui.QStandardItemModel):
        sdir = os.path.join(self.sensorDir, "shafts", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        for file in files:
            shaft = Shaft()
            shaft.loadShaft(file, sensorModel)  
            
            
    def loadThermometers(self, sensorModel: QtGui.QStandardItemModel):
        #sdir = os.path.join(self.sensorDir, "thermometer_sensors", "*.csv") # API v1
        sdir = os.path.join(self.sensorDir, "temperature_sensors", "*.csv")
        files = glob.glob(sdir)
        files.sort()
        for file in files:
            thermometer = Thermometer()
            thermometer.loadThermometer(file, sensorModel)  


    def loadPoints(self, pointModel: QtGui.QStandardItemModel):
        rdir = self.rootDir
        dirs = [ name for name in os.listdir(rdir) if os.path.isdir(os.path.join(rdir, name)) ] #no file
        dirs = list(filter(('.DS_Store').__ne__, dirs))
        #permet de ne pas prendre en compte les fichiers '.DS_Store'
        for mydir in dirs:
            pointDir = os.path.join(self.rootDir, mydir)
            name = os.path.basename(pointDir)
            point = Point(name, pointDir)
            point.loadPointFromDir()
            point.loadPoint(pointModel)