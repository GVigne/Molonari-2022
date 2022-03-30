import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from study import Study
from dialogstudy import DialogStudy

From_MainWindow,dummy = uic.loadUiType(os.path.join(os.path.dirname(__file__),"mainwindow.ui"))
class MainWindow(QtWidgets.QMainWindow,From_MainWindow):
    def __init__(self):
        # Call constructor of parent classes
        super(MainWindow, self).__init__()
        QtWidgets.QMainWindow.__init__(self)
        
        self.setupUi(self)

        self.currentStudy = None
        
        self.actionCreate_Study.triggered.connect(self.createStudy)
        self.actionOpen_Study.triggered.connect(self.openStudy)
        
        self.sensorModel = QtGui.QStandardItemModel()
        self.treeViewSensors.setModel(self.sensorModel)
        
    def createStudy(self):
        dlg = DialogStudy() # Could be renamed DialogCreateStudy
        res = dlg.exec()
        if (res == QtWidgets.QDialog.Accepted) :
            self.currentStudy = dlg.getStudy()
            self.currentStudy.loadSensors(self.sensorModel)
        
    def openStudy(self):
        # TODO : create and show DialogOpenStudy, then intialiaze a new study
        self.currentStudy.loadSensors(self.sensorModel)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())