import sys
import os
from PyQt5.QtSql import QSqlDatabase, QSqlQuery

############################# Create BDD

print(os.path)
if os.path.exists("molonari.sqlite"):
    os.remove("molonari.sqlite")

con = QSqlDatabase.addDatabase("QSQLITE")
con.setDatabaseName("molonari.sqlite")

con.open()

# Open the connection and handle errors
if not con.open():
    print("Database Error: %s" % con.lastError().databaseText())
    sys.exit(1)
    
############################# Create tables

createTableQuery = QSqlQuery()
createTableQuery.exec(
    """
    CREATE TABLE points (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        name VARCHAR(40) NOT NULL,
        pressure_sensor VARCHAR(50) NOT NULL,
        implantation_date TIMESTAMP NOT NULL
    )
    """
)
createTableQuery.finish()

createTableQuery.exec(
    """
    CREATE TABLE measures (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        date TIMESTAMP NOT NULL,
        p FLOAT NOT NULL,
        t0 FLOAT NOT NULL,
        t1 FLOAT NOT NULL,
        t2 FLOAT NOT NULL,
        t3 FLOAT NOT NULL,
        t4 FLOAT NOT NULL
    )
    """
)
createTableQuery.finish()

print("Tables in the BDD:", con.tables())


############################ Populate tables

# Points

pt_name = "Point66"
pt_psensor = "P508"
pt_impdate = "2017/02/14 12:00:00"

query = QSqlQuery()
query.exec(
     f"""INSERT INTO points (name, pressure_sensor, implantation_date)
     VALUES ('{pt_name}', '{pt_psensor}', '{pt_impdate}')"""
)
query.finish()

# Measures

data = [
    ("2017/03/15 13:30:00", "1.5", "10.8", "10.6", "10.4", "10.2", "10.0"),
    ("2017/03/15 13:45:00", "2.5", "11.8", "11.6", "11.4", "11.2", "11.0"),
    ("2017/03/15 14:00:00", "3.5", "12.8", "12.6", "12.4", "12.2", "12.0"),
    ("2017/03/15 14:15:00", "4.5", "13.8", "13.6", "13.4", "13.2", "13.0"),
]
insertDataQuery = QSqlQuery()
insertDataQuery.prepare(
    """
    INSERT INTO measures (
        date,
        p,
        t0,
        t1,
        t2,
        t3,
        t4
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
)
for date, p, t0, t1, t2, t3, t4 in data:
    insertDataQuery.addBindValue(date)
    insertDataQuery.addBindValue(p)
    insertDataQuery.addBindValue(t0)
    insertDataQuery.addBindValue(t1)
    insertDataQuery.addBindValue(t2)
    insertDataQuery.addBindValue(t3)
    insertDataQuery.addBindValue(t4)
    insertDataQuery.exec()

insertDataQuery.finish()

############################# Print tables content

query = QSqlQuery()
query.exec("SELECT name, pressure_sensor, implantation_date FROM points")
name, psensor, impdate = range(3)
print("Content for Table 'points'")
while query.next() :
    print("  ", query.value(name), query.value(psensor), query.value(impdate))
query.finish()

query = QSqlQuery()
query.exec("SELECT date, p, t0, t1, t2, t3, t4 FROM measures")
date, p, t0, t1, t2, t3, t4 = range(7)
print("Content for Table 'measures'")
while query.next() :
    print("  ", query.value(date), query.value(p), query.value(t0), query.value(t1), query.value(t2), query.value(t3), query.value(t4))
query.finish()

############################## Closing database

con.close()
