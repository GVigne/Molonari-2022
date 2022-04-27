from PyQt5.QtSql import QSqlQuery

class DirectParametersDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE DirectParameters
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE DirectParameters (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            log10K         REAL,
            LambdaS         REAL,
            NBest           REAL,
            Layer           INTEGER REFERENCES Layer (id),
            PointKey        INTEGER REFERENCES Point (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        