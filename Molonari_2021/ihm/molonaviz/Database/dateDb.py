from PyQt5.QtSql import QSqlQuery

class DateDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Date
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Date (
            id             INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date           DATETIME
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self):
        pass
        