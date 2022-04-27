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
            log10K         REAL,
            LambdaS         REAL,
            N               REAL,
            Cap             REAL,
            Layer           INTEGER REFERENCES Layer (id),
            PointKey        INTEGER REFERENCES Point (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self, params):
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO ParametersDistribution (
            log10k,
            LambdaS,
            N,
            Cap,
            Layer,
            PointKey
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
        )
        
        
        for i in range(len(params)): # on parcourt les layers
            for k in range(len(params[i])):
                insertQuery.addBindValue(str(params[i][k, 0]))
                insertQuery.addBindValue(str(params[i][k, 2]))
                insertQuery.addBindValue(str(params[i][k, 1]))
                insertQuery.addBindValue(str(params[i][k, 3]))
                insertQuery.addBindValue(str(i))
                insertQuery.addBindValue(str(params[i][k, 3]))
                insertQuery.addBindValue(str(1))
                insertQuery.exec_()
            
        insertQuery.finish()
        