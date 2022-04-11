import sys, os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QAbstractItemView
)
import pandas as pd
from PyQt5 import uic
from studyDb import StudyDb
from laboDb import LaboDb
from thermometerDb import ThermometerDb
from samplingPointDb import SamplingPointDb
from shaftsDb import ShaftDb

from tp_ihm_sql import loadCSV, convertDates
from creationTables import createTableMeasures
from insertionTables import writeProcessedMeasuresSql, writeRawPressuresSql, writeRawTemperaturesSql
from pressureSensorDb import PressureSensorDb
from rawMeasuresTempDb import RawMeasuresTempDb
from rawMeasuresPressDb import RawMeasuresPressDb
from shaftsDb import ShaftDb
sys.path.insert(0, 'C:/Users/33689/OneDrive/Documents/2A/Molonari/Molonari-2022/Molonari_2021/ihm/molonaviz')
from study import Study


version_ui = uic.loadUiType(os.path.join(os.path.dirname(__file__),"mainSql.ui"))


def dropTableMeasures(connection):
    dropTableQuery = QSqlQuery(connection)
    dropTableQuery.exec_(
        """
        DROP TABLE measures_temp
        """
    )
    dropTableQuery.exec_(
        """
        DROP TABLE measures_press
        """
    )
    dropTableQuery.finish()


class DataBase(version_ui[0], version_ui[1]):
    def __init__(self) -> None:
        super(DataBase, self).__init__()
        self.setupUi(self)
        
        self.pushButtonBrowse.clicked.connect(self.browseFile)
        self.comboBox.currentIndexChanged.connect(self.displaySQL)
        
        self.sqlfile = "molonari_slqdb.sqlite"
        if os.path.exists(self.sqlfile):
            os.remove(self.sqlfile)
        
        
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sqlfile)
        if not self.con.open():
            print("Cannot open SQL database")
            
        self.model = QSqlTableModel(self, self.con)

        
        # dropTableMeasures(self.con)
        # createTableMeasures(self.con)
        
        
        
    def displaySQL(self):
        """
        Display measures
        """
        
        # Re-Load the table directly in a QSqlTableModel
        if self.comboBox.currentText() == "Raw temperatures":
            self.model.setTable("RawMeasuresTemp")
        elif self.comboBox.currentText() == "Raw pressures":
            self.model.setTable("RawMeasuresPress")
        elif self.comboBox.currentText() == "Processed measures":
            self.model.setTable("CleanedMeasures")
        elif self.comboBox.currentText() == "Labo":
            self.model.setTable("Labo")
        elif self.comboBox.currentText() == "Study":
            self.model.setTable("Study")
        elif self.comboBox.currentText() == "Pressure Sensor":
            self.model.setTable("PressureSensor")
        elif self.comboBox.currentText() == "Shaft":
            self.model.setTable("Shaft")
        elif self.comboBox.currentText() == "Thermometer":
            self.model.setTable("Thermometer")
        elif self.comboBox.currentText() == "Sampling point":
            self.model.setTable("SamplingPoint")
        self.model.select()
        
        # Set the model to the GUI table view
        self.tableView.reset()
        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        
        # Prevent from editing the table
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers);
        
        
    def browseFile(self):
    # Open a "File Dialog" window and retrieve the path
        StudyFolderPath = QFileDialog.getExistingDirectory(self, "Select Study Root Directory")
        
        
        
        if StudyFolderPath:
            current_study = Study(rootDir=StudyFolderPath)
            current_study.loadStudyFromText()
            
            # Update the lineEditTempFile
            self.lineEditTempFile.setText(StudyFolderPath)
        
            # Read the CSV file
            df_processed_temp = pd.read_csv(StudyFolderPath + "/Point034/processed_data/processed_temperatures.csv")
            df_processed_press = pd.read_csv(StudyFolderPath + "/Point034/processed_data/processed_pressures.csv")
            df_processed_measures = df_processed_temp.merge(df_processed_press)
            df_raw_temp = pd.read_csv(StudyFolderPath + "/Point034/raw_data/raw_temperatures.csv", skiprows=1)
            df_raw_temp = df_raw_temp.iloc[:, 1:]
            df_raw_press = pd.read_csv(StudyFolderPath + "/Point034/raw_data/raw_pressures.csv", skiprows=1)
            df_raw_press = df_raw_press.iloc[:, 1:]
            
            # Dump the measures to SQL database
            laboDb = LaboDb(self.con)
            laboDb.create()
            laboDb.insert()
            
            thermometerDb = ThermometerDb(self.con)
            thermometerDb.create()
            thermometerDb.insert(current_study)
            
            studyDb = StudyDb(self.con)
            studyDb.create()
            studyDb.insert(current_study)
            
            pressureSensorDb = PressureSensorDb(self.con)
            pressureSensorDb.create()
            pressureSensorDb.insert(current_study)
            
            shaftDb = ShaftDb(self.con)
            shaftDb.create()
            shaftDb.insert(current_study)
            
            samplingPointDb = SamplingPointDb(self.con)
            samplingPointDb.create()
            samplingPointDb.insert(current_study)
            
            rawMeasuresTempDb = RawMeasuresTempDb(self.con)
            rawMeasuresTempDb.create()
            rawMeasuresTempDb.insert(current_study)
            
            rawMeasuresPressDb = RawMeasuresPressDb(self.con)
            rawMeasuresPressDb.create()
            rawMeasuresPressDb.insert(current_study)
            
            # writeRawTemperaturesSql(self.con, df_raw_temp)
            # writeRawPressuresSql(self.con, df_raw_press)
            # writeProcessedMeasuresSql(self.con, df_processed_measures)
            
            # Read the SQL and update the views
            self.displaySQL()



if __name__ == '__main__':
    """
    Main function of the script:
    - Create the QApplication object
    - Create the TemperatureViewer dialog and show it
    - Execute the infinite event loop and wait for interaction or exit
    """
    app = QApplication(sys.argv)

    mainWin = DataBase()
    mainWin.show()

    sys.exit(app.exec_())
    
