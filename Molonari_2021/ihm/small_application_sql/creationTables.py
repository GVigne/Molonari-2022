from PyQt5.QtSql import QSqlQuery

def createTableMeasures(connection):
    createTablesQuery = QSqlQuery(connection)
    createTablesQuery.exec_(
        """
        CREATE TABLE measures_temp (
        id          INTEGER UNIQUE
                            PRIMARY KEY AUTOINCREMENT,
        date        TIME    NOT NULL
                            UNIQUE,
        t1          REAL,
        t2          REAL,
        t3          REAL,
        t4          REAL,
        point_key   INTEGER,
        uncertaincy REAL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE measures_press (
        id          INTEGER UNIQUE
                            PRIMARY KEY AUTOINCREMENT
                            REFERENCES measures_temp (id),
        date        TIME    NOT NULL
                            UNIQUE,
        pressure    REAL    NOT NULL,
        bed_temp    REAL,
        point_key   INTEGER,
        uncertaincy REAL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE processed_measures (
        id            INTEGER  PRIMARY KEY AUTOINCREMENT,
        date          DATETIME UNIQUE,
        temp_bed      REAL     NOT NULL,
        t1            REAL     NOT NULL,
        t2            REAL     NOT NULL,
        t3            REAL     NOT NULL,
        t4            REAL     NOT NULL,
        pressure      REAL     NOT NULL,
        point_key     INTEGER,
        uncertainties INTEGER
        );

        """
    )
    
    createTablesQuery.finish()

