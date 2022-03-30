'''
Created on 3 mars 2021

@author: fors
'''
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic

import point as pt
from fileutil import FileExists

from geometry import Geometry
from geometrydialog import GeometryDialog
from PyQt5.Qt import QListWidgetItem

From_ImportPointDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"importpointdialog.ui"))
class ImportPointDialog(QtWidgets.QDialog,From_ImportPointDialog):

    def __init__(self, parent, sensorModel):
        super(ImportPointDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.sensorModel = sensorModel
        self.geometry = None
        
        # TODO : To be removed
        self.editName.setText("point41")
        self.dateEdit.setDateTime(QtCore.QDateTime.fromString("2017/07/11", "yyyy/MM/dd"))
        self.editRawTempFile.setText("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/HOBO_data/point41_18_05_17/p41_t_11_07_17.csv")
        self.editRawPressFile.setText("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/HOBO_data/point41_18_05_17/p41_p_11_07_17.csv")
        self.editGeomFile.setText("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/DESC_data/DATA_SENSOR/geometried_ET_data_miniLomos/point41_11_07_17/geometrie.txt")
        self.editNoticeFile.setText("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/DESC_data/DATA_SENSOR/geometried_ET_data_miniLomos/point41_11_07_17/notice.txt")
        self.editInstallFile.setText("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/DESC_data/DATA_SENSOR/geometried_ET_data_miniLomos/point41_11_07_17/systeme_41.png")
        item = QListWidgetItem("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/DESC_data/DATA_SENSOR/geometried_ET_data_miniLomos/point41_11_07_17/Figure_charge_temp_p41.png")
        self.listAuxFiles.addItem(item)
        item.setTextAlignment(QtCore.Qt.AlignRight)
        item = QListWidgetItem("/home/fors/Projets/molonari/data-hz/Avenelles/raw_data/DESC_data/DATA_SENSOR/geometried_ET_data_miniLomos/point41_11_07_17/systeme_41.svg")
        self.listAuxFiles.addItem(item)
        item.setTextAlignment(QtCore.Qt.AlignRight)
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText("Import")
        self.comboSensors.setModel(sensorModel)

        self.butBrowseRawTempFile.clicked.connect(self.browseRawTempFile)
        self.butBrowseRawPressFile.clicked.connect(self.browseRawPressFile)
        self.butBrowseGeomFile.clicked.connect(self.browseGeomFile)
        self.butEditGeomNew.clicked.connect(self.createGeom)
        self.butBrowseNoticeFile.clicked.connect(self.browseNoticeFile)
        self.butBrowseInstallFile.clicked.connect(self.browseInstallFile)
        self.butAddAuxFile.clicked.connect(self.addAuxFile)
        self.butDelAuxFile.clicked.connect(self.delAuxFile)
        
        self.radioGeomFile.toggled.connect(self.onCheckGeometry)
        self.radioGeomNew.toggled.connect(self.onCheckGeometry)
        self.editName.textChanged.connect(self.updateInfo)
        self.editRawTempFile.textChanged.connect(self.updateInfo)
        self.editRawPressFile.textChanged.connect(self.updateInfo)
        self.editGeomFile.textChanged.connect(self.updateInfo)
        self.editGeomNew.textChanged.connect(self.updateInfo)
        self.editNoticeFile.textChanged.connect(self.updateInfo)
        self.editInstallFile.textChanged.connect(self.updateInfo)
        self.listAuxFiles.model().rowsInserted.connect(self.updateInfo)
        
        # Update locks
        self.updateGeometry()
        self.updateInfo()
        
    def browseRawTempFile(self):
        path = self.editRawTempFile.text().strip()
        if not FileExists(path):
            path = os.path.expanduser("~")
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Select Raw Temperature CSV File",
                                                       path)
        if path:
            self.editRawTempFile.setText(path)                   

    def browseRawPressFile(self):
        path = self.editRawPressFile.text().strip()
        if not FileExists(path):
            path = os.path.expanduser("~")
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Select Raw Pressure CSV File",
                                                       path)
        if path:
            self.editRawPressFile.setText(path)

    def browseGeomFile(self):
        path = self.editGeomFile.text().strip()
        if not FileExists(path):
            path = os.path.expanduser("~")
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Select Geometry TXT File",
                                                       path)
        if path:
            self.editGeomFile.setText(path)
            self.updateGeometry()
            
    def createGeom(self):
        geometry = self.geometry
        diag = GeometryDialog(self, self.editName.text().strip(), self.sensorModel, geometry)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            geometry = diag.getGeometry()
            self.editGeomNew.setText(geometry.toString())
            self.updateGeometry(geometry)

    def browseNoticeFile(self):
        path = self.editNoticeFile.text().strip()
        if not FileExists(path):
            path = os.path.expanduser("~")
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Select Notice TXT File",
                                                       path)
        if path:
            self.editNoticeFile.setText(path)

    def browseInstallFile(self):
        path = self.editInstallFile.text().strip()
        if not FileExists(path):
            path = os.path.expanduser("~")
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Select Installation Scheme PNG File",
                                                       path)
        if path:
            self.editInstallFile.setText(path)
            
    def addAuxFile(self):
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                       "Add an Auxiliary File")
        if path:
            item = QListWidgetItem(path)
            self.listAuxFiles.addItem(item)
            item.setTextAlignment(QtCore.Qt.AlignRight)

    def delAuxFile(self):
        items = self.listAuxFiles.selectedItems()
        if items:
            self.listAuxFiles.takeItem(self.listAuxFiles.row(items[0]))

    def onCheckGeometry(self):
        self.updateGeometry(self.geometry)
        self.updateInfo()
        self.editGeomNew.setText(self.geometry.toString())
        
    def updateGeometry(self, geometry=None):
        self.geometry = geometry
        if self.radioGeomFile.isChecked():
            self.geometry = Geometry.load(self.editGeomFile.text().strip(), self.sensorModel)
        if (self.geometry and self.geometry.isValid()):
            self.comboSensors.setCurrentText(self.geometry.sensor.name)

    def updateInfo(self):
        self.labelInfo.setText(" ")
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
        if self.radioGeomNew.isChecked():
            self.butEditGeomNew.setEnabled(True)
        if not FileExists(self.editRawPressFile.text().strip()):
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.labelInfo.setText("The Raw Pressure File doesn't exist")
        if not FileExists(self.editRawTempFile.text().strip()):
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.labelInfo.setText("The Raw Temperature File doesn't exist")
        if not self.editName.text().strip():
            self.butEditGeomNew.setEnabled(False)
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
            self.labelInfo.setText("The Point Name must not be empty")

    def getPoint(self):
        point = pt.Point(self.editName.text().strip(),
                         self.dateEdit.dateTime(),
                         self.geometry)
        return point
        
    def getSourceFiles(self):
        srcFiles = pt.SourceFiles(self.editRawTempFile.text().strip(),
                                  self.editRawPressFile.text().strip(),
                                  self.editNoticeFile.text().strip(),
                                  self.editInstallFile.text().strip(),
                                  [self.listAuxFiles.item(i).text().strip() for i in range(self.listAuxFiles.count())])
        return srcFiles
        