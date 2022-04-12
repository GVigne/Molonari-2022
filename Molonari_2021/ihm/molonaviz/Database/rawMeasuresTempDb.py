from PyQt5.QtSql import QSqlQuery
from .samplingPointDb import SamplingPointDb


class RawMeasuresTempDb():
    def __init__(self, con) -> None:    
        self.con = con
            
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec_(
            """       
            DROP TABLE RawMeasuresTemp
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE RawMeasuresTemp (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            Date        DATETIME,
            Temp1       REAL,
            Temp2       REAL,
            Temp3       REAL,
            Temp4       REAL,
            PointKey    INTEGER REFERENCES SamplingPoint (id)
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self, study):
        self.con.transaction()
        
        points = study.getPointsDb()
        
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
        """ 
        INSERT INTO RawMeasuresTemp (
            Date,
            Temp1,
            Temp2,
            Temp3,
            Temp4,
            PointKey
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
        )
        
        for point in points:
            pointKey = SamplingPointDb(self.con).getIdByname(point.name)
            
            dftemp = point.dftemp
            
            col = dftemp.columns
            for ind in dftemp.index:
                insertQuery.addBindValue(str(dftemp[col[0]][ind]))
                insertQuery.addBindValue(str(dftemp[col[1]][ind]))
                insertQuery.addBindValue(str(dftemp[col[2]][ind]))
                insertQuery.addBindValue(str(dftemp[col[3]][ind]))
                insertQuery.addBindValue(str(dftemp[col[4]][ind]))
                insertQuery.addBindValue(str(pointKey))
                
                insertQuery.exec_()
        
        insertQuery.finish()
        
        self.con.commit()
        
    def select(self):
        pass
                        
                