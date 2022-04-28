from PyQt5.QtSql import QSqlQuery

class LayerDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE Layer
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE Layer (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            Layer           INTEGER,
            DepthBed        REAL
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self, layers):
        self.con.transaction()
        
        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
        """
        INSERT INTO Layer (
            Layer,
            DepthBed
        )
        VALUES (?, ?)
        """
        )
        
        for k in range(len(layers)):
            insertQuery.addBindValue(str(k+1))
            insertQuery.addBindValue(str(layers[k].zLow))
            insertQuery.exec_()
            
        insertQuery.finish()
        
        self.con.commit()