from PyQt5 import QtWidgets, uic
import os

From_DialogReset = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogreset.ui"))[0]

class DialogReset(QtWidgets.QDialog, From_DialogReset):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogReset, self).__init__()
        QtWidgets.QDialog.__init__(self)

        self.setupUi(self)