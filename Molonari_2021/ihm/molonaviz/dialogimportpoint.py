import sys, os, shutil, re
from PyQt5 import QtWidgets, uic
from usefulfonctions import clean_filename, displayWarningMessage, displayCriticalMessage
from point import Point
import pandas as pd
from errors import *

From_DialogImportPoint = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogimportpoint.ui"))[0]

class DialogImportPoint(QtWidgets.QDialog, From_DialogImportPoint):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogImportPoint, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)

        self.radioButtonAuto.toggled.connect(self.autoEntry)
        self.radioButtonManual.toggled.connect(self.manualEntry)

        self.pushButtonBrowseDataDir.clicked.connect(self.browseDataDir)
        self.pushButtonBrowseInfo.clicked.connect(self.browseInfo)
        self.pushButtonBrowsePressures.clicked.connect(self.browsePressures)
        self.pushButtonBrowseTemperatures.clicked.connect(self.browseTemperatures)
        self.pushButtonBrowseNotice.clicked.connect(self.browseNotice)
        self.pushButtonBrowseConfig.clicked.connect(self.browseConfig)

        #On pré-coche l'entrée automatique
        self.radioButtonAuto.setChecked(True)

    def autoEntry(self):

        self.pushButtonBrowseDataDir.setEnabled(True)
        self.pushButtonBrowseInfo.setEnabled(False)
        self.pushButtonBrowsePressures.setEnabled(False)
        self.pushButtonBrowseTemperatures.setEnabled(False)
        self.pushButtonBrowseNotice.setEnabled(False)
        self.pushButtonBrowseConfig.setEnabled(False)

        self.lineEditDataDir.setReadOnly(False)
        self.lineEditInfo.setReadOnly(True)
        self.lineEditPressures.setReadOnly(True)
        self.lineEditTemperatures.setReadOnly(True)
        self.lineEditConfig.setReadOnly(True)
        self.lineEditNotice.setReadOnly(True)

    def manualEntry(self):

        self.pushButtonBrowseDataDir.setEnabled(False)
        self.pushButtonBrowseInfo.setEnabled(True)
        self.pushButtonBrowsePressures.setEnabled(True)
        self.pushButtonBrowseTemperatures.setEnabled(True)
        self.pushButtonBrowseNotice.setEnabled(True)
        self.pushButtonBrowseConfig.setEnabled(True)

        self.lineEditDataDir.setReadOnly(True)
        self.lineEditInfo.setReadOnly(False)
        self.lineEditPressures.setReadOnly(False)
        self.lineEditTemperatures.setReadOnly(False)
        self.lineEditConfig.setReadOnly(False)
        self.lineEditNotice.setReadOnly(False)


    def browseDataDir(self):

        dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Point Data Directory")
        
        if dirPath:

            self.lineEditDataDir.setText(dirPath)
            files = list(filter(('.DS_Store').__ne__, os.listdir(dirPath))) 

            nPath = 0

            for file in files : 

                if re.search('info', file):
                    filePath = os.path.join(dirPath, file)
                    try :
                        self.lineEditInfo.setText(filePath) 
                        df = pd.read_csv(filePath, header=None, index_col=0)
                        if not self.lineEditName.text(): 
                            #on n'importe pas le nom si un autre nom a été choisi par l'utilisateur
                            self.lineEditName.setText(df.iloc[0].at[1])
                        self.lineEditPressureSensor.setText(df.iloc[1].at[1])
                        self.lineEditShaft.setText(df.iloc[2].at[1])
                        nPath += 1
                    except :
                        self.lineEditInfo.setText('') 

                if re.search('.png', file):
                    try :
                        filePath = os.path.join(dirPath, file)
                        self.lineEditConfig.setText(filePath) 
                        nPath += 1
                    except :
                        pass

                if re.search('notice', file):
                    try :
                        filePath = os.path.join(dirPath, file)
                        self.lineEditNotice.setText(filePath) 
                        nPath += 1
                    except :
                        pass

                if re.search('P_', file):
                    try :
                        filePath = os.path.join(dirPath, file)
                        self.lineEditPressures.setText(filePath) 
                        nPath += 1
                    except : 
                        pass

                if re.search('T_', file):
                    try : 
                        filePath = os.path.join(dirPath, file)
                        self.lineEditTemperatures.setText(filePath) 
                        nPath += 1
                    except :
                        pass
            
            if nPath<5 : 
                displayWarningMessage(f'Only {nPath} lines have been successfully filled. Please fill in missing information manually')
                self.lineEditDataDir.setText('')
                self.radioButtonManual.setChecked(True)


    def browseInfo(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Info File")[0]
        if filePath:
            self.lineEditInfo.setText(filePath) 
            try :
                df = pd.read_csv(filePath, header=None, index_col=0)
                if not self.lineEditName.text(): 
                #on n'importe pas le nom si un autre nom a été choisi par l'utilisateur
                    self.lineEditName.setText(df.iloc[0].at[1])
                self.lineEditPressureSensor.setText(df.iloc[1].at[1])
                self.lineEditShaft.setText(df.iloc[2].at[1])
            except KeyError as e:
                print(f"KeyError : {e}")
                displayCriticalMessage('Invalid Info File', 'Please check "Application Messages" for further information')
                self.lineEditInfo.setText('') 
            except Exception as e :
                raise e
            except pd.errors.ParserError :
                raise CustomError("Parser error. You might have selected the wrong file")
    
    def browsePressures(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Pressure Measures File")[0]
        if filePath:
            self.lineEditPressures.setText(filePath) 
    
    def browseTemperatures(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Temperature Measures File")[0]
        if filePath:
            self.lineEditTemperatures.setText(filePath) 
    
    def browseNotice(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Notice File")[0]
        if filePath:
            self.lineEditNotice.setText(filePath) 
    
    def browseConfig(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Configuration File")[0]
        if filePath:
            self.lineEditConfig.setText(filePath) 
    
    def getPointInfo(self):
        name = self.lineEditName.text()
        infofile = self.lineEditInfo.text()
        prawfile = self.lineEditPressures.text()
        trawfile = self.lineEditTemperatures.text()
        noticefile = self.lineEditNotice.text()
        configfile = self.lineEditConfig.text()
        return name, infofile, prawfile, trawfile, noticefile, configfile

"""
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = DialogImportPoint()
    mainWin.show()
    sys.exit(app.exec_())
"""