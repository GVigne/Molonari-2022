from PyQt5.QtSql import QSqlQuery
import pandas as pd
from .samplingPointDb import SamplingPointDb

class CleanedMeasuresDb():
    def __init__(self, con) -> None:
        self.con = con
    
    def create(self):
        dropQuery = QSqlQuery()
        
        dropQuery.exec(
            """       
            DROP TABLE CleanedMeasures
            """
        )
    
        dropQuery.finish()
        
        createQuery = QSqlQuery(self.con)
        
        createQuery.exec_(
        """
        CREATE TABLE CleanedMeasures (
            id            INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date          INTEGER REFERENCES Date (id),
            TempBed      REAL     NOT NULL,
            Temp1            REAL     NOT NULL,
            Temp2            REAL     NOT NULL,
            Temp3            REAL     NOT NULL,
            Temp4            REAL     NOT NULL,
            Pressure      REAL     NOT NULL,
            PointKey     INTEGER REFERENCES Sampling_point (id)
        );

        """
        )
        createQuery.finish()
        
    
    def insert(self, study):
        self.con.transaction()
        insertQuery = QSqlQuery(self.con)
        
        insertQuery.prepare(
            """
            INSERT INTO CleanedMeasures (
                Date,
                TempBed,
                Temp1,
                Temp2,
                Temp3,
                Temp4,
                Pressure,
                PointKey
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
    
        points = study.getPointsDb()
        
        
        for point in points:
            df_processed_temp = pd.read_csv(study.rootDir + "/" + point.name + "/processed_data/processed_temperatures.csv")
            df_processed_press = pd.read_csv(study.rootDir + "/" + point.name + "/processed_data/processed_pressures.csv")
            df_processed_measures = df_processed_temp.merge(df_processed_press)
            
            df = df_processed_measures
            col = df.columns
            
            pointKey = SamplingPointDb(self.con).getIdByname(point.name)
            
            for ind in df.index:
                insertQuery.addBindValue(str(df[col[0]][ind]))
                insertQuery.addBindValue(str(df[col[-1]][ind]))
                insertQuery.addBindValue(str(df[col[1]][ind]))
                insertQuery.addBindValue(str(df[col[2]][ind]))
                insertQuery.addBindValue(str(df[col[3]][ind]))
                insertQuery.addBindValue(str(df[col[4]][ind]))
                insertQuery.addBindValue(str(df[col[5]][ind]))
                insertQuery.addBindValue(str(pointKey))
                
                insertQuery.exec_()
        insertQuery.finish()
        
        self.con.commit()
            
        insertQuery.exec_()
        insertQuery.finish()

        self.con.commit()
        
    def getIdDate(self, date: str):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Date where Date = :date")
        selectQuery.bindValue(":date", date)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id

    def update(self, df, pointKey):
        self.con.transaction()

        deleteQuery = QSqlQuery(self.con)
        statement = f'DELETE FROM CleanedMeasures WHERE PointKey = {pointKey}'
        deleteQuery.exec(statement)
        deleteQuery.finish()

        insertQuery = QSqlQuery(self.con)
        insertQuery.prepare(
            """
            INSERT INTO CleanedMeasures (
                Date,
                TempBed,
                Temp1,
                Temp2,
                Temp3,
                Temp4,
                Pressure,
                PointKey
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        )
        col = df.columns
        for ind in df.index:
            dateId = self.getIdDate(str(df[col[0]][ind]))
            insertQuery.addBindValue(dateId)
            insertQuery.addBindValue(str(df[col[1]][ind]))
            insertQuery.addBindValue(str(df[col[3]][ind]))
            insertQuery.addBindValue(str(df[col[4]][ind]))
            insertQuery.addBindValue(str(df[col[5]][ind]))
            insertQuery.addBindValue(str(df[col[6]][ind]))
            insertQuery.addBindValue(str(df[col[2]][ind]))
            insertQuery.addBindValue(str(pointKey))
            
            insertQuery.exec_()
        insertQuery.finish()

        self.con.commit()
        
    def getIdDate(self, date: str):
        selectQuery = QSqlQuery(self.con)
        selectQuery.prepare("SELECT id FROM Date where Date = :date")
        selectQuery.bindValue(":date", date)
        selectQuery.exec_()
        
        selectQuery.next()
        id = int(selectQuery.value(0))
        selectQuery.finish()
        return id