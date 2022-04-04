from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)


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
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            dateid INT KEY EXT,
            tbed FLOAT 
            t1 FLOAT,
            t2 FLOAT,
            t3 FLOAT,
            t4 FLOAT,
            tension FLOAT,
            pointid INT KEY EXT,
            incertitude FLOAT
        )
        """
    )
    createTableQuery.finish()



class DataBase(QMainWindow):
    def __init__(self, dftemp, dfpres, dfinfo, parent=None) -> None:
        super().__init__(parent)
        self.dftemp = dftemp
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
            VALUES (?, ?, ?, ?, ?)
            """
        )
        
        # assuming that dftemp and dfpres are cleaned, and have the same number of lines
        for ind in dftemp.index:
            insertDataQuery.addBindValue(str(self.dftemp['Date'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['River_bed'][ind]))            
            insertDataQuery.addBindValue(str(self.dftemp['Temp1'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp2'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp3'][ind]))
            insertDataQuery.addBindValue(str(self.dftemp['Temp4'][ind]))
            insertDataQuery.addBindValue(str(self.dfpres['Pressure'][ind]))
            # waiting to know how to manage pointid and uncertaincy
            insertDataQuery.addBindValue("0")
            insertDataQuery.addBindValue("0")
        
            insertDataQuery.exec()
        insertDataQuery.finish()
        
        self.model = QSqlTableModel()
        self.model.setTable("measures") 