'''
Created on 3 mars 2021

@author: fors
'''
import os

from PyQt5 import QtWidgets
from PyQt5 import uic

import outputmesh as om

From_OutputMeshDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"outputmeshdialog.ui"))
class OutputMeshDialog(QtWidgets.QDialog,From_OutputMeshDialog):

    def __init__(self, parent, point, outputMesh):
        super(OutputMeshDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle("{} Output Mesh Dialog".format(point.name))

        self.editPointName.setText(point.name)
        self.comboSensors.addItem(point.geometry.sensor.name)
        
        self.doubleEditDepthMin.textChanged.connect(self.updateInfo)
        self.doubleEditDepthMax.textChanged.connect(self.updateInfo)
        self.doubleEditDepthStep.textChanged.connect(self.updateInfo)
        
        self.doubleEditDepthMin.setValue(outputMesh.min)
        self.doubleEditDepthMax.setValue(outputMesh.max)
        self.doubleEditDepthStep.setValue(outputMesh.step)
        
        # Update locks
        self.updateInfo()
            
    def updateInfo(self):
        self.labelInfo.setText("")
        # TODO : check that depths are consistent

    def getOutputMesh(self):
        outputmesh = om.OutputMesh(self.doubleEditDepthMin.value(),
                                   self.doubleEditDepthMax.value(),
                                   self.doubleEditDepthStep.value())
        return outputmesh
        