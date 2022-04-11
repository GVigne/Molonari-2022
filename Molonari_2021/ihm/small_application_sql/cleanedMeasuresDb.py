from PyQt5.QtSql import QSqlQuery

class CleanedMeasuresDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE CleanedMeasures
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE CleanedMeasures (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date          DATETIME UNIQUE,
            TempBed      REAL     NOT NULL,
            Temp1            REAL     NOT NULL,
            Temp2            REAL     NOT NULL,
            Temp3            REAL     NOT NULL,
            Temp4            REAL     NOT NULL,
            Pressure      REAL     NOT NULL,
            PointKey     INTEGER REFERENCES Sampling_point (id),
            uncertainties INTEGER REFERENCES Uncertainties (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        