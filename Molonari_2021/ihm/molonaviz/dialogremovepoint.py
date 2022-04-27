import sys
import os
import shutil
from PyQt5 import QtWidgets, uic

From_DialogRemovePoint = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogremovepoint.ui"))[0]

class DialogRemovePoint(QtWidgets.QDialog, From_DialogRemovePoint):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogRemovePoint, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)

    def setPointsList(self, pointsModel):
        self.comboBox.setModel(pointsModel)

    def getPointToDelete(self):
        return self.comboBox.currentText()
