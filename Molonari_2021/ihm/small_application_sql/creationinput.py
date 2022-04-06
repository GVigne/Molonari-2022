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
from tp_ihm_sql import loadCSV, convertDates

version_ui = uic.loadUiType(os.path.join(os.path.dirname(__file__),"creationinput.ui"))


def dropTableMeasures(connection):
    dropTableQuery = QSqlQuery(connection)
    dropTableQuery.exec_(
        """       
        DROP TABLE processed_measures_temp
        """
    )
    dropTableQuery.finish()


def createTableMeasures(connection):
    createTablesQuery = QSqlQuery(connection)
    createTablesQuery.exec_(
        """
        CREATE TABLE processed_measures_temp (
        id          INTEGER UNIQUE
                            PRIMARY KEY AUTOINCREMENT,
        date        TIME    NOT NULL
                            UNIQUE,
        t1          REAL,
        t2          REAL,
        t3          REAL,
        t4          REAL,
        point_key   INTEGER,
        uncertaincy REAL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE processed_measures_press (
        id          INTEGER UNIQUE
                            PRIMARY KEY AUTOINCREMENT
                            REFERENCES processed_measures_temp (id),
        date        TIME    NOT NULL
                            UNIQUE,
        pressure    REAL    NOT NULL,
        point_key   INTEGER,
        uncertaincy REAL
        );
        """
    )
    createTablesQuery.finish()


def cleanupTemp(df: pd.DataFrame):
    """
    Cleanup raw temperature Pandas Dataframe:
        - Rename the columns,
        - Remove lines having missing values 
        - Remove unexpected last columns and
        - Delete Index column
    
    This function works directly on the giving Pandas Dataframe (in place)
    """
    # New column names
    val_cols = ["Temp1", "Temp2", "Temp3", "Temp4"]
    all_cols = ["Date"] + val_cols
    # Rename the 6 first columns
    for i in range(0, len(all_cols)) :
        df.columns.values[i] = all_cols[i]
    # Remove lines having at least one missing value
    # df.dropna(subset=val_cols,inplace=True)
    # Remove last columns
    # df.dropna(axis=1,inplace=True)


def writeTemperaturesSql(con, dftemp):
    con.transaction()
    
    insertTemperaturesQuery = QSqlQuery(con)
    insertTemperaturesQuery.prepare(
        """
        INSERT INTO processed_measures_temp (
            date,
            t1,
            t2,
            t3,
            t4,
            point_key,
            uncertaincy
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
    )
    
    col = dftemp.columns
    
    for ind in dftemp.index:
        insertTemperaturesQuery.addBindValue(str(dftemp[col[0]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[1]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[2]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[3]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[4]][ind]))
        # waiting to know how to manage pointid and uncertaincy
        insertTemperaturesQuery.addBindValue("0")
        insertTemperaturesQuery.addBindValue("0")
    
        insertTemperaturesQuery.exec_()
    insertTemperaturesQuery.finish()
    con.commit()

def writePressuresSql(con, dfpress):
    insertPressuresQuery = QSqlQuery(con)
    insertPressuresQuery.prepare(
        """
        INSERT INTO processed_measures_press (
           date,
           pressure,
           point_key,
           uncertaincy
        )
        VALUES (?, ?, ?, ?)
        """
    )
    
    col = dfpress.columns
    
    for ind in dfpress.index:
        insertPressuresQuery.addBindValue(str(dfpress[col[0]][ind]))
        insertPressuresQuery.addBindValue(str(dfpress[col[1]][ind]))
        insertPressuresQuery.addBindValue("0")
        insertPressuresQuery.addBindValue("0")
        
        insertPressuresQuery.exec_()
    insertPressuresQuery.finish()

    

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
        
        
        
    def readCSV(self):
        """
        Read the provided CSV file and load it into a Pandas dataframe
        """
        # Retrieve the CSV file path from lineEditTempFile
        ### TODO
        trawfile = self.lineEditTempFile.text()
        ### End TODO
        if trawfile:
            # Load the CSV file
            df = pd.read_csv(trawfile, skiprows=1)
            
            # Convert the dates
            convertDates(df)
            
            return df
        
    def displaySQL(self):
        """
        Display measures
        """
        
        # Re-Load the table directly in a QSqlTableModel
        if self.comboBox.currentText() == "Processed measures":
            self.model.setTable("processed_measures_temp")
        elif self.comboBox.currentText() == "":
            self.model.setTable("processed_measures_press")
        
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
            dftemp = pd.read_csv(StudyFolderPath + "/Point034/processed_data/processed_temperatures.csv")
            dfpress = pd.read_csv(StudyFolderPath + "/Point034/processed_data/processed_pressures.csv")

            # Dump the measures to SQL database
            writeTemperaturesSql(self.con, dftemp)
            writePressuresSql(self.con, dfpress)
            
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
    
