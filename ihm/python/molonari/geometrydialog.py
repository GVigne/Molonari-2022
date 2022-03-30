'''
Created on 3 mars 2021

@author: fors
'''
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5 import uic

import geometry as geom

From_GeometryDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"geometrydialog.ui"))
class GeometryDialog(QtWidgets.QDialog,From_GeometryDialog):

    def __init__(self, parent, pointName, sensorModel, geometry):
        super(GeometryDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.editPointName.setText(pointName)
        self.comboSensors.setModel(sensorModel)

        self.butAddTempDepth.clicked.connect(self.addTempDepth)
        self.butDelTempDepth.clicked.connect(self.delTempDepth)
        
        self.doubleEditDepthRiverTube.textChanged.connect(self.updateInfo)
        self.doubleEditDepthHyporheicTube.textChanged.connect(self.updateInfo)
        self.listTempDepths.model().rowsInserted.connect(self.updateInfo)
        
        for i in range(len(geometry.tempDepths)):
            self.appendTempDepth(str(geometry.tempDepths[i])) 
        self.doubleEditDepthRiverTube.setValue(geometry.riverDepth)
        self.doubleEditDepthHyporheicTube.setValue(geometry.hyporheicDepth)
        
        if (geometry and geometry.isValid()):
            self.comboSensors.setCurrentText(geometry.sensor.name)
            
        # Update locks
        self.updateInfo()

    def appendTempDepth(self, val="0.00"):
        item = QtWidgets.QListWidgetItem(val)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        self.listTempDepths.addItem(item)
        
    def addTempDepth(self):
        self.appendTempDepth()
              
    def delTempDepth(self):
        items = self.listTempDepths.selectedItems()
        if items:
            self.listTempDepths.takeItem(self.listTempDepths.row(items[0]))  
            
    def updateInfo(self):
        self.labelInfo.setText("")
        # TODO : Check that depth are consistent increasing
                
    def getGeometry(self):
        index = self.comboSensors.currentIndex()
        item = self.comboSensors.model().item(index)
        sensor = item.data(QtCore.Qt.UserRole)
        depths =  [float(self.listTempDepths.item(i).text()) for i in range(self.listTempDepths.count())]
        geometry = geom.Geometry(sensor,
                                 self.doubleEditDepthRiverTube.value(),
                                 self.doubleEditDepthHyporheicTube.value(),
                                 depths)
        return geometry
        