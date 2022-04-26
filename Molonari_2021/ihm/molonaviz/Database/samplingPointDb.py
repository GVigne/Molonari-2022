from PyQt5.QtSql import QSqlQuery
from .studyDb import StudyDb
from .thermometerDb import ThermometerDb
from .pressureSensorDb import PressureSensorDb
from .shaftDb import ShaftDb

class SamplingPointDb():
    def __init__(self, con) -> None:    
        self.con = con
        
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE SamplingPoint
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE SamplingPoint (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            Name            VARCHAR,
            Notice          VARCHAR,
            Longitude       REAL,
            Latitude        REAL,
            Implentation    DATETIME,
            LastTransfer    DATETIME,
            DeltaH          REAL,
            RiverBed        REAL,
            Shaft           INTEGER REFERENCES Shaft (id),
            PressureSensor  INTEGER REFERENCES PressureSensor (id),
            Study           INTEGER REFERENCES Study (id),
            Scheme          VARCHAR,
            CleanupScript   VARCHAR
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
            INSERT INTO SamplingPoint (
                Name,
                Notice,
                Longitude,
                Latitude,
                Implentation,
                LastTransfert,
                DeltaH,
                RiverBed,
                Shaft,
                PressureSensor,
                Study,
                Scheme,
                CleanupScript
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        
        study_id = StudyDb(self.con).getIdByname(study.name)
        
        for point in points:
            shaft = point.getShaft()
            shaft_id = ShaftDb(self.con).getIdByname(shaft)
            
            psensor = point.getPressureSensor()
            psensor_id = PressureSensorDb(self.con).getIdByname(psensor)
            
            insertQuery.addBindValue(point.oldName)
            insertQuery.addBindValue("notice")
            insertQuery.addBindValue(str(0))
            insertQuery.addBindValue(str(0))
            insertQuery.addBindValue("06/27/16 12:00:00 PM")
            insertQuery.addBindValue("06/27/16 12:00:00 PM")
            insertQuery.addBindValue(point.deltaH)
            insertQuery.addBindValue(point.rivBed)
            insertQuery.addBindValue(shaft_id)
            insertQuery.addBindValue(psensor_id)
            insertQuery.addBindValue(str(study_id))
            insertQuery.addBindValue("1")
            insertQuery.addBindValue("CleanupScript")
            
            insertQuery.exec_()
            
        insertQuery.finish()
            
        self.con.commit()
        
    def select(self):
        pass
    
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM SamplingPoint where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        