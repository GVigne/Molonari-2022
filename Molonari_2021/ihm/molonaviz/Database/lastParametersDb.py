from PyQt5.QtSql import QSqlQuery

class LastParametersDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE BestParameters
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE BestParameters (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            log10KBest         REAL,
            LambdaSBest         REAL,
            NBest           REAL,
            Cap             REAL,
            Layer           INTEGER REFERENCES Layer (id),
            PointKey        INTEGER REFERENCES Point (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        