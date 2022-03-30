'''
Created on 15 march 2021

@author: fors
'''
import os

from PyQt5 import QtWidgets
from PyQt5 import uic

From_CleanupDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"cleanupdialog.ui"))
class CleanupDialog(QtWidgets.QDialog,From_CleanupDialog):
    '''
    classdocs
    '''
    def __init__(self, parent, point, script=""):
        super(CleanupDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.setWindowTitle("{} Cleanup Dialog".format(point.name))
        
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(self.onApply) 
        
        if (script):
            self.editScript.setPlainText(script)

    def onApply(self):
        self.parentWidget().cleanupPoint(self.getScript())
        
    def getScript(self):
        return self.editScript.toPlainText()