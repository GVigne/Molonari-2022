from PyQt5.QtSql import QSqlQuery
from .quantileDb import QuantileDb


class WaterFlowDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE WaterFlow
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE WaterFlow (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            WaterFlow           REAL,
            Date                INTEGER REFERENCES Date (id),
            PointKey            INTEGER REFERENCES Point (id),
            Quantile            INTEGER REFERENCES Quantile (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert_quantile_0(self, water_flows):
        self.con.transaction()
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO WaterFlow (
            WaterFlow,
            Date,
            PointKey,
            Quantile,
        )
        VALUES (?, ?, ?, ?)
        """
        )
        # point_id = PointDb.getIdByName(point.name)
        
        for i in range (len(water_flows)):
            insertQuery.addBindValue(i)
            insertQuery.addBindValue(str(i+1)) #SQL Indexing starts at 1
            insertQuery.addBindValue(str(1))
            insertQuery.addBindValue(str(1))
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    
    def insert_quantile_0(self, water_flows):
        self.con.transaction()
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO WaterFlow (
            WaterFlow,
            Date,
            PointKey,
            Quantile,
        )
        VALUES (?, ?, ?, ?)
        """
        )
        # point_id = PointDb.getIdByName(point.name)
        
        for i in range (len(water_flows)):
            insertQuery.addBindValue(i)
            insertQuery.addBindValue(str(i+1)) #SQL Indexing starts at 1
            insertQuery.addBindValue(str(1))
            insertQuery.addBindValue(str(1))
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()

    def insert_quantile(self, water_flows, quantiles):
        self.con.transaction()
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO WaterFlow (
            WaterFlow,
            Date,
            PointKey,
            Quantile,
        )
        VALUES (?, ?, ?, ?)
        """
        )
        # point_id = PointDb.getIdByName(point.name)
        
        for quantile in quantiles:
            quantile_id = QuantileDb(self.con).getIdByQuantile(quantile)
            for i in range (len(water_flows)):
                insertQuery.addBindValue(i)
                insertQuery.addBindValue(str(i+1)) #SQL Indexing starts at 1
                insertQuery.addBindValue(str(1))
                insertQuery.addBindValue(str(quantile_id))
                insertQuery.exec_()
                
            insertQuery.finish()
            
            self.con.commit()