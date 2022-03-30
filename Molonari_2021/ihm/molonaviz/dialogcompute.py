import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from math import log10

From_DialogCompute = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcompute.ui"))[0]

class DialogCompute(QtWidgets.QDialog, From_DialogCompute):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogCompute, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)

        self.setMouseTracking(True)

        #self.permeabilityValidator = QtGui.QDoubleValidator(0.0, 5.0, 2)
        #self.lineEditKDirect.setValidator(self.permeabilityValidator)
        #self.lineEditKMax.setValidator(self.permeabilityValidator)
        #self.lineEditKMin.setValidator(self.permeabilityValidator)

        for i in range(50, 151, 5):
            self.comboBoxNCellsDirect.addItem(f'{i}')
            self.comboBoxNCellsMCMC.addItem(f'{i}')
        
        self.setDefaultValues()

        self.directModelLineEdits = [self.lineEditKDirect, self.lineEditPorosityDirect, self.lineEditThermalConductivityDirect,
            self.lineEditThermalCapacityDirect]

        self.MCMCLineEdits = [self.lineEditMaxIterMCMC, 
            self.lineEditKMin, self.lineEditKMax, self.lineEditMoinsLog10KSigma,
            self.lineEditPorosityMin, self.lineEditPorosityMax, self.lineEditPorositySigma,
            self.lineEditThermalConductivityMin, self.lineEditThermalConductivityMax, self.lineEditThermalConductivitySigma,
            self.lineEditThermalCapacityMin, self.lineEditThermalCapacityMax, self.lineEditThermalCapacitySigma]

        self.radioButtonDirect.toggled.connect(self.inputDirect)
        self.radioButtonMCMC.toggled.connect(self.inputMCMC)

        #On pré-coche le modèle direct
        self.radioButtonDirect.setChecked(True)

        self.pushButtonDirect.clicked.connect(self.getInputDirectModel)
        self.pushButtonMCMC.clicked.connect(self.getInputMCMC)

        self.pushButtonRestoreDefault.clicked.connect(self.setDefaultValues)
        self.pushButtonRestoreDefault.setToolTip("All parameters will be set to default value")

        #self.labelMoinsLog10KDirect.setToolTip("Please enter -log10K, K being permeability")
        self.labelsigmaK.setToolTip(f"WARNING : sigma applies to -log<sub>10<sub>K")

    def setDefaultValues(self):

        # Direct model
        self.lineEditKDirect.setText('1e-5')
        self.lineEditPorosityDirect.setText('0.15')
        self.lineEditThermalConductivityDirect.setText('3.4')
        self.lineEditThermalCapacityDirect.setText('5e6')
        self.comboBoxNCellsDirect.setCurrentIndex(10) #100 cellules

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

        self.comboBoxNCellsMCMC.setCurrentIndex(10) #100 cellules

        self.lineEditQuantiles.setText('0.05,0.5,0.95')


    def inputDirect(self):

        self.pushButtonDirect.setEnabled(True)
        self.pushButtonMCMC.setEnabled(False)

        self.comboBoxNCellsDirect.setEnabled(True)
        self.comboBoxNCellsMCMC.setEnabled(False)

        for lineEdit in self.directModelLineEdits :
            lineEdit.setReadOnly(False)
    
        for lineEdit in self.MCMCLineEdits :
            lineEdit.setReadOnly(True)


    def inputMCMC(self):

        self.pushButtonDirect.setEnabled(False)
        self.pushButtonMCMC.setEnabled(True)

        self.comboBoxNCellsDirect.setEnabled(False)
        self.comboBoxNCellsMCMC.setEnabled(True)

        for lineEdit in self.directModelLineEdits :
            lineEdit.setReadOnly(True)
            
        for lineEdit in self.MCMCLineEdits :
            lineEdit.setReadOnly(False)



    def getInputDirectModel(self):
        moinslog10K = -log10(float(self.lineEditKDirect.text()))
        n = float(self.lineEditPorosityDirect.text())
        lambda_s = float(self.lineEditThermalConductivityDirect.text())
        rhos_cs = float(self.lineEditThermalCapacityDirect.text())
        nb_cells = int(self.comboBoxNCellsDirect.currentText())
        self.done(10)
        return (moinslog10K, n, lambda_s, rhos_cs), nb_cells

    def getInputMCMC(self):

        nb_iter = int(self.lineEditMaxIterMCMC.text())
        nb_cells = int(self.comboBoxNCellsMCMC.currentText())

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