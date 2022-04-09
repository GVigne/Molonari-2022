from PyQt5.QtSql import QSqlQuery

class StudyDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def insert(self, study):
        self.con.transaction()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Study (
            Name,
            Labo
        )
        VALUES (?, ?)
        """
        )
        insertQuery.addBindValue(study.name)
        insertQuery.addBindValue("1")
        
        insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByname(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.exec_(f"SELECT id FROM Study where name = {name}")
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        