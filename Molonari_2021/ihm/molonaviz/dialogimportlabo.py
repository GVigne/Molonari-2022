import os
from PyQt5 import QtWidgets, uic
from Database.pressureSensorDb import PressureSensorDb
from Database.thermometerDb import ThermometerDb
from errors import *
from usefulfonctions import getPressureSensorsDb, getShaftsDb, getThermometersDb
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
        
    def browseLabo(self):
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Configuration Directory")
        
        if dirPath:
            self.lineEditLabo.setText(dirPath)
            shafts = getShaftsDb(dirPath)
            thermometers = getThermometersDb(dirPath)
            psensors = getPressureSensorsDb(dirPath)
            
            thermometerDb = ThermometerDb(self.con)
            thermometerDb.insert(thermometers)
            
            psensorDb = PressureSensorDb(self.con)
            psensorDb.insert(psensors)
            
            shaftDb = ShaftDb(self.con)
            shaftDb.insert(shafts)
