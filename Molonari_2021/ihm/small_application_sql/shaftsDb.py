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
        
        '''insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Shaft (
            Name,
            Depth1,
            Depth2,
            Depth3,
            Depth4,
            Thermo_model,
            Labo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        )
        '''
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
            '''
            insertQuery.exec_()
                
        insertQuery.finish()
        '''
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.exec_(f"SELECT id FROM Shaft where name = {name}")
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        