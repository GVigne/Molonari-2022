from PyQt5.QtSql import QSqlQuery

class QuantileDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Quantile
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Quantile (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            Quantile    REAL NOT NULL
        );
        """
        )
        createQuery.finish()
        
    
    def insert(self, quantiles):
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Quantile (
            Quantile
        )
        VALUES (?)
        """
        )
        
        for quantile in quantiles:
            insertQuery.addBindValue(str(quantile))
            insertQuery.exec_()
            
        insertQuery.finish()
    
    def getIdByQuantile(self, quantile):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Quantile where Quantile = :quantile")
        selectQuery.bindValue(":quantile", quantile)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id