import sys
import os
import shutil
from PyQt5 import QtWidgets, uic

From_DialogOpenPoint = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogopenpoint.ui"))[0]

class DialogOpenPoint(QtWidgets.QDialog, From_DialogOpenPoint):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogOpenPoint, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
    
    def setPointsList(self, pointModel):
        self.comboBox.setModel(pointModel)

    def getPointName(self):
        return self.comboBox.currentText()
        