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
            Error REAL    NOT NULL
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
            Date        DATETIME    NOT NULL
                                UNIQUE,
            Temp1          REAL,
            Temp2          REAL,
            Temp3          REAL,
            Temp4          REAL,
            Point_key   INTEGER,
        );
        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE pressure_sensor (
            id           INTEGER  PRIMARY KEY AUTOINCREMENT,
            Name         VARCHAR ,
            Datalogger   VARCHAR ,
            Calibration  DATETIME,
            Intercept    REAL,
            [Du/Dh]      REAL,
            [Du/Dt]      REAL,
            Precision    REAL,
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
            point_key     INTEGER REFERENCES Sampling_point (id),
            uncertainties INTEGER REFERENCES Uncertainties (id)
        );

        """
    )
    
    createTablesQuery.exec_(
        """
        CREATE TABLE Sampling_point (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            Name            VARCHAR,
            Notice          VARCHAR,
            Longitude       REAL,
            Latitude        REAL,
            Implentation    DATETIME,
            Last_transfert  DATETIME,
            Delta_h         REAL,
            River_bed       REAL,
            Shaft           INTEGER REFERENCES Shaft (id),
            Pressure_sensor INTEGER REFERENCES pressure_sensor (id),
            Study           INTEGER REFERENCES Study (id)
        );
        """
    )
    
    createTablesQuery.finish()

