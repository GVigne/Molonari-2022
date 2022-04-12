from PyQt5.QtSql import QSqlQuery
from .thermometerDb import ThermometerDb

class ShaftDb():
    def __init__(self, con) -> None:    
        self.con = con
        
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Shaft
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Shaft (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            Name         VARCHAR NOT NULL,
            Depth1       REAL    NOT NULL,
            Depth2       REAL    NOT NULL,
            Depth3       REAL    NOT NULL,
            Depth4       REAL    NOT NULL,
            Thermo_model INTEGER REFERENCES Thermometer (id),
            Labo         INTEGER REFERENCES Labo (id)
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self, study):
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
            thermo_name = shaft.getThermometer()
            thermo_model = ThermometerDb(self.con).getIdByname(thermo_name)
            
            insertQuery.addBindValue(shaft.name)
            insertQuery.addBindValue(shaft.depths[0])
            insertQuery.addBindValue(shaft.depths[1])
            insertQuery.addBindValue(shaft.depths[2])
            insertQuery.addBindValue(shaft.depths[3])
            insertQuery.addBindValue(str(thermo_model))
            insertQuery.addBindValue(str(1))
            
            insertQuery.exec_()
            
        insertQuery.finish()
            
        self.con.commit()
    
    def select(self):
        pass
    
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Shaft where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        