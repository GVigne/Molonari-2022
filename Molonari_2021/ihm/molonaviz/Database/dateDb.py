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
            id             INTEGER  PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            Date           DATETIME,
            UNIQUE(Date)
        );

        """
        )
        createQuery.finish()
        
    def insert(self, times):
        self.con.transaction()
        
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO Date (
                Date
            )
            VALUES (?)
            """
        )
        # times = df.apply(lambda x: x['date'].strftime("%Y:%m:%d:%H:%M:%S"), axis=1)
        for time in times:
            insertQuery.addBindValue(str(time))

            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        
    def getIdByDate(self, date):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Date where Date = :date")
        selectQuery.bindValue(":date", date)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id        