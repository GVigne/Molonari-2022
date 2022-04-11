from PyQt5.QtSql import QSqlQuery

class PressureSensorDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def insertSensorsFromStudy(self, study):
        self.con.transaction()
        
        pressure_sensors = study.getPressureSensorsDb()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """ 
        INSERT INTO pressure_sensor (
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
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM pressure_sensor where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        