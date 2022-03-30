import sys
import os
from PyQt5 import QtWidgets, uic

From_DialogCleanup = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcleanup.ui"))[0]

class DialogCleanup(QtWidgets.QDialog, From_DialogCleanup):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogCleanup, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)


    def getScript(self):
        scriptpartiel = self.plainTextEdit.toPlainText()
        scriptindente = scriptpartiel.replace("\n", "\n   ")
        script = "def fonction(dft, dfp): \n   " + scriptindente + "\n" + "   return(dft, dfp)"
        return(script)
        