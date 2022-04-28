from PyQt5.QtSql import QSqlQuery

class DateDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE NewDate
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE NewDate (
            id             INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date           DATETIME
        );

        """
        )
        createQuery.finish()
        
    def insert(self, times):
        self.con.transaction()
        
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO NewDate (
                Date
            )
            VALUES (?)
            """
        )
    
        for time in times:
            insertQuery.addBindValue(str(time))
            
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByDate(self, date):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM NewDate where Date = :date")
        selectQuery.bindValue(":date", date)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id        