import sys, os, errno
from PyQt5 import QtWidgets, uic
from study import Study
from errors import *

From_DialogStudy = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogstudy.ui"))[0]

class DialogStudy(QtWidgets.QDialog, From_DialogStudy):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogStudy, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
        
        self.pushButtonBrowseRootDir.clicked.connect(self.browseRootDir)
        self.pushButtonBrowseSensorsDir.clicked.connect(self.browseSensorsDir)
        
    def browseRootDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Study Root Directory")
        if dirPath:
            self.lineEditRootDirPath.setText(dirPath) 
    
    def browseSensorsDir(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Study Root Directory")
        if dirPath:
            self.lineEditSensorsDir.setText(dirPath) 

    def setStudy(self):

        name = self.lineEditName.text()
        if not name: #si la lineEdit est vide
            raise EmptyFieldError('New study should have a name')
        
        sensorsdir = self.lineEditSensorsDir.text()
        if not os.path.isdir(sensorsdir):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), sensorsdir)
        
        rootpath = self.lineEditRootDirPath.text()
        if not os.path.isdir(rootpath):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), rootpath)
            
        rootdir = os.path.join(rootpath, name)
        os.mkdir(rootdir)
        return Study(name, rootdir, sensorsdir)

            


