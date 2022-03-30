import sys, os, errno
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap


From_DialogAboutUs = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogaboutus.ui"))[0]

class DialogAboutUs(QtWidgets.QDialog,From_DialogAboutUs):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogAboutUs, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)

        logo1path = os.path.join(os.path.dirname(__file__), "MolonavizIcon.png")
        logo2path = os.path.join(os.path.dirname(__file__), "LogoMines.jpeg")

        self.labelLogo1.setPixmap(QPixmap(logo1path))
        self.labelLogo2.setPixmap(QPixmap(logo2path))