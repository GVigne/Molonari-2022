from PyQt5.QtSql import QSqlQuery

class ParametersDistributionDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE ParametersDistribution
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE ParametersDistribution (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            -log10K         REAL,
            LambdaS         REAL,
            N               REAL,
            Layer           INTEGER REFERENCES Layer (id),
            PointKey        INTEGER REFERENCES Point (id),
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        