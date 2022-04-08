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
from StudyDb import StudyDb
from LaboDb import LaboDb

from tp_ihm_sql import loadCSV, convertDates
from creationTables import createTableMeasures
from insertionTables import writeProcessedMeasuresSql, writeRawPressuresSql, writeRawTemperaturesSql

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

        
        dropTableMeasures(self.con)
        createTableMeasures(self.con)
        
        
        
    def displaySQL(self):
        """
        Display measures
        """
        
        # Re-Load the table directly in a QSqlTableModel
        if self.comboBox.currentText() == "Raw temperatures":
            self.model.setTable("measures_temp")
        elif self.comboBox.currentText() == "Raw pressures":
            self.model.setTable("measures_press")
        elif self.comboBox.currentText() == "Processed measures":
            self.model.setTable("processed_measures")
        elif self.comboBox.currentText() == "Labo":
            self.model.setTable("Labo")
        elif self.comboBox.currentText() == "Study":
            self.model.setTable("Study")
            
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
            labo = LaboDb(self.con)
            labo.insert()
            
            study = StudyDb(self.con)
            study.insert()
            
            writeRawTemperaturesSql(self.con, df_raw_temp)
            writeRawPressuresSql(self.con, df_raw_press)
            writeProcessedMeasuresSql(self.con, df_processed_measures)
            
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
    
