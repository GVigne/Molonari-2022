import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from math import log10
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem

From_DialogCompute = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcompute.ui"))[0]

class DialogCompute(QtWidgets.QDialog, From_DialogCompute):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogCompute, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)

        self.setMouseTracking(True)
        
        self.setDefaultValues()
        
        # spinBoxNCellsDirect
        self.spinBoxNCellsDirect.setRange(0, 200)
        self.spinBoxNCellsDirect.setSingleStep(10)
        self.spinBoxNCellsDirect.setValue(100)
        # self.spinBoxNCellsDirect.setWrapping(True)
        
        # spinBoxNLayersDirect
        self.spinBoxNLayersDirect.setRange(0, 10)
        self.spinBoxNLayersDirect.setSingleStep(1)
        self.spinBoxNLayersDirect.setValue(3)
        # self.spinBoxNLayersDirect.setWrapping(True)

        self.spinBoxNCellsDirect.valueChanged.connect(self.spinBoxNCellsDirect_cb)
        self.spinBoxNLayersDirect.valueChanged.connect(self.spinBoxNLayersDirect_cb)

        self.MCMCLineEdits = [self.lineEditMaxIterMCMC, 
            self.lineEditKMin, self.lineEditKMax, self.lineEditMoinsLog10KSigma,
            self.lineEditPorosityMin, self.lineEditPorosityMax, self.lineEditPorositySigma,
            self.lineEditThermalConductivityMin, self.lineEditThermalConductivityMax, self.lineEditThermalConductivitySigma,
            self.lineEditThermalCapacityMin, self.lineEditThermalCapacityMax, self.lineEditThermalCapacitySigma]

        self.pushButtonUpdate.clicked.connect(self.change_showdb)
        self.groupBoxMCMC.clicked.connect(self.inputMCMC)
        
        # Show the default table
        self.showdb()

        self.pushButtonMCMC.clicked.connect(self.getInputMCMC)

        self.pushButtonRestoreDefault.clicked.connect(self.setDefaultValues)
        self.pushButtonRestoreDefault.setToolTip("All parameters will be set to default value")

        # self.labelMoinsLog10KDirect.setToolTip("Please enter -log10K, K being permeability")
        self.labelsigmaK.setToolTip(f"WARNING : sigma applies to -log<sub>10<sub>K")
        
    def spinBoxNCellsDirect_cb(self):
        return self.spinBoxNCellsDirect.value()

    def spinBoxNLayersDirect_cb(self):
        return self.spinBoxNLayersDirect.value()
        
    # Set the default table
    def showdb(self): 
        
        # spinBoxNCellsDirect
        self.spinBoxNCellsDirect.setValue(100)
        self.spinBoxNCellsDirect.setEnabled(True)
        self.spinBoxNLayersDirect.setEnabled(True)
        
        row = self.spinBoxNLayersDirect.value() 
        # col always = 5 
        # the default number of rows = 3
        for i in range(row):
    
            self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
            self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
            self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                    
        self.tableWidget.setItem(0, 0, QTableWidgetItem("21"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("31"))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("46"))
    
    # Change the number of rows according to spinBoxNLayersDirect    
    def change_showdb(self): 
            
            row = int(self.spinBoxNLayersDirect.value())
            # col = 5
                
            self.tableWidget.setRowCount(row)
            self.tableWidget.setColumnCount(5)
            
            for i in range(row):
    
                self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
                self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
                self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                
            for j in range (row):
                val = int(6+(40/row)*(j+1))
                self.tableWidget.setItem(j, 0, QTableWidgetItem(str(val)))
       
    def setDefaultValues(self):
        
        # MCMC
        self.lineEditMaxIterMCMC.setText('5000')

        self.lineEditKMin.setText('1e-2')
        self.lineEditKMax.setText('1e-7')
        self.lineEditMoinsLog10KSigma.setText('0.01')

        self.lineEditPorosityMin.setText('0.01')
        self.lineEditPorosityMax.setText('0.25')
        self.lineEditPorositySigma.setText('0.01')

        self.lineEditThermalConductivityMin.setText('1')
        self.lineEditThermalConductivityMax.setText('5')
        self.lineEditThermalConductivitySigma.setText('0.05')

        self.lineEditThermalCapacityMin.setText('5e5')
        self.lineEditThermalCapacityMax.setText('1e7')
        self.lineEditThermalCapacitySigma.setText('1e5')

        self.lineEditQuantiles.setText('0.05,0.5,0.95')

    # directModel changes according to the previous result of Inversion 
    # So need to modify the codes in change_showdb when we have the result of Group calcul

    def inputMCMC(self):
        
        self.pushButtonMCMC.setEnabled(True)

        self.spinBoxNCellsDirect.setEnabled(False)
            
        for lineEdit in self.MCMCLineEdits :
            lineEdit.setReadOnly(False)     

    def getInputMCMC(self):

        nb_iter = int(self.lineEditMaxIterMCMC.text())
        nb_cells = self.spinBoxNCellsDirect.value()

        moins10logKmin = -log10(float(self.lineEditKMin.text()))
        moins10logKmax = -log10(float(self.lineEditKMax.text()))
        moins10logKsigma = -log10(float(self.lineEditMoinsLog10KSigma.text()))

        nmin = float(self.lineEditPorosityMin.text())
        nmax = float(self.lineEditPorosityMax.text())
        nsigma = float(self.lineEditPorositySigma.text())

        lambda_s_min = float(self.lineEditThermalConductivityMin.text())
        lambda_s_max = float(self.lineEditThermalConductivityMax.text())
        lambda_s_sigma = float(self.lineEditThermalConductivitySigma.text())

        rhos_cs_min = float(self.lineEditThermalCapacityMin.text())
        rhos_cs_max = float(self.lineEditThermalCapacityMax.text())
        rhos_cs_sigma = float(self.lineEditThermalCapacitySigma.text())

        priors = {
        "moinslog10K": ((moins10logKmin, moins10logKmax), moins10logKsigma),
        "n": ((nmin, nmax), nsigma),
        "lambda_s": ((lambda_s_min, lambda_s_max), lambda_s_sigma),
        "rhos_cs": ((rhos_cs_min, rhos_cs_max), rhos_cs_sigma) }

        quantiles = self.lineEditQuantiles.text()
        quantiles = quantiles.split(",")
        quantiles = tuple(quantiles)
        quantiles = [float(quantile) for quantile in quantiles]
        
        self.done(1)
        return nb_iter, priors, nb_cells, quantiles


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = DialogCompute()
    mainWin.show()
    sys.exit(app.exec_())