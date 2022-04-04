from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


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



class DataBase():
    def __init__(self, dftemp, dfpres) -> None:
        self.dftemp = dftemp
        self.dfpres = dfpres
        self.sql = "molonari_db.sqlite"
        
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sql)
        if not self.con.open():
            print("Cannot open SQL database")
            
        dropTableMeasures(self.con)
        createTableMeasures(self.con)