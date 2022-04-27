from PyQt5.QtSql import QSqlQuery
from .pointDb import PointDb
from .quantileDb import QuantileDb

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
        
    
    def insert(self, col, quantiles, point):
        self.con.transaction()
                
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO RMSE (
                Depth1,
                Depth2,
                Depth3,
                Temp1RMSE,
                Temp2RMSE,
                Temp3RMSE,
                RMSET,
                PointKey,
                Quantile
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        
        point_id = PointDb(self.con).getIdByName(point.name)
        
        for quantile in quantiles:
            if quantile > 0:
                quantile_id = QuantileDb(self.con).getIdByQuantile(quantile)
                
                insertQuery.addBindValue(str(col.depth_sensors[0]))
                insertQuery.addBindValue(str(col.depth_sensors[1]))
                insertQuery.addBindValue(str(col.depth_sensors[2]))
                insertQuery.addBindValue(str(col.get_RMSE_quantile(quantile)[0]))
                insertQuery.addBindValue(str(col.get_RMSE_quantile(quantile)[1]))
                insertQuery.addBindValue(str(col.get_RMSE_quantile(quantile)[2]))
                insertQuery.addBindValue(str(col.get_RMSE_quantile(quantile)[3]))
                insertQuery.addBindValue(str(point_id))
                insertQuery.addBindValue(str(quantile_id))
                
                insertQuery.exec_()
            else:
                insertQuery.addBindValue(str(col.depth_sensors[0]))
                insertQuery.addBindValue(str(col.depth_sensors[1]))
                insertQuery.addBindValue(str(col.depth_sensors[2]))
                insertQuery.addBindValue(str(col.get_RMSE()[0]))
                insertQuery.addBindValue(str(col.get_RMSE()[1]))
                insertQuery.addBindValue(str(col.get_RMSE()[2]))
                insertQuery.addBindValue(str(col.get_RMSE()[3]))
                insertQuery.addBindValue(str(point_id))
                insertQuery.addBindValue(str(1))
                
                insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
    