from PyQt5.QtSql import QSqlQuery

class DepthDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Depth
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Depth (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            Depth         REAL
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self, depths):
        self.con.transaction()
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Depth (
            Depth
        )
        VALUES (?)
        """
        )
        
        
        
        for depth in depths:
            insertQuery.addBindValue(str(depth))
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()
        