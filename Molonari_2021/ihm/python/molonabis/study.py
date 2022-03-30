from sensor import Sensor
import os
from PyQt5 import QtGui, QtCore

class Study(object):
    '''
    classdocs
    '''

    def __init__(self, name, rootDir, sensorDir):
        self.name = name
        self.rootDir = rootDir
        self.sensorDir = sensorDir
    
    def loadSensors(self, sensorModel):
        # Reset the model (remove all sensors) !
        sensorModel.clear()
        # Reload all sensors from sensorDir
        sdir = self.sensorDir
        dirs = os.listdir(sdir)
        for mydir in dirs:
            sensor = self.loadSensor(mydir)
            
            item = QtGui.QStandardItem(mydir)
            item.setData(sensor, QtCore.Qt.UserRole)
            
            sensorModel.appendRow(item)
            item.appendRow(QtGui.QStandardItem("intercept = {:.2f}".format(float(sensor.intercept))))
            item.appendRow(QtGui.QStandardItem("dudh = {:.2f}".format(float(sensor.dudh))))
            item.appendRow(QtGui.QStandardItem("dudt = {:.2f}".format(float(sensor.dudt))))
    
    def loadSensor(self, sensorName):
        sensor = Sensor(sensorName)
        pathCalib = os.path.join(self.sensorDir, sensorName, "calibfit_{}.csv".format(sensorName))
        file = open(pathCalib,"r")
        lines = file.readlines()
        for line in lines:
            if line.split(';')[0].strip() == "Intercept":
                sensor.intercept = line.split(';')[1].strip()
            if line.split(';')[0].strip() == "dU/dH":
                sensor.dudh = line.split(';')[1].strip()
            if line.split(';')[0].strip() == "dU/dT":
                sensor.dudt = line.split(';')[1].strip()
        return sensor
    
    