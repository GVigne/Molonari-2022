from PyQt5.QtSql import QSqlQuery

class ShaftDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def insertShaftsromStudy(self, study):
        self.con.transaction()
        
        shafts = study.getShaftsDb()
        
        insertQuery = QSqlQuery(self.con)
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
        
        for shaft in shafts:
            # thermo_model = 
            insertQuery.addBindValue(shaft.name)
            insertQuery.addBindValue(shaft.depths[0])
            insertQuery.addBindValue(shaft.depths[1])
            insertQuery.addBindValue(shaft.depths[2])
            insertQuery.addBindValue(shaft.depths[3])
            insertQuery.addBindValue("1")
            insertQuery.addBindValue("1")
            
            insertQuery.exec_()
                
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.exec_(f"SELECT id FROM Shaft where name = {name}")
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        