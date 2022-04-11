from PyQt5.QtSql import QSqlQuery
from ThermometerDb import ThermometerDb

class ShaftDb():
    def __init__(self, con, model) -> None:    
        self.con = con
        self.model = model
        
        self.model.setTable("Shaft")
    
    def insertShaftsromStudy(self, study):
        self.con.transaction()
        
        shafts = study.getShaftsDb()
        
        for shaft in shafts:
            thermo_name = shaft.getThermometer()
            thermo_model = ThermometerDb(self.con).getIdByname(thermo_name)
            
            r = self.model.record()
            r.setValue("Name", shaft.name)
            r.setValue("Depth1", shaft.depths[0])
            r.setValue("Depth2", shaft.depths[1])
            r.setValue("Depth3", shaft.depths[2])
            r.setValue("Depth4", shaft.depths[3])
            r.setValue("Thermo_model", str(thermo_model))
            r.setValue("Labo", "1")
            
            self.model.insertRecord(-1, r)
            
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Shaft where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        