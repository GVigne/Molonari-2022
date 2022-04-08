from PyQt5.QtSql import QSqlQuery

def createTableMeasures(connection):
    createTablesQuery = QSqlQuery(connection)
    
    createTablesQuery.exec_(
        """
        CREATE TABLE Labo (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR NOT NULL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE Study (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR NOT NULL,
            Labo INTEGER REFERENCES Labo (id)
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE Thermometer (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            Name      VARCHAR NOT NULL,
            Manu_name VARCHAR NOT NULL,
            Manu_ref  VARCHAR NOT NULL,
            Precision REAL    NOT NULL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE Shaft (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            Name         VARCHAR NOT NULL,
            Depth1       REAL    NOT NULL,
            Depth2       REAL    NOT NULL,
            Depth3       REAL    NOT NULL,
            Depth4       REAL    NOT NULL,
            Thermo_model INTEGER REFERENCES Thermometer (id),
            Labo         INTEGER REFERENCES Labo (id)
        );
        """
    )

    createTablesQuery.exec_(
        """
        CREATE TABLE measures_temp (
            id          INTEGER UNIQUE
                                PRIMARY KEY AUTOINCREMENT,
            date        DATETIME    NOT NULL
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
        CREATE TABLE [Pressure sensor] (
            id           INTEGER  PRIMARY KEY AUTOINCREMENT,
            Name         VARCHAR  NOT NULL,
            Datalogger   VARCHAR  NOT NULL,
            Calibration  DATETIME NOT NULL,
            Intercept    REAL     NOT NULL,
            [Du/Dh]      REAL     NOT NULL,
            [Du/Dt]      REAL     NOT NULL,
            Precision    REAL     NOT NULL,
            Thermo_model INTEGER  REFERENCES Thermometer (id),
            Labo         INTEGER  REFERENCES Labo (id)
        );
        """
    )

    
    createTablesQuery.exec_(
        """
        CREATE TABLE Uncertainties (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            sigmaT    REAL    NOT NULL,
            sigmaP    REAL    NOT NULL,
            sigmaTbed REAL    NOT NULL
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE measures_press (
            id          INTEGER UNIQUE
                                PRIMARY KEY AUTOINCREMENT,
            date        DATETIME    NOT NULL
                                UNIQUE,
            pressure    REAL,
            bed_temp     REAL,
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
            point_key     INTEGER REFERENCES [Sampling point] (id),
            uncertainties INTEGER REFERENCES Uncertainties (id)
        );

        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE [Sampling point] (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            Longitude       REAL,
            latitude        REAL,
            Implentation    DATETIME,
            Last_transfert  DATETIME,
            Delta_h         REAL    NOT NULL,
            River_bed       REAL    NOT NULL,
            Shaft           INTEGER REFERENCES Shaft (id),
            Pressure_sensor INTEGER REFERENCES [Pressure sensor] (id),
            Study           INTEGER REFERENCES Study (id)
        );
        """
    )
    
    createTablesQuery.finish()

