from PyQt5.QtSql import QSqlQuery

class RawMeasuresPressDb():
    def __init__(self, con, table_name) -> None:    
        self.con = con
        self.table = table_name
            
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE RawMeasuresPress
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE RawMeasuresPress (
            id          INTEGER UNIQUE
                                PRIMARY KEY AUTOINCREMENT,
            Date        DATETIME    NOT NULL
                                UNIQUE,
            TempBed          REAL,
            Pressure          REAL,
            PointKkey   INTEGER,
        );
        """
        )
        createQuery.finish()
        
    
    def insertRawMeasuresPressFromStudy(self, study):
        pass
        
    def select(self):
        pass
                        
                