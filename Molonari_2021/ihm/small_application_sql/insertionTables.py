from PyQt5.QtSql import QSqlQuery

def writeRawTemperaturesSql(con, dftemp):
    con.transaction()
    
    insertTemperaturesQuery = QSqlQuery(con)
    insertTemperaturesQuery.prepare(
        """
        INSERT INTO measures_temp (
            date,
            t1,
            t2,
            t3,
            t4,
            point_key,
            uncertaincy
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
    )
    
    col = dftemp.columns
    
    for ind in dftemp.index:
        insertTemperaturesQuery.addBindValue(str(dftemp[col[0]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[1]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[2]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[3]][ind]))
        insertTemperaturesQuery.addBindValue(str(dftemp[col[4]][ind]))
        # waiting to know how to manage pointid and uncertaincy
        insertTemperaturesQuery.addBindValue("0")
        insertTemperaturesQuery.addBindValue("0")
    
        insertTemperaturesQuery.exec_()
    insertTemperaturesQuery.finish()
    con.commit()

def writeRawPressuresSql(con, dfpress):
    insertPressuresQuery = QSqlQuery(con)
    insertPressuresQuery.prepare(
        """
        INSERT INTO measures_press (
           date,
           pressure,
           bed_temp,
           point_key,
           uncertaincy
        )
        VALUES (?, ?, ?, ?, ?)
        """
    )
    
    col = dfpress.columns
    
    for ind in dfpress.index:
        insertPressuresQuery.addBindValue(str(dfpress[col[0]][ind]))
        insertPressuresQuery.addBindValue(str(dfpress[col[1]][ind]))
        insertPressuresQuery.addBindValue(str(dfpress[col[2]][ind]))
        insertPressuresQuery.addBindValue("0")
        insertPressuresQuery.addBindValue("0")
        
        insertPressuresQuery.exec_()
    insertPressuresQuery.finish()


def writeProcessedMeasuresSql(con, df):
    insertProcessedMeasuresQuery = QSqlQuery(con)
    insertProcessedMeasuresQuery.prepare(
        """
        INSERT INTO processed_measures (
            date,
            temp_bed,
            t1,
            t2,
            t3,
            t4,
            pressure,
            point_key,
            uncertainties
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    )
    
    col = df.columns
    
    for ind in df.index:
        insertProcessedMeasuresQuery.addBindValue(str(df[col[0]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[-1]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[1]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[2]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[3]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[4]][ind]))
        insertProcessedMeasuresQuery.addBindValue(str(df[col[5]][ind]))
        insertProcessedMeasuresQuery.addBindValue("0")
        insertProcessedMeasuresQuery.addBindValue("0")
        
        insertProcessedMeasuresQuery.exec_()
    insertProcessedMeasuresQuery.finish()
        
