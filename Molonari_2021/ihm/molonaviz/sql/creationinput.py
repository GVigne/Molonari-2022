from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)
import pandas as pd

def dropTableMeasures(connection):
    dropTableQuery = QSqlQuery(connection)
    dropTableQuery.exec(
        """       
        DROP TABLE measures
        """
    )
    dropTableQuery.finish()


def createTableMeasures(connection):
    createTableQuery = QSqlQuery(connection)
    createTableQuery.exec(
        """
        CREATE TABLE measures (
        id                  PRIMARY KEY
                            UNIQUE,
        dateid              NOT NULL
                            UNIQUE,
        t1          REAL,
        t2          REAL,
        t3          REAL,
        t4          REAL,
        pressure    REAL,
        point_key   INTEGER,
        uncertaincy REAL
        );

        """
    )
    createTableQuery.finish()
    


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
    df.dropna(subset=val_cols,inplace=True)
    # Remove last columns
    df.dropna(axis=1,inplace=True)
    



class DataBase():
    def __init__(self, dftemp, dfpres, dfinfo=None) -> None:
        self.dftemp = dftemp
        cleanupTemp(self.dftemp)
        self.dfpres = dfpres
        self.dfinfo = dfinfo
        
        self.sql = "molonari_db.sqlite"
        
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sql)
        if not self.con.open():
            print("Cannot open SQL database")
            
        dropTableMeasures(self.con)
        createTableMeasures(self.con)
        
        insertDataQuery = QSqlQuery(self.con)
        insertDataQuery.prepare(
            """
            INSERT INTO measures (
                dateid INT KEY EXT,
                tbed FLOAT,
                t1 FLOAT,
                t2 FLOAT,
                t3 FLOAT,
                t4 FLOAT,
                pressure FLOAT,
                pointid INT KEY EXT,
                uncertaincy FLOAT
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        
        # assuming that dftemp and dfpres are cleaned, and have the same number of lines
        for ind in dftemp.index:
            insertDataQuery.addBindValue(str(self.dftemp['Date'][ind]))
            insertDataQuery.addBindValue("0")            
            insertDataQuery.addBindValue(str(self.dftemp['Temp1'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp2'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp3'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp4'][ind]))
            #insertDataQuery.addBindValue(str(self.dfpres['Pressure'][ind]))
            insertDataQuery.addBindValue("0")
            # waiting to know how to manage pointid and uncertaincy
            insertDataQuery.addBindValue("0")
            insertDataQuery.addBindValue("0")
        
            insertDataQuery.exec()
        insertDataQuery.finish()
        
        self.model = QSqlTableModel()
        self.model.setTable("measures")
        self.model.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.model.select()