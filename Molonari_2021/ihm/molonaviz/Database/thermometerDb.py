from PyQt5.QtSql import QSqlQuery

class ThermometerDb():
    def __init__(self, con) -> None:
        self.con = con
        
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Thermometer
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Thermometer (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            Name      VARCHAR NOT NULL,
            Manu_name VARCHAR NOT NULL,
            Manu_ref  VARCHAR NOT NULL,
            Error     REAL    NOT NULL
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self, thermometers):
        self.con.transaction()
                
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
        