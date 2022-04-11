from PyQt5.QtSql import QSqlQuery
from thermometerDb import ThermometerDb
from pressureSensorDb import PressureSensorDb
from shaftsDb import ShaftDb

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
            LastTransfert  DATETIME,
            DeltaH         REAL,
            RiverBed       REAL,
            Shaft           INTEGER REFERENCES Shaft (id),
            PressureSensor INTEGER REFERENCES pressure_sensor (id),
            Study           INTEGER REFERENCES Study (id)
        );
        """
        )
        createQuery.finish()
        
            
    def insert(self, study):
        """self.con.transaction()
        
        points = study.getPointsDb()
        
        for point in points:
            shaft = point.getShaft()
            shaft_id = ShaftDb(self.con, self.model).getIdByname(shaft)
            
            psensor = point.getPressureSensor()
            psensor_id = PressureSensorDb(self.con).getIdByname(psensor)
            
            r = self.model.record()
            r.setValue("Name", point.oldName)
            r.setValue("Notice", "notice")
            r.setValue("Longitude", 0)
            r.setValue("Latitude", 0)
            r.setValue("Implentation", "06/27/16 12:00:00 PM")
            r.setValue("Last_transfert", "06/27/16 12:00:00 PM")
            r.setValue("Delta_h", point.deltaH)
            r.setValue("River_bed", point.rivBed)
            r.setValue("Shaft", shaft_id)
            r.setValue("Pressure_sensor", psensor_id)
            r.setValue("Study", 1)
            
            self.model.setTable("Sampling_point")
            self.model.insertRecord(-1, r)
            
        self.con.commit()"""
        
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
        