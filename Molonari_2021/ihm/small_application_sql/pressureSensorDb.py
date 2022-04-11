from PyQt5.QtSql import QSqlQuery

class PressureSensorDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE PressureSensor
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE PressureSensor (
            id           INTEGER  PRIMARY KEY AUTOINCREMENT,
            Name         VARCHAR ,
            Datalogger   VARCHAR ,
            Calibration  DATETIME,
            Intercept    REAL,
            [Du/Dh]      REAL,
            [Du/Dt]      REAL,
            Precision    REAL,
            Thermo_model INTEGER  REFERENCES Thermometer (id),
            Labo         INTEGER  REFERENCES Labo (id)
        );
        """
        )
        createQuery.finish()
        
    
    def insertSensorsFromStudy(self, study):
        self.con.transaction()
        
        pressure_sensors = study.getPressureSensorsDb()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """ 
        INSERT INTO PressureSensor (
            Name,
            Datalogger,
            Calibration,
            Intercept,
            [Du/Dh],
            [Du/Dt],
            Precision,
            Thermo_model,
            Labo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        )
        
        for psensor in pressure_sensors:
            insertQuery.addBindValue(psensor.name)
            insertQuery.addBindValue(psensor.datalogger)
            insertQuery.addBindValue(psensor.calibrationDate)
            insertQuery.addBindValue(str(psensor.intercept))
            insertQuery.addBindValue(str(psensor.dudh))
            insertQuery.addBindValue(str(psensor.dudt))
            insertQuery.addBindValue(str(psensor.sigma))
            insertQuery.addBindValue("1")
            insertQuery.addBindValue("1")
            
            insertQuery.exec_()
                
        insertQuery.finish()
        
        self.con.commit()
    
    def select(self):
        pass
    
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM PressureSensor where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        