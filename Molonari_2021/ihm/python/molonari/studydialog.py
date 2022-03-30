'''
Created on 7 janv. 2021

@author: fors
'''
import os

from PyQt5 import QtWidgets
from PyQt5 import uic

import study as stu
from fileutil import DirExists

From_StudyDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"studydialog.ui"))
class StudyDialog(QtWidgets.QDialog,From_StudyDialog):
    '''
    mode : 0 = New, 1 = Open, 2 = Edit, 3 = Save As
    '''

    def __init__(self, parent, mode=0, study=stu.Study.createDefault()):
        super(StudyDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.butBrowseRoot.clicked.connect(self.browseRoot)
        self.butBrowseSensor.clicked.connect(self.browseSensor)
        self.editRootDir.textChanged.connect(self.updateInfo)
        self.editDescrDir.textChanged.connect(self.updateInfo)
        self.editRawDir.textChanged.connect(self.updateInfo)
        self.editProcessedDir.textChanged.connect(self.updateInfo)
        self.editSensorDir.textChanged.connect(self.updateInfo)
        
        self.mode = mode
        if mode==1: # Open mode
            self.editName.setEnabled(False)
            self.editDescrDir.setEnabled(False)
            self.editRawDir.setEnabled(False)
            self.editProcessedDir.setEnabled(False)
            self.editSensorDir.setEnabled(False)
        else:
            self.editName.setText(study.name)
            self.editRootDir.setText(study.rootDir)
            self.editDescrDir.setText(study.descrDir)
            self.editRawDir.setText(study.rawDir)
            self.editProcessedDir.setText(study.processedDir)
            self.editSensorDir.setText(study.sensorDir)
            
        # Update locks
        self.updateInfo()
        
    def browseRoot(self):
        path = self.editRootDir.text().strip()
        if not DirExists(path):
            path = os.path.expanduser("~")
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             "Select Study Root Directory",
                                                             path,
                                                             QtWidgets.QFileDialog.ShowDirsOnly)
        if dirPath:
            self.editRootDir.setText(dirPath)                   

    def browseSensor(self):
        path = self.editSensorDir.text().strip()
        if not DirExists(path):
            path = os.path.expanduser("~")
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                             "Select Sensor Directory",
                                                             path,
                                                             QtWidgets.QFileDialog.ShowDirsOnly)
        if dirPath:
            self.editSensorDir.setText(dirPath)
             
    def updateInfo(self):
        path = self.editRootDir.text().strip()
        self.labelInfo.setText(" ")
        labels={0:"New", 1:"Open", 2:"Edit", 3:"Save As"}
        self.setWindowTitle("{} MolonaViz Study".format(labels.get(self.mode)))
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText(labels.get(self.mode))
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        if self.mode==0:
            if DirExists(path) and os.listdir(path): # New mode
                self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                self.labelInfo.setText("The Root directory must be empty")
            else:
                sensorDir = self.editSensorDir.text().strip()
                if not DirExists(sensorDir) or not os.listdir(sensorDir):
                    self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                    self.labelInfo.setText("The Sensor directory must not be empty")
        if self.mode==1: # Open mode
            study = stu.Study.createOpen(path)
            if study.isValid(False):
                self.editName.setText(study.name)
                self.editRootDir.setText(study.rootDir)
                self.editDescrDir.setText(study.descrDir)
                self.editRawDir.setText(study.rawDir)
                self.editProcessedDir.setText(study.processedDir)
                self.editSensorDir.setText(study.sensorDir)
            else:
                self.editName.setText("")
                self.editDescrDir.setText("")
                self.editRawDir.setText("")
                self.editProcessedDir.setText("")
                self.editSensorDir.setText("")
                self.labelInfo.setText("The Root directory is not a valid study!")
                self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                
    def getStudy(self):
        if self.mode==1: # Open
            study = stu.Study.createOpen(self.editRootDir.text())
        else : # New or Edit
            study = stu.Study(self.editName.text(),
                              self.editRootDir.text(),
                              self.editDescrDir.text(),
                              self.editRawDir.text(),
                              self.editProcessedDir.text(),
                              self.editSensorDir.text())
        return study
        