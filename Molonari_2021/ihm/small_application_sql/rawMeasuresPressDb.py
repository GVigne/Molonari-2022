from PyQt5.QtSql import QSqlQuery
from samplingPointDb import SamplingPointDb

class RawMeasuresPressDb():
    def __init__(self, con, ) -> None:    
        self.con = con
            
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec_(
            """       
            DROP TABLE RawMeasuresPress
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE RawMeasuresPress (
            id          INTEGER UNIQUE
                                PRIMARY KEY AUTOINCREMENT,
            Date        DATETIME    NOT NULL
                                UNIQUE,
            TempBed     REAL,
            Pressure    REAL,
            PointKey   INTEGER
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
        INSERT INTO RawMeasuresPress (
            Date,
            TempBed,
            Pressure,
            PointKey
        )
        VALUES (?, ?, ?, ?)
        """
        )
        
        for point in points:
            pointKey = SamplingPointDb(self.con).getIdByname(point.name)
            
            dfpress = point.dfpress
            
            col = dfpress.columns
            for ind in dfpress.index:
                insertQuery.addBindValue(str(dfpress[col[0]][ind]))
                insertQuery.addBindValue(str(dfpress[col[1]][ind]))
                insertQuery.addBindValue(str(dfpress[col[2]][ind]))
                insertQuery.addBindValue(str(pointKey))
                
                insertQuery.exec_()
        insertQuery.finish()
        self.con.commit()
        
    def select(self):
        pass
                        
                