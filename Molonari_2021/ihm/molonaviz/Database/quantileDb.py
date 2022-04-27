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
        
        # We insert the fictional quantile 0 corresponding to the direct modele
        insertQuery.addBindValue(str(0))
        insertQuery.exec_()
        
        for quantile in quantiles:
            insertQuery.addBindValue(str(quantile))
            insertQuery.exec_()
            
        insertQuery.finish()
    
