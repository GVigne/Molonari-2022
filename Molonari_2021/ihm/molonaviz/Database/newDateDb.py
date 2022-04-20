from PyQt5.QtSql import QSqlQuery
import pandas as pd

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
        
    
    def insert(self, study):
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO NewDate (
                Date
            )
            VALUES (?)
            """
        )
    
        points = study.getPointsDb()
        
        for point in points:
            df_processed_temp = pd.read_csv(study.rootDir + "/" + point.name + "/processed_data/processed_temperatures.csv")
            df_processed_press = pd.read_csv(study.rootDir + "/" + point.name + "/processed_data/processed_pressures.csv")
            df_processed_measures = df_processed_temp.merge(df_processed_press)
            
            df = df_processed_measures
            col = df.columns
            
            for ind in df.index:
                insertQuery.addBindValue(str(df[col[0]][ind]))
            
            insertQuery.exec_()
            
        insertQuery.finish()
        
    def getIdByDate(self, date):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM NewDate where Date = :date")
        selectQuery.bindValue(":date", date)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id
        
        
        