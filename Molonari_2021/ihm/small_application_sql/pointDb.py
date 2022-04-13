from PyQt5.QtSql import QSqlQuery

class PointDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Point
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Point (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            SamplingPoint   INTEGER REFERENCES SamplingPoint (id),
            IncertK         REAL,
            IncertLambda    REAL,
            IncertN         REAL,
            IncertRho       REAL,
            IncertT         REAL,
            IncertPressure  REAL
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        