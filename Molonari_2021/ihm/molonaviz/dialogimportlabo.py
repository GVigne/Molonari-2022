import os
from PyQt5 import QtWidgets, uic
from Database.pressureSensorDb import PressureSensorDb
from Database.thermometerDb import ThermometerDb
from errors import *
from usefulfonctions import displayCriticalMessage, getPressureSensorsDb, getShaftsDb, getThermometersDb
from Database.shaftDb import ShaftDb

From_DialogImportLabo = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogimportlabo.ui"))[0]

class DialogImportLabo(QtWidgets.QDialog, From_DialogImportLabo):
    
    def __init__(self, con):
        # Call constructor of parent classes
        super(DialogImportLabo, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
        
        self.con = con
        
        self.pushBrowseButton.clicked.connect(self.browseLabo)
        self.buttonBox.clicked.connect(self.insertLabo)
        
    def browseLabo(self):
        self.dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Configuration Directory")
        
        if self.dirPath:
            self.lineEditLabo.setText(self.dirPath)

    def insertLabo(self):
        dirPath = self.lineEditLabo.text()
        shafts = getShaftsDb(dirPath)
        thermometers = getThermometersDb(dirPath)
        psensors = getPressureSensorsDb(dirPath)
        
        thermometerDb = ThermometerDb(self.con)
        thermometerDb.insert(thermometers)
        
        psensorDb = PressureSensorDb(self.con)
        psensorDb.insert(psensors)
        
        shaftDb = ShaftDb(self.con)
        shaftDb.insert(shafts)
        
        if not thermometers or not psensors or not shafts:
            displayCriticalMessage("Error due to folder path", "Please select a good configuration folder")