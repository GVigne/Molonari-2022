from PyQt5.QtSql import QSqlQuery

class LaboDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Labo
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Labo (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR NOT NULL
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self):
        self.con.transaction()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Labo (
            Name
        )
        VALUES (?)
        """
        )
        insertQuery.addBindValue("nom")
        insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.exec_(f"SELECT id FROM Labo where name = {name}")
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        