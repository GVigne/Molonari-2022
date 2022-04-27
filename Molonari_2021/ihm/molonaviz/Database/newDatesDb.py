from PyQt5.QtSql import QSqlQuery

class NewDatesDb():
    def __init__(self, con) -> None:    
        self.con = con
            
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec_(
            """       
            DROP TABLE NewDates
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE NewDates (
            id          INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            Date        TIMESTAMP,  
            UNIQUE(Date)  
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self, df):
        self.con.transaction()
   
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """ 
        INSERT INTO NewDates (
            Date
        )
        VALUES (?)
        """
        )
        
        df = df.apply(lambda x: x['date'].strftime("%Y:%m:%d:%H:%M:%S"), axis=1)
        for ind in df.index:
            insertQuery.addBindValue(str(df[ind]))            
            insertQuery.exec_()
        
        insertQuery.finish()
        
        self.con.commit()