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
            Date            INTEGER REFERENCES Date (id),
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
        
    
    def insert(self, temps, advective_flux, conductive_flux, flows, point):
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO TemperatureAndHeatFlows (
            Date,
            Depth,
            Temperature,
            AdvectiveFlow,
            ConductiveFlow,
            TotalFlow,
            PointKey,
            Quantile
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        )
        # point_id = PointDb.getIdByName(point.name)
        
        for k in range(temps.shape[0]):
            for i in range(temps.shape[1]):
                insertQuery.addBindValue(str(i))
                insertQuery.addBindValue(str(k))
                insertQuery.addBindValue(str(temps[k, i]))
                insertQuery.addBindValue(str(advective_flux[k, i]))
                insertQuery.addBindValue(str(conductive_flux[k, i]))
                insertQuery.addBindValue(str(flows[k, i]))
                insertQuery.addBindValue(str(1))
                insertQuery.addBindValue(str(1))
            
                insertQuery.exec_()
            
        insertQuery.finish()
        