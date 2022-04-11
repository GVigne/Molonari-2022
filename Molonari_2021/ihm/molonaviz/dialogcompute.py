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

        #self.permeabilityValidator = QtGui.QDoubleValidator(0.0, 5.0, 2)
        #self.lineEditKDirect.setValidator(self.permeabilityValidator)
        #self.lineEditKMax.setValidator(self.permeabilityValidator)
        #self.lineEditKMin.setValidator(self.permeabilityValidator)

        #for i in range(50, 151, 5):
            # self.spinBoxNCellsDirect.addItem(f'{i}')
            #self.comboBoxNCellsMCMC.addItem(f'{i}')
        
        self.setDefaultValues()
        #self.tableWidge.horizontalHeader().setStretchLastSection(True) # 单元横向高度自适应。铺满窗口
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

        #self.directModelLineEdits = [self.lineEditKDirect, self.lineEditPorosityDirect, self.lineEditThermalConductivityDirect,
        #    self.lineEditThermalCapacityDirect]

        self.MCMCLineEdits = [self.lineEditMaxIterMCMC, 
            self.lineEditKMin, self.lineEditKMax, self.lineEditMoinsLog10KSigma,
            self.lineEditPorosityMin, self.lineEditPorosityMax, self.lineEditPorositySigma,
            self.lineEditThermalConductivityMin, self.lineEditThermalConductivityMax, self.lineEditThermalConductivitySigma,
            self.lineEditThermalCapacityMin, self.lineEditThermalCapacityMax, self.lineEditThermalCapacitySigma]

        #self.ifButtonDirect.clicked.connect(self.inputDirect)

        #self.ifButtonMCMC.clicked.connect(self.inputMCMC)
        self.pushButtonUpdate.clicked.connect(self.change_showdb)
        self.groupBoxMCMC.clicked.connect(self.inputMCMC)
        #self.pushButtonAddLayers.clicked.connect(self.AddLayers_nb) # layers<=10 à priori
        #self.pushButtonDeleLayers.clicked.connect(self.DeleLayers_nb)

        #On pré-coche le modèle direct
        #self.ifButtonDirect.setChecked(True)
        
        #tableau initial
        self.showdb()

        #self.pushButtonDirect.clicked.connect(self.getInputDirectModel)
        #self.checkBox.setChecked(True)
        #self.checkBox.stateChanged.connect(self.getInputDirectModel)
        
        self.pushButtonMCMC.clicked.connect(self.getInputMCMC)

        self.pushButtonRestoreDefault.clicked.connect(self.setDefaultValues)
        self.pushButtonRestoreDefault.setToolTip("All parameters will be set to default value")

        #self.labelMoinsLog10KDirect.setToolTip("Please enter -log10K, K being permeability")
        self.labelsigmaK.setToolTip(f"WARNING : sigma applies to -log<sub>10<sub>K")
        
    def spinBoxNCellsDirect_cb(self):
        return self.spinBoxNCellsDirect.value()

    def spinBoxNLayersDirect_cb(self):
        return self.spinBoxNLayersDirect.value()
        
    #def AddLayers_nb(self):
        #n = int(self.lineEditNumberLayers.text()) + 1
        #self.lineEditNumberLayers.setText(str(n))
        
        #return self.change_showdb()
    
    #def DeleLayers_nb(self):
        #n = int(self.lineEditNumberLayers.text()) - 1
        #self.lineEditNumberLayers.setText(str(n))
        
        return self.change_showdb()
 
    #可自定义表格
    #def table(self): 
        #self.tableWidget.setColumnCount(6)
        #self.tableWidget.setRowCount(11)
        #j = 0#第几行（从0开始）
        #i = 0#第几列（从0开始）
        #Value = "0"#内容
        #self.tableWidget.setItem(j, i, QTableWidgetItem(Value))#设置j行i列的内容为Value
        #self.tableWidget.setColumnWidth(j,80)#设置j列的宽度
        #self.tableWidget.setRowHeight(i,50)#设置i行的高度
        #self.tableWidget.verticalHeader().setVisible(False)#隐藏垂直表头
        #self.tableWidget.horizontalHeader().setVisible(False)#隐藏水平表头
        
    #数据展示在表格上
    def showdb(self): ### 设置默认Direct表格
        #query = QSqlQuery()
        #if query.exec('select * from person ORDER BY ID  DESC limit {},10'.format(str(n))):
            #id_index = query.record().indexOf('id')
            #name_index = query.record().indexOf('name')
            #age_index = query.record().indexOf('age')
            #sex_index = query.record().indexOf('sex')
            #nr_index = query.record().indexOf('nr')
            #db = []
            #while query.next():
                #id = query.value(id_index)
                #name = query.value(name_index)
                #age = query.value(age_index)
                #sex = query.value(sex_index)
                #nr = query.value(nr_index)
                # print(id,name,age,sex,nr)
                #db.append((id,name,age,sex,nr))
            # print(db) 
        #self.tableWidget.clearContents()#清除所有数据--不包括标题头
        #if n == 0:
            #self.label_8.setText('1')
            #self.current_page = 1
        #else:
            #self.label_8.setText(str(self.current_page))    
        
        #self.tbnum(0)   
        
        # spinBoxNCellsDirect
        self.spinBoxNCellsDirect.setValue(100)
        # self.spinBoxNCellsDirect.setWrapping(True)
        
        # spinBoxNLayersDirect
        #self.lineEditNumberLayers.setText("3")
        # self.spinBoxNLayersDirect.setWrapping(True)
        
        #self.ifButtonDirect.setDefault(True)
        #self.pushButtonDirect.setEnabled(True)
        self.spinBoxNCellsDirect.setEnabled(True)
        self.spinBoxNLayersDirect.setEnabled(True)
        
        row = self.spinBoxNLayersDirect.value() 
        #col = 5
        #row = 3 
        for i in range(row):
    
            self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
            self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
            self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                    
        self.tableWidget.setItem(0, 0, QTableWidgetItem("21"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("31"))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("46"))
        
        #for i in range (1,10):
            #if i > 2:
                #self.tableWidget.hideRow(i)
            #else:
                #self.tableWidget.showRow(i)

        #for i, j in zip(range(1, 10), range(1, 5)):
            #Value = "0"
            #self.spinBoxNCellsDirect.valueChanged.connect(self.change_table)
            #return self.tableWidget.setItem(i, j, QTableWidgetItem(Value))
        #for i in range(1,10): #i是行数
            # print(db[i])
            # print(db[i][0])
            #self.tableWidget.setItem(0, 0, QTableWidgetItem(0))
            #self.tableWidget.setItem(0, 1, QTableWidgetItem(0))
            #self.tableWidget.setItem(0, 2, QTableWidgetItem(0))
            #self.tableWidget.setItem(0, 3, QTableWidgetItem(0))
            #self.tableWidget.setItem(i, 4, QTableWidgetItem(db[i][4]))#设置j行i列的内容为Value    
    
    # 第一次执行命令：我们有一个初始化的表格 但用户可先设自己想要的layers 然后第一层和第二层深度, 基于此建立的表格应自动生成对应数据。
    # 但用户若又改变主意（仍然还未执行第一次命令运行），应尽可能最大化保留信息，保留上次所改数据，应用到新增层等等
    # 若增加layer 应在后面增加，若减少layer 应从第一层开始删减
    def change_showdb(self): # changer le nombre de lignes selon spinBoxNLayersDirect
        #if self.ifButtonDirect.isChecked():
            #self.pushButtonDirect.setEnabled(True)
            #self.pushButtonMCMC.setEnabled(False)
            #self.spinBoxNCellsDirect.setEnabled(True)
            #self.spinBoxNLayersDirect.setEnabled(True)
            #self.comboBoxNCellsMCMC.setEnabled(False)
            
            #for lineEdit in self.MCMCLineEdits :
                #lineEdit.setReadOnly(True)
            
            row = int(self.spinBoxNLayersDirect.value())
            #col = 5
                
            self.tableWidget.setRowCount(row)
            self.tableWidget.setColumnCount(5)
            
            for i in range(row):
    
                #self.tableWidget.setItem(i, 0, QTableWidgetItem("0"))
                self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
                self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
                self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                
                #self.tableWidget.setItem(0, 0, QTableWidgetItem("6"))
                #self.tableWidget.setItem(row-1, 0, QTableWidgetItem("46"))
                
            for j in range (row):
                val = int(6+(40/row)*(j+1))
                self.tableWidget.setItem(j, 0, QTableWidgetItem(str(val)))
            
            #if row == 1:
                #self.tableWidget.setItem(0, 0, QTableWidgetItem("46"))
                
            #if row == 2: # par default deltaH = 6
                #self.tableWidget.setItem(0, 0, QTableWidgetItem("26"))
                #self.tableWidget.setItem(1, 0, QTableWidgetItem("46"))
                
            #if row == 3:
                #self.tableWidget.setItem(0, 0, QTableWidgetItem("19.3"))
                #self.tableWidget.setItem(1, 0, QTableWidgetItem("32.3")) 
                #self.tableWidget.setItem(2, 0, QTableWidgetItem("46"))   
        
            #cols = self.spinBoxNLayersDirect.value() - 1
            #for i in range(row):
                #for j in range(col):
                    #Value = "0"
                    #self.tableWidget.setItem(i, j, QTableWidgetItem(Value))
            #for k in range (1,10):
                #if k > row:
                    #self.tableWidget.hideRow(k)
                #else:
                    #self.tableWidget.showRow(k)
            
        #cols = self.spinBoxNLayersDirect.value()
        #for i in range (1,10):
            #if i > cols:
                #self.tableWidget.hideRow(i)
            #else:
                #self.tableWidget.showRow(i)
    
    '''
    def change_table(self): # changer le nombre de lignes selon spinBoxNLayersDirect
        cols = self.spinBoxNLayersDirect.value()
        if(cols == 1):
            # 行隐藏
            self.tableWidget.hideRow(1)
            self.tableWidget.hideRow(2)

        elif(cols == 2):
            self.tableWidget.showRow(1)
            self.tableWidget.hideRow(2)
            
        elif(cols ==3):
            # 行显示
            self.tableWidget.showRow(1)
            self.tableWidget.showRow(2)

    # QSpinBox值改变事件监听
    self.spinBox.valueChanged.connect(self.change_table)
    '''
    #def btnSetHeader_clicked(self):
        #headerList = ["Depth_bottom", "Permeability", "Porosity", "Sediment Thermal Conductivity (W/m/K)", "Solid Volumetric Thermal Capacity (J/m^3/K)"]
        #self.tableWidget.setColumnCount(len(headerList))
        #for i in range(len(headerList)):
            #headerItem = QTableWidgetItem(headerList[i])
            #font = headerItem.font()
            #font.setPointSize(11)
            #headerItem.setFont(font)
            #headerItem.setBackground(QBrush(Qt.red))
            #self.tableWidget.setHorizontalHeaderItem(i, headerItem)
    
    #def btnSetRow_clicked(self):
        #self.tableWidget.setRowCount(self.spinBoxNLayersDirect.value())
        #self.tableWidget.setAlternatingRowColors(self.chkBoxBackground.isChecked())
    
    #def setDefaultTableDirect(self):    
    # Direct model
        #for i, j in zip(range(1, 10), range(1, 5)):
            #Value = 0
            #self.spinBox.valueChanged.connect(self.change_table)
            #return self.tableWidget.setItem(i, j, QTableWidgetItem(Value))
            
    def setDefaultValues(self):
        
        # Direct model
        #self.lineEditKDirect.setText('1e-5')
        #self.lineEditPorosityDirect.setText('0.15')
        #self.lineEditThermalConductivityDirect.setText('3.4')
        #self.lineEditThermalCapacityDirect.setText('5e6')
        # self.spinBoxNCellsDirect.setCurrentIndex(10) #100 cellules

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

        #self.comboBoxNCellsMCMC.setCurrentIndex(10) #100 cellules

        self.lineEditQuantiles.setText('0.05,0.5,0.95')

    #directModel change selon le dernier resultat de Inversion
    def inputDirect(self):
        
        #self.pushButtonDirect.clicked.connect(self.getInputDirectModel)

        #self.pushButtonDirect.setEnabled(True)
        #self.pushButtonMCMC.setEnabled(False)

        self.spinBoxNCellsDirect.setEnabled(True)
        self.spinBoxNLayersDirect.setEnabled(True)
        #self.comboBoxNCellsMCMC.setEnabled(False)
        
        #for lineEdit in self.directModelLineEdits :
            #lineEdit.setReadOnly(False)
        for lineEdit in self.MCMCLineEdits :
            lineEdit.setReadOnly(True)


    def inputMCMC(self):
        
        #self.ifButtonDirect.toggle()
        #self.pushButtonDirect.setEnabled(False)
        self.pushButtonMCMC.setEnabled(True)

        self.spinBoxNCellsDirect.setEnabled(False)
        #self.spinBoxNLayersDirect.setEnabled(False)
        #self.comboBoxNCellsMCMC.setEnabled(True)

        #for lineEdit in self.directModelLineEdits :
            #lineEdit.setReadOnly(True)
            
        for lineEdit in self.MCMCLineEdits :
            lineEdit.setReadOnly(False)     
        
    #def getInputDirectModel(self):
        #moinslog10K = -log10(float(self.lineEditKDirect.text()))
        #n = float(self.lineEditPorosityDirect.text())
        #lambda_s = float(self.lineEditThermalConductivityDirect.text())
        #rhos_cs = float(self.lineEditThermalCapacityDirect.text())
        #nb_cells = int(self.spinBoxNCellsDirect.value())
        #self.done(10)
        #return (moinslog10K, n, lambda_s, rhos_cs), nb_cells
        #return self.change_showdb()

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