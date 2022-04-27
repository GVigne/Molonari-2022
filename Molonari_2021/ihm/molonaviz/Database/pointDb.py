from PyQt5.QtSql import QSqlQuery

class PointDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Point
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Point (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            SamplingPoint   INTEGER REFERENCES SamplingPoint (id),
            IncertT         REAL,
            n_discr  REAL
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO Point (
                SamplingPoint,
                IncertT,
                n_discr
            )
            VALUES (?, ?, ?)
            """
        )
    
        
        selectQuery = QSqlQuery(self.con)
        selectQuery.exec_("SELECT id FROM SamplingPoint")
        
        while selectQuery.next():
            id = int(selectQuery.value(0))
            insertQuery.addBindValue(id)
            insertQuery.addBindValue("0")
            insertQuery.addBindValue("100")
            
            insertQuery.exec_()
            
        insertQuery.finish()
        selectQuery.finish()
        
    def getIdByName(self, name):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Point where Name = :name")
        selectQuery.bindValue(":name", name)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        