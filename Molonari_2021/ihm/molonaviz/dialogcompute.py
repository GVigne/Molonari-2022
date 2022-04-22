import sys
import os
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from math import log10
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from queue import Queue
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery

#from mainwindow import mainWin

From_DialogCompute = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcompute.ui"))[0]

class DialogCompute(QtWidgets.QDialog, From_DialogCompute):
    
    def __init__(self,pointName):
        # Call constructor of parent classes
        super(DialogCompute, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.pointName = pointName
        
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

        self.MCMCLineEdits = [self.lineEditMaxIterMCMC, 
            self.lineEditKMin, self.lineEditKMax, self.lineEditMoinsLog10KSigma,
            self.lineEditPorosityMin, self.lineEditPorosityMax, self.lineEditPorositySigma,
            self.lineEditThermalConductivityMin, self.lineEditThermalConductivityMax, self.lineEditThermalConductivitySigma,
            self.lineEditThermalCapacityMin, self.lineEditThermalCapacityMax, self.lineEditThermalCapacitySigma]

        self.pushButtonUpdate.clicked.connect(self.change_showdb)
        
        # Show the default table
        self.showdb()

        self.pushButtonRun.clicked.connect(self.run)

        self.pushButtonRestoreDefault.clicked.connect(self.setDefaultValues)
        self.pushButtonRestoreDefault.setToolTip("All parameters will be set to default value")

        # self.labelMoinsLog10KDirect.setToolTip("Please enter -log10K, K being permeability")
        self.labelsigmaK.setToolTip(f"WARNING : sigma applies to -log<sub>10<sub>K")
        
        self.pushButtonUpdate.setToolTip("Click to update the table after having decided the number of layers")
        self.pushButtonRun.setToolTip("Run MCMC if 'Execute inversion before' is checked, otherwise run Direct Model")
        self.buttonBox.setToolTip("Close the window")
        
        item0 = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item0)
        item0.setText('Depth_bottom (cm)')
        item0.setToolTip('Depth of each layer. By default, it shows the distance between river bed and the middle of each layer')
        
        item1 = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item1)
        item1.setText('Permeability (m/s)')
        item1.setToolTip('Measure that represents the ability of water to move through a rock')
        
        item2 = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item2)
        item2.setText('Porosity')
        item2.setToolTip('Percentage of void space in a rock')

        item3 = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item3)
        item3.setText('SediThermCon (W/m/K)')
        item3.setToolTip('A key factor in basin modelling')
        
        item4 = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item4)
        item4.setText('SolVolThermCap (J/m^3/K)')
        item4.setToolTip('Solid Volumetric Thermal Capacity: heat capacity of a sample of the substance divided by the volume of the sample')
    
    #Find the values related to point_id in different tables
    def searchTable(tableName = None, point_id = None):
        query_test.exec_(f"SELECT 1 FROM {tableName} WHERE PointKey = {point_id}")
        if not (query_test.first()): 
            return False
        
        i = 0
        while i<row:
            #Read the data
            query_test.exec_(f"SELECT 1 FROM {tableName} WHERE PointKey = {point_id} AND Layer = {i+1}")
            if not query_test.first():
                break
            permeability = query_test.value(1)
            sediThermCon = query_test.value(2)
            porosity = query_test.value(3)
            layer = query_test.value(4)
            #Find the depthBed
            query_new = QSqlQuery()
            query_new.exec_("SELECT DepthBed FROM Layer WHERE id = {layer}")
            query_new.first()
            depth_bed = query_new.value(2)
            #Insert the values
            self.tableWidget.setItem(i, 0, QTableWidgetItem(depth_bed))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(permeability))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(porosity))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(sediThermCon))
            self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
            i+=1  
        return True    
    
    # Set the default table
    def showdb(self): 
        
        # spinBoxNCellsDirect
        self.spinBoxNCellsDirect.setValue(100)
        
        row = self.spinBoxNLayersDirect.value() 
        # col always = 5 
        # the default number of rows = 3
        
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(5)
        
        for i in range(row):
    
            self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
            self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
            self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
            self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                    
        self.tableWidget.setItem(0, 0, QTableWidgetItem("21"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("31"))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("46"))
        
        for k in range(10):
                if k > row - 1:
                    self.tableWidget.hideRow(k)
                else:
                    self.tableWidget.showRow(k)
        #Open the database
        db_point = QSqlDatabase.addDatabase("QSQLITE")
        db_point.setDatabaseName(r"C:\Users\fujia\Documents\GitHub\Molonari-2022\Molonari_2021\studies\study_2022\molonari_study_2022 .sqlite")
        if not db_point.open():
            print("Error: Cannot open databse")
        #Find the id related to the SamplingPoint
        query_test = QSqlQuery()
        query_test.exec_(f"SELECT id FROM Point WHERE SamplingPoint = {self.pointName}")
        query_test.first()
        point_id = query_test.value(0)
        #Find the bestParameter related to the id found

        query_test.exec_(f"SELECT 1 FROM BestParameters WHERE PointKey = {point_id}")
        if not (query_test.first()): 
            query_test.exec_(f"SELECT 1 FROM ParametersDistribution WHERE PointKey = {point_id}")
            if not (query_test.first()): 
                print("Error, point not found")
                return
        
            i = 0
            while i<row:
                #Read the data
                query_test.exec_(f"SELECT 1 FROM ParametersDistribution WHERE PointKey = {point_id} AND Layer = {i+1}")
                if not query_test.first():
                    break
                permeability = query_test.value(1)
                sediThermCon = query_test.value(2)
                porosity = query_test.value(3)
                layer = query_test.value(4)
                #Find the depthBed
                query_new = QSqlQuery()
                query_new.exec_("SELECT DepthBed FROM Layer WHERE id = {layer}")
                query_new.first()
                depth_bed = query_new.value(2)
                #Insert the values
                self.tableWidget.setItem(i, 0, QTableWidgetItem(depth_bed))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(permeability))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(porosity))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(sediThermCon))
                self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                i+=1
            db_point.close()
            return  
        
        i = 0
        while i<row:
            #Read the data
            query_test.exec_(f"SELECT 1 FROM BestParameters WHERE PointKey = {point_id} AND Layer = {i+1}")
            if not query_test.first():
                break
            permeability = query_test.value(1)
            sediThermCon = query_test.value(2)
            porosity = query_test.value(3)
            layer = query_test.value(4)
            #Find the depthBed
            query_new = QSqlQuery()
            query_new.exec_("SELECT DepthBed FROM Layer WHERE id = {layer}")
            query_new.first()
            depth_bed = query_new.value(2)
            #Insert the values
            self.tableWidget.setItem(i, 0, QTableWidgetItem(depth_bed))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(permeability))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(porosity))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(sediThermCon))
            self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
            i+=1  
        '''
        if not (self.searchTable(tableName = "BestParameters",point_id = point_id)):
            if not (self.searchTable(tableName = "ParametersDistribution",point_id = point_id)):
                print("Error, point not found")
        '''
                                     
        db_point.close()
         
    #    self.readSQL()
    
    # Change the number of rows according to spinBoxNLayersDirect    
    def change_showdb(self): 
            
            row = int(self.spinBoxNLayersDirect.value())
            # col = 5
                
            self.tableWidget.setRowCount(10)
            self.tableWidget.setColumnCount(5)
            
            for i in range(row):
    
                self.tableWidget.setItem(i, 1, QTableWidgetItem("1e-5"))
                self.tableWidget.setItem(i, 2, QTableWidgetItem("0.15"))
                self.tableWidget.setItem(i, 3, QTableWidgetItem("3.4"))
                self.tableWidget.setItem(i, 4, QTableWidgetItem("5e6"))
                
            for j in range (row):
                val = int(6+(40/row)*(j+1))
                self.tableWidget.setItem(j, 0, QTableWidgetItem(str(val)))
                
            for k in range(10):
                if k > row - 1:
                    self.tableWidget.hideRow(k)
                else:
                    self.tableWidget.showRow(k)

       
    def setDefaultValues(self):
        
        # Direct model
        #self.showdb()
        
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

    def getInputDirectModel(self):
        
        nb_cells = self.spinBoxNCellsDirect.value()
        
        row = int(self.spinBoxNLayersDirect.value())
        
        for i in range (row):
            
            moinslog10K = -log10(float(self.tableWidget.item(i, 1).text()))
            n = float(self.tableWidget.item(i, 2).text())
            lambda_s = float(self.tableWidget.item(i, 3).text())
            rhos_cs = float(self.tableWidget.item(i, 4).text())
            return (moinslog10K, n, lambda_s, rhos_cs), nb_cells


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
        
        return nb_iter, priors, nb_cells, quantiles
    
    '''
    def writeSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        self.sql = "molonari_slqdb.sqlite"
        #self.con = QSqlDatabase.addDatabase("QSQLITE", connectionName = "qsldatabase")
        #self.con.setDatabaseName(self.sql)
        # Remove the previous measures table (if so)
        dropTableQuery = QSqlQuery() 

        dropTableQuery.exec("DROP TABLE IF EXISTS LastParameters")
        
        dropTableQuery.finish()
        
        # Create the table（LastParameters） for storing the measures (layer, Depth_bed, -log10K_best, lambda_s_best, n_best, Cap)
        createTableQuery = QSqlQuery()
        createTableQuery.exec(
            """
            CREATE TABLE IF NOT EXISTS LastParameters (
                Layer INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                Depth_bed FLOAT,
                -log10K_best FLOAT,
                lambda_s_best FLOAT,
                n_best FLOAT,
                Cap FLOAT           
            )
            """
        )
        # Construct the dynamic insert SQL request and execute it
        insertDataQuery = QSqlQuery()
        insertDataQuery.prepare(
            """
            INSERT INTO LastParameters (
                Depth_bed,
                -log10K_best,
                lambda_s_best,
                n_best,
                Cap
            )
            VALUES (?, ?, ?, ?, ?)
            """
        )

        for i in range(df.shape[0]):
            val = tuple(df.iloc[i])
            insertDataQuery.addBindValue(str(val[0]))
            insertDataQuery.addBindValue(str(val[1]))
            insertDataQuery.addBindValue(str(val[2]))
            insertDataQuery.addBindValue(str(val[3]))
            insertDataQuery.addBindValue(str(val[4]))
            insertDataQuery.exec()
    
    def readSQL(self):
        """
        Read the SQL database and display measures
        """
        #print("Tables in the SQL Database:", self.con.tables())
        
        # Read the database and print its content using SELECT
        selectDataQuery = QSqlQuery()
        
        selectDataQuery.exec("SELECT -log10K_best, lambda_s_best, n_best, Cap, Depth_bed FROM LastParameters join Layer on Layer.ID = LastParameters.Layer")
        while selectDataQuery.next():
            print(selectDataQuery.value(0))
            print(selectDataQuery.value(1))
            print(selectDataQuery.value(2))
            print(selectDataQuery.value(3))
            print(selectDataQuery.value(4))
      
        selectDataQuery.finish()
        
        # Re-Load the table directly in a QSqlTableModel
        model = QSqlTableModel()
        model.setTable("LastParameters")
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        model.select()
        
        # Set the model to the GUI table view
        self.tableWidget.setModel(model)
        
        # Prevent from editing the table
        # self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    '''
    def run(self):        
        if self.groupBoxMCMC.isChecked():
            self.done(1)
        else:
            self.done(10)
            
        '''
        SQL : INSERT INTO Layer (DepthBed) VALUES (1) WHERE id = layer
        '''
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = DialogCompute(1)
    mainWin.show()
    sys.exit(app.exec_())