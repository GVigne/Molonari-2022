from PyQt5.QtSql import QSqlQuery
from .quantileDb import QuantileDb

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
        
    
    def insert_quantile_0(self, temps, advective_flux, conductive_flux, flows):
        self.con.transaction()
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
        
        self.con.commit()
        
    
    def insert_quantiles(self, col, quantiles):
        self.con.transaction()
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
        
        for quantile in quantiles:
            if quantile > 0:
                temps = col.get_temps_quantile(quantile)
                flows = col.get_flows_quantile(quantile)
                
                quantile_id = QuantileDb(self.con).getIdByQuantile(quantile)
                
                for k in range(temps.shape[0]):
                    for i in range(temps.shape[1]):
                        insertQuery.addBindValue(str(i))
                        insertQuery.addBindValue(str(k))
                        insertQuery.addBindValue(str(temps[k, i]))
                        """insertQuery.addBindValue(str(advective_flux[k, i]))
                        insertQuery.addBindValue(str(conductive_flux[k, i]))"""
                        insertQuery.addBindValue(str(1))
                        insertQuery.addBindValue(str(1))
                        insertQuery.addBindValue(str(flows[k, i]))
                        insertQuery.addBindValue(str(1))
                        insertQuery.addBindValue(str(quantile_id))
                    
                        insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()