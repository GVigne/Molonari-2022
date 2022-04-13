from PyQt5.QtSql import QSqlQuery

class TemperatureAndHeatFlowsDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE TemperatureAndHeatFlows
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE TemperatureAndHeatFlows (
            id              INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date            INTEGER REFERENCES Date (id),,
            Depth           INTEGER REFERENCES Depth (id),
            Temperature     REAL,
            AdvectiveFlow   REAL,
            ConductiveFlow  REAL,
            TotalFlow       REAL,
            PointKey        INTEGER REFERENCES Point (id),
            Quantile        INTEGER REFERENCES Quantile (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        