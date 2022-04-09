from PyQt5.QtSql import QSqlQuery

class ThermometerDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def insertThermometersFromStudy(self, study):
        self.con.transaction()
        
        thermometers = study.getThermometersDb()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Thermometer (
            Name,
            Manu_name,
            Manu_ref,
            Error
        )
        VALUES (?, ?, ?, ?)
        """
        )
        for thermometer in thermometers:
            insertQuery.addBindValue(thermometer.name)
            insertQuery.addBindValue(thermometer.consName)
            insertQuery.addBindValue(thermometer.ref)
            insertQuery.addBindValue(str(thermometer.sigma))
            
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Thermometer where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        