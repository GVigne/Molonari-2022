import os, glob, shutil, sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic
import pandas as pd
from numpy import NaN
from datetime import datetime, timedelta

from sensors import PressureSensor, Shaft, Thermometer
from usefulfonctions import *
from pyheatmy import *
from errors import *


class Point():
    """
    This class is made to store some important data about the current point being viewed. It is nothing more then an elaborated list
    """
    def __init__(self, name="",  psensor="", shaft="", rivBed=NaN, deltaH=0,poindir =""):
        self.name = name
        self.psensor = psensor #nom du capteur de pression associé
        self.shaft = shaft #nom de la tige de température associée
        self.rivBed = rivBed
        self.deltaH = deltaH
        self.pointDir = poindir
    
    def getName(self):
        return self.name

    def getPointDir(self):
        return self.pointDir

    def getPressureSensor(self):
        return self.psensor

    def getShaft(self):
        return self.shaft
    
    def loadPoint(self, pointModel): 
        item = QtGui.QStandardItem(self.name)
        item.setData(self, QtCore.Qt.UserRole)
        pointModel.appendRow(item)
        item.appendRow(QtGui.QStandardItem(f"pressure sensor : {self.psensor}"))
        item.appendRow(QtGui.QStandardItem(f"shaft : {self.shaft}"))
        item.appendRow(QtGui.QStandardItem(f"rivBed = {self.rivBed:.2f}"))
        item.appendRow(QtGui.QStandardItem(f"offset = {self.deltaH:.2f}"))
       
