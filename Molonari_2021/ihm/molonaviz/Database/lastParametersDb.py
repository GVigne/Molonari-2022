from PyQt5.QtSql import QSqlQuery
from .pointDb import PointDb

class LastParametersDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE LastParameters
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE LastParameters (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            log10K          REAL,
            LambdaS         REAL,
            N               REAL,
            Cap             REAL,
            Layer           INTEGER REFERENCES Layer (id),
            PointKey        INTEGER REFERENCES Point (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self, layers, point):
        self.con.transaction()

        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO LastParameters (
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
        point_id = PointDb(self.con).getIdByName(point.name)
        
        for i in range(len(layers)): # on parcourt les layers
            insertQuery.addBindValue(str(layers[i].params[0]))
            insertQuery.addBindValue(str(layers[i].params[2]))
            insertQuery.addBindValue(str(layers[i].params[1]))
            insertQuery.addBindValue(str(layers[i].params[3]))
            insertQuery.addBindValue(str(i+1))
            insertQuery.addBindValue(str(point_id))
            insertQuery.exec_()
            
        insertQuery.finish()
                
        self.con.commit()