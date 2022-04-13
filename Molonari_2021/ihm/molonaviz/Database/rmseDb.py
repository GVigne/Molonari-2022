from PyQt5.QtSql import QSqlQuery

class RMSEDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE RMSE
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE RMSE (
            id                  INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date                INTEGER REFERENCES Date (id),
            Depth1              INTEGER REFERENCES Depth (id),
            Depth2              INTEGER REFERENCES Depth (id),
            Depth3              INTEGER REFERENCES Depth (id),
            Temp1RMSE           REAL,
            Temp2RMSE           REAL,
            Temp3RMSE           REAL,
            RMSET               REAL,
            PointKey            INTEGER REFERENCES Point (id),
            Quantile            INTEGER REFERENCES Quantile (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        