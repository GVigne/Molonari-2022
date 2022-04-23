import sys, os

from pkg_resources import run_script
import numpy as np
import pandas as pd
from scipy import stats
# Import PyQt sub-modules
from PyQt5 import QtWidgets, QtCore, uic
# Import PyQt5.QtSql classes 
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel

# Import matplolib backend for PyQt
# https://www.pythonguis.com/tutorials/plotting-matplotlib/
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from scipy.signal import savgol_filter

from dialogcleanpoints import DialogCleanPoints
from dialogscript import DialogScript

# Load "UI" (user interface) XML file produced by QtDesigner
# and construct an object which inherits from the global parent class (PyQt5.QtWidgets.QDialog)
# See https://doc.qt.io/qtforpython-5/PySide2/QtUiTools/ls.loadUiType.html
# This function returns a pair of "types" : (generated_class, base_class) :
#  - generated_class: Ui_TemperatureViewer (contains all graphical controls/views defined with QtDesigner
#  - base_class: PyQt5.QtWidgets.QDialog (parent class of the UI)
From_sqlgridview = uic.loadUiType(os.path.join(os.path.dirname(__file__),"cleanupmain.ui"))


class MplCanvasTimeCompare(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeCompare, self).__init__(self.fig)

    def refresh_compare(self, df_or, df_cleaned,id):
        suffix_or = "_or"
        varOr = df_or.dropna()[['date',id]]
        df_compare_or = df_or[["date",id]].join(varOr.set_index("date"),on="date",rsuffix=suffix_or)
        df_compare_or['missing'] = df_compare_or[list(df_compare_or.columns)[-1]]

        df_compare_or.loc[np.isnan(df_compare_or['missing']),'missing'] = True
        df_compare_or.loc[df_compare_or['missing'] != True, 'missing'] = False
        
        df_compare_or['date'] = mdates.date2num(df_compare_or['date'])
        # df_compare_or[df_compare_or['missing'] == False].plot(x='date',y=id,ax = self.axes)
        df_compare_or[df_compare_or['missing'] == True].plot.scatter(x='date',y=id,c = 'g',s = 3,ax = self.axes)
        # self.format_axes()
        # self.fig.canvas.draw()
        
        suffix_cl = '_cleaned'
        varCleaned = df_cleaned[["date",id]].dropna()
        df_compare = varOr.join(varCleaned.set_index("date"),on="date",rsuffix=suffix_cl)
        df_compare['outliers'] = df_compare[list(df_compare.columns)[-1]]

        df_compare.loc[np.isnan(df_compare['outliers']),'outliers'] = True
        df_compare.loc[df_compare['outliers'] != True, 'outliers'] = False
        
        df_compare['date'] = mdates.date2num(df_compare['date'])
        df_compare[df_compare['outliers'] == False].plot(x='date',y=id,ax = self.axes)
        df_compare[df_compare['outliers'] == True].plot.scatter(x='date',y=id,c = 'r',s = 3,ax = self.axes)
        self.format_axes()
        self.fig.canvas.draw()

    def refresh(self,df_cleaned,id):
        varCleaned = df_cleaned[["date",id]].dropna()
        varCleaned['date'] = mdates.date2num(varCleaned['date'].copy())
        varCleaned.plot(x='date',y=id,ax = self.axes)       
        self.format_axes()
        self.axes.set_ylabel(id)
        self.fig.canvas.draw()

    def format_axes(self):
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))

    def clear(self):
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)
     
class LoadingError(Exception):
    """
    Override Exception base class for particular case of a file loading error
    """
    def __init__(self, object: str, reason: str):
        self.object = object
        self.reason = reason

    # Override __str__ operator for string representation
    # See https://www.pythontutorial.net/python-oop/python-__str__
    def __str__(self): ####
        return f"Error : Couldn't load {self.object}\n{self.reason}" ####
    
    
def displayCriticalMessage(mainMessage: str, infoMessage: str=''):
    """
    Display a "critical" popup dialog with a main message and a secondary detailed message
    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(mainMessage) ####
    msg.setInformativeText(infoMessage) ####
    msg.exec() 


def loadCSV(path: str):
    """
    Open and read the CSV file
    """
    df = pd.read_csv(path)
    
    return df

def loadRawCSV(path: str):
    df = pd.read_csv(path,header=1)
    return df

def cleanupTempZH(df: pd.DataFrame):
    """
    Cleanup raw temperature Pandas Dataframe:
        - Rename the columns,
        - Remove lines having missing values 
        - Remove unexpected last columns and
        - Delete Index column
    
    This function works directly on the giving Pandas Dataframe (in place)
    """
    # New column names
    val_cols = ["Temp1", "Temp2", "Temp3", "Temp4"]
    all_cols = ["Idx", "Date"] + val_cols

    # Rename the 6 first columns
    for i in range(0, len(all_cols)) :
        df.columns.values[i] = all_cols[i]
    # Remove lines having at least one missing value
    df.dropna(subset=val_cols,inplace=True)
    # Remove last columns
    df.dropna(axis=1,inplace=True)
    # Remove first column
    df.drop(["Idx"],axis=1,inplace=True)

def cleanupPressure(df: pd.DataFrame):
    val_cols = ["tension_V", "Temp_Stream"]
    all_cols = ["Idx", "Date"] + val_cols
    # Rename the 6 first columns
    for i in range(0, len(all_cols)) :
        df.columns.values[i] = all_cols[i]
    # Remove lines having at least one missing value
    df.dropna(subset=val_cols,inplace=True)
    # Remove last columns
    df.dropna(axis=1,inplace=True)
    # Remove first column
    df.drop(["Idx"],axis=1,inplace=True)

def convertDates(df: pd.DataFrame):
    """
    Convert dates from a list of strings by testing several different input formats
    Try all date formats already encountered in data points
    If none of them is OK, try the generic way (None)
    If the generic way doesn't work, this method fails
    (in that case, you should add the new format to the list)
    
    This function works directly on the giving Pandas dataframe (in place)
    This function assumes that the first column of the given Pandas dataframe
    contains the dates as characters string type
    
    For datetime conversion performance, see:
    See https://stackoverflow.com/questions/40881876/python-pandas-convert-datetime-to-timestamp-effectively-through-dt-accessor
    """
    formats = ("%m/%d/%y %H:%M:%S", "%m/%d/%y %I:%M:%S %p",
               "%d/%m/%y %H:%M",    "%d/%m/%y %I:%M %p",
               "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p", 
               "%d/%m/%Y %H:%M",    "%d/%m/%Y %I:%M %p",
               "%y/%m/%d %H:%M:%S", "%y/%m/%d %I:%M:%S %p", 
               "%y/%m/%d %H:%M",    "%y/%m/%d %I:%M %p",
               "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %I:%M:%S %p", 
               "%Y/%m/%d %H:%M",    "%Y/%m/%d %I:%M %p",
               None)
    times = df[df.columns[0]]
    for f in formats:
        try:
            # Convert strings to datetime objects
            new_times = pd.to_datetime(times, format=f)
            # Convert datetime series to numpy array of integers (timestamps)
            new_ts = new_times.values.astype(np.int64)
            # If times are not ordered, this is not the appropriate format
            test = np.sort(new_ts) - new_ts
            if np.sum(abs(test)) != 0 :
                #print("Order is not the same")
                raise ValueError()
            # Else, the conversion is a success
            #print("Found format ", f)
            df[df.columns[0]] = new_times
            return
        
        except ValueError:
            #print("Format ", f, " not valid")
            continue
    
    # None of the known format are valid
    raise ValueError("Cannot convert dates: No known formats match your data!")


class TemperatureViewer(From_sqlgridview[0], From_sqlgridview[1]):
    """
    Dialog class that inherits from BOTH :
     - the QtDesigner generated_class: UI_TemperatureViewer 
     - the UI base_class (here QDialog)
    This offers the possibility to access directly the graphical controls variables (i.e. self.editFile)
    """
    def __init__(self):
        """
        Constructor
        """
        # Call the constructor of parent classes (super)
        super(TemperatureViewer, self).__init__()
        # Configure the initial values of graphical controls 
        # See https://doc.qt.io/qt-5/designer-using-a-ui-file-python.html
        self.setupUi(self)
        
        # Connect the buttons

        self.pushButtonBrowseRawZH.clicked.connect(self.browseFileRawZH)
        self.pushButtonBrowseRauPressure.clicked.connect(self.browseFileRawPressure)
        self.pushButtonBrowseCalibration.clicked.connect(self.bbrowseFileCalibration)
        self.pushButtonSelectPoints.clicked.connect(self.selectPoints)
        self.pushButtonEditCode.clicked.connect(self.editScript)

        self.checkBoxChanges.clicked.connect(self.plotPrevisualizedVar)
        self.checkBoxFilter.clicked.connect(self.triggerSetFilter)
        self.pushButtonResetVar.clicked.connect(self.resetCleanVar)
        self.pushButtonResetAll.clicked.connect(self.resetCleanAll)

        # connects the slot function and makes the argument of the band int type
        self.buttonGroupMethod.setId(self.radioButtonZScore,1)
        self.buttonGroupMethod.setId(self.radioButtonIQR,2)
        self.buttonGroupMethod.setId(self.radioButtonNone,3)
        
        self.buttonGroupMethod.buttonClicked.connect(self.selectMethod)
        self.radioButtonNone.setChecked(True)

        self.checkBoxChanges.setChecked(True)
        self.checkBoxFilter.setChecked(False)
        # Remove existing SQL database file (if so)
        self.sql = "molonari_grid_temp.sqlite"
        if os.path.exists(self.sql):
            os.remove(self.sql)

        # Connect to the SQL database and display a critical message in case of failure
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sql)
        if not self.con.open():
            displayCriticalMessage(f"{str(self.con.lastError().databaseText())}", "Cannot open SQL database")

        self.rawCon = QSqlDatabase.addDatabase("QSQLITE") #Creates the connection with a database
        self.rawCon.setDatabaseName("molonari_raw.sqlite") #The database is self.sql
        if not self.rawCon.open(): #Try to open the connection. If it fails, returns error
            displayCriticalMessage(self.rawCon.lastError().databaseText(), "There was an error opening the database")
            sys.exit(1)

        # Create data models and associate to corresponding viewers

        self.getDF()
        self.comboBoxRawVar.addItems(self.varList[1:])
        self.varName = self.comboBoxRawVar.currentText
        self.comboBoxRawVar.currentIndexChanged.connect(self.plotPrevisualizedVar)

        self.method_dic = dict.fromkeys(self.varList[1:],self.buttonGroupMethod.button(3))
        self.filter_dic = dict.fromkeys(self.varList[1:],False)

        self.plotPrevisualizedVar()

        
        
    def __del__(self):
        """
        Destructor
        """
        # Close the SQL connection
        self.con.close() ####
        self.rawCon.close()


    def readCSV(self):
        """
        Read the provided CSV files (depths values and gridded temperatures)
        and load it into a Pandas dataframes
        """
        # Retrieve the CSV file paths from lineEditDepthFile and lineEditTempFile
        depthfile = self.lineEditDepthFile.text()
        gridfile = self.lineEditTempFile.text()
        if depthfile and gridfile:
            try :
                # Load the CSV file
                dfdepth = loadCSV(depthfile)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different depth file")
                return pd.DataFrame(), pd.DataFrame()
            
            try :
                # Load the CSV file
                dftemp = loadCSV(gridfile)
                
                # Convert the dates
                convertDates(dftemp)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different temperatures file")
                return pd.DataFrame(), pd.DataFrame()
            
        return dfdepth, dftemp
    
    def readRawZHCSV(self):
        trawfile = self.lineEditRawZHFile.text()
        if trawfile:
            try :
                # Load the CSV file
                dftemp = loadRawCSV(trawfile)
                # Cleanup the dataframe
                cleanupTempZH(dftemp)
                # Convert the dates
                convertDates(dftemp)
                return dftemp

            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different file")
    
        # If failure, return an empty dataframe
        return pd.DataFrame()

    def readRawPressureCSV(self):
        trawfile = self.lineEditRawPressureFile.text()
        if trawfile:
            try :
                # Load the CSV file
                dftemp = loadRawCSV(trawfile)
                # Cleanup the dataframe
                cleanupPressure(dftemp)
                # Convert the dates
                convertDates(dftemp)
                return dftemp

            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different file")
    
        # If failure, return an empty dataframe
        return pd.DataFrame()
    
    def readCalibrationCSV(self):
        path = self.lineEditCalibrationFile.text()
        
        if path:
            try :
                # Load the CSV file
                dftemp = loadCSV(path)
                return dftemp

            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different file")
    
        # If failure, return an empty dataframe
        return pd.DataFrame()
    
    def writeSQL(self, dfdepth: pd.DataFrame, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Number of depths
        self.ndepth = df.shape[1] - 1 # Remove Date/Time column
        if self.ndepth != dfdepth.shape[0]:
            displayCriticalMessage(f"{str(e)}", "Number of depths doesn't match")
            return
            
        # Create the table for storing the temperature measures (id, date, temp*4)
        createTableQuery = QSqlQuery(self.con) 
        createTableQuery.exec(
            """
            CREATE TABLE solved_depth (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                depth FLOAT NOT NULL
            )
            """
        )
        createTableQuery.finish() #### Do not forget to finish your queries (close the transaction and free memory)
        
        # Insert temperatures
        insertDataQuery = QSqlQuery(self.con)
        insertDataQuery.prepare(
            f"""
            INSERT INTO solved_depth (
                depth
            )
            VALUES (?)
            """
        )
        for row in range(0, dfdepth.shape[0]): # TODO Not efficient !!
            insertDataQuery.addBindValue(float(dfdepth.iloc[row, 0]))
            insertDataQuery.exec()
        insertDataQuery.finish()


        # Create the table for storing the solved temperature (id, date, temp in ndepth columns)
        createTableQuery.exec(
            f"""
            CREATE TABLE solved_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                date DATETIME NOT NULL,
                {', '.join(['d_' + str(i) + ' FLOAT NOT NULL' for i in range(1, self.ndepth+1)])}
            )
            """
        )
        createTableQuery.finish()

        # For large dataset, try a transaction :
        self.con.transaction()
        
        # Insert temperatures
        insertDataQuery.prepare(
            f"""
            INSERT INTO solved_temp (
                date,
                {', '.join(['d_' + str(i) for i in range(1, self.ndepth+1)])}
            )
            VALUES (?, {', '.join('?'*self.ndepth)})
            """
        )
        # https://stackoverflow.com/questions/24245245/pyqt-qstandarditemmodel-how-to-get-a-row-as-a-list
        for row in range(0, df.shape[0]): # TODO : There is a limit of the query size ! (no more than 250 rows inserted)
            insertDataQuery.addBindValue(str(df.iloc[row,0]))
            for col in range(1, df.shape[1]): # TODO Not efficient !!
                insertDataQuery.addBindValue(float(df.iloc[row, col]))
            insertDataQuery.exec()
        insertDataQuery.finish()
        
        self.con.commit()

    def writeRawZHSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Remove the previous measures table (if so)
        dropTableQuery = QSqlQuery(self.rawCon) # Connection mustt be specified in each query
        
        ### TODO
        dropTableQuery.exec("DROP TABLE IF EXISTS ZH") 
        ### End TODO
        dropTableQuery.finish()
        
        # Create the table for storing the temperature measures (id, date, temp*4)
        ### TODO

        createTableQuery = QSqlQuery(self.rawCon) 
        # Columns and their data type are defined
        createTableQuery.exec(
            """
            CREATE TABLE IF NOT EXISTS ZH (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                date TIMESTAMP,
                t1 FLOAT,
                t2 FLOAT,
                t3 FLOAT,
                t4 FLOAT           
            )
            """
        )
        createTableQuery.finish()
        ### End TODO

        # Construct the dynamic insert SQL request and execute it
        ### TODO
        
        dynamicInsertQuery = QSqlQuery(self.rawCon)
        # In a dynamic query, first of all the query is prepared with placeholders (?)
        dynamicInsertQuery.prepare(
            """
            INSERT INTO ZH (
                date,
                t1,
                t2,
                t3,
                t4
            )
            VALUES (?, ?, ?, ?, ?)
            """
        )

         
        for i in range(df.shape[0]): 
            val = tuple(df.iloc[i])  # Each row of the DataFrame is selected as a tuple
            dynamicInsertQuery.addBindValue(str(val[0])) # The first placeholder is for the date. Then, it should be a string
            for j in range(1,5):
                dynamicInsertQuery.addBindValue(float(val[j])) # The rest are for the temperatures (which are supposed to be float instead of np.float64)
            dynamicInsertQuery.exec() # Once the placeholders are filled, the query is executed
        dynamicInsertQuery.finish()
        ### End TODO

    def writeRawPressureSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Remove the previous measures table (if so)
        dropTableQuery = QSqlQuery(self.rawCon) # Connection mustt be specified in each query
        
        ### TODO
        dropTableQuery.exec("DROP TABLE IF EXISTS Pressure") 
        ### End TODO
        dropTableQuery.finish()
        
        # Create the table for storing the temperature measures (id, date, temp*4)
        ### TODO

        createTableQuery = QSqlQuery(self.rawCon) 
        # Columns and their data type are defined
        createTableQuery.exec(
            """
            CREATE TABLE IF NOT EXISTS Pressure (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                date TIMESTAMP,
                tension FLOAT,
                t_stream FLOAT      
            )
            """
        )
        createTableQuery.finish()
        ### End TODO

        # Construct the dynamic insert SQL request and execute it
        ### TODO
        
        dynamicInsertQuery = QSqlQuery(self.rawCon)
        # In a dynamic query, first of all the query is prepared with placeholders (?)
        dynamicInsertQuery.prepare(
            """
            INSERT INTO Pressure (
                date,
                tension,
                t_stream
            )
            VALUES (?, ?, ?)
            """
        )

         
        for i in range(df.shape[0]): 
            val = tuple(df.iloc[i])  # Each row of the DataFrame is selected as a tuple
            dynamicInsertQuery.addBindValue(str(val[0])) # The first placeholder is for the date. Then, it should be a string
            for j in range(1,3):
                dynamicInsertQuery.addBindValue(float(val[j])) # The rest are for the temperatures (which are supposed to be float instead of np.float64)
            dynamicInsertQuery.exec() # Once the placeholders are filled, the query is executed
        ### End TODO
        dynamicInsertQuery.finish()

    def writeCalibrationSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Remove the previous measures table (if so)
        dropTableQuery = QSqlQuery(self.rawCon) # Connection mustt be specified in each query        
        dropTableQuery.exec("DROP TABLE IF EXISTS Calibration") 
        dropTableQuery.finish()
        
        # Create the table for storing the temperature measures (id, date, temp*4)
        createTableQuery = QSqlQuery(self.rawCon) 
        # Columns and their data type are defined
        createTableQuery.exec(
            """
            CREATE TABLE IF NOT EXISTS Calibration (
                Var VARCHAR(20),
                Value VARCHAR(40)  
            )
            """
        )
        createTableQuery.finish()
        # Construct the dynamic insert SQL request and execute it
        dynamicInsertQuery = QSqlQuery(self.rawCon)
        # In a dynamic query, first of all the query is prepared with placeholders (?)
        dynamicInsertQuery.prepare(
            """
            INSERT INTO Calibration (
                Var,
                Value
            )
            VALUES (?, ?)
            """
        )

        for i in range(df.shape[0]): 
            val = tuple(df.iloc[i])  # Each row of the DataFrame is selected as a tuple
            dynamicInsertQuery.addBindValue(str(val[0]))
            dynamicInsertQuery.addBindValue(str(val[1]))
            dynamicInsertQuery.exec() # Once the placeholders are filled, the query is executed
        dynamicInsertQuery.finish()

    def readCalibrationSQL(self):
        """
        Read the SQL database and display measures
        """
        print("Tables in the SQL Database:", self.rawCon.tables())

        # Read the database and print its content
        selectDataQuery = QSqlQuery(self.rawCon)
        selectDataQuery.exec("SELECT Var, Value FROM Calibration")

        while selectDataQuery.next() :
            print("  ", selectDataQuery.value(0),
                        selectDataQuery.value(1))
        selectDataQuery.finish()    

        selectDataQuery = QSqlQuery(self.rawCon)
        selectDataQuery.exec("PRAGMA table_info(Calibration)") #get column names
        while selectDataQuery.next():
            print(selectDataQuery.value(1))
        selectDataQuery.finish()
               
    def browseFileTemp(self):
        """
        Display an "Open file dialog" when the user click on the 'Browse' button then
        store the selected CSV file path in the LineEdit (solved temperature)
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Solved Temperature File")[0]
        if filePath:
            self.lineEditTempFile.setText(filePath)
        
    def browseFileDepth(self):
        """
        Display an "Open file dialog" when the user click on the 'Browse' button then
        store the selected CSV file path in the LineEdit (solved depths)
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Solved Depths File")[0]
        if filePath:
            self.lineEditDepthFile.setText(filePath)
    
    def browseFileRawZH(self):
        """
        Get the CSV file for the raw data to be cleaned up
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Raw ZH File",'/home/jurbanog/T3/MOLONARI_1D_RESOURCES/sampling_points/Point034', filter='*.csv')[0]
        if filePath:
            self.lineEditRawZHFile.setText(filePath)
            df = self.readRawZHCSV()            
            # Dump the measures to SQL database
            self.writeRawZHSQL(df)

    def browseFileRawPressure(self):
        """
        Get the CSV file for the raw data to be cleaned up
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Raw Pressure File",'/home/jurbanog/T3/MOLONARI_1D_RESOURCES/sampling_points/Point034', filter='*.csv')[0]
        if filePath:
            self.lineEditRawPressureFile.setText(filePath)
            df = self.readRawPressureCSV()            
            # Dump the measures to SQL database
            self.writeRawPressureSQL(df)
            
    def bbrowseFileCalibration(self):
        """
        Get the CSV file for the raw data to be cleaned up
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Calibration File",'/home/jurbanog/T3/MOLONARI_1D_RESOURCES/configuration/pressure_sensors', filter='*.csv')[0]
        if filePath:
            self.lineEditCalibrationFile.setText(filePath)
            df = self.readCalibrationCSV()            
            # Dump the measures to SQL database
            self.writeCalibrationSQL(df)

    def load_pandas(self,db, statement, cols):    
        query = QSqlQuery(db)
        query.exec(statement)
        table = []
        while query.next():
            values = []
            for i in range(query.record().count()):
                values.append(query.value(i))
            table.append(values)
        df = pd.DataFrame(table)
        # for i in range(0, len(cols)) :
        #     df.columns.values[i] = cols[i]
        df.columns = cols
        return df
    
    def iqr(self,df_in, col_name):

        q1 = df_in[col_name].quantile(0.25)
        q3 = df_in[col_name].quantile(0.75)
        iqr = q3-q1 #Interquartile range
        fence_low  = q1-1.5*iqr
        fence_high = q3+1.5*iqr
        df_out = df_in.copy()
        df_out[col_name] = df_in[col_name].loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
        return df_out

    def remove_outlier_z(self, df_in, col_name):
        df_out = df_in.copy()
        var = df_in[col_name].copy().dropna()
        df_out[col_name]= var.loc[(np.abs(stats.zscore(var)) < 3)]
        return df_out

    def plotPrevisualizedVar(self):
        self.method_dic[self.varName()].setChecked(True)
        self.checkBoxFilter.setChecked(self.filter_dic[self.varName()])
        "Refresh plot"
        try: # this try can be erased TODO
            if type(self.mplPrevisualizeCurve) == MplCanvasTimeCompare:
                id = self.comboBoxRawVar.currentText()
                self.mplPrevisualizeCurve.clear()

                if self.checkBoxChanges.isChecked():
                    self.mplPrevisualizeCurve.refresh_compare(self.df_loaded, self.df_cleaned, id)
                else:
                    self.mplPrevisualizeCurve.refresh(self.df_cleaned, id)
                

                self.widgetRawData.addWidget(self.mplPrevisualizeCurve)

        except AttributeError:
            print("Entered exception")
            pass
            
    def getScript(self):
        try:
            with open('saved_text.txt', 'r') as f:
                sample_text = f.read()
                f.close()
            # with open(os.path.join(pointDir,"script_"+name+".txt")) as f:
            #     sample_text = f.read()
        except:
            print("No saved script, show sample script")
            with open(os.path.join(os.path.dirname(__file__),"sample_text.txt")) as f:
                sample_text = f.read()
                f.close()
        # scriptpartiel = plainTextEdit.toPlainText()
        scriptindente = sample_text.replace("\n", "\n   ")
        script = "def fonction(self, df_ZH, df_Pressure, df_Calibration): \n   " + scriptindente + "\n" + "   return(1)"
        return(script)

    def cleanup(self, script, df_ZH, df_Pressure, df_Calibration):
        scriptDir = "script.py"
        # sys.path.append(self.pointDir) # TODO uncomment

        with open(scriptDir, "w") as f:
            f.write(script)
            f.close()

        # There are different error in the script, sometimes it will cause the import step to fail, in this case we still have to remove the scripy.py file.
        try:
            from script import fonction
        except Exception as e:
            raise e
        finally:
            os.remove(scriptDir)
            del sys.modules["script"]

        try :
            fonction(self,df_ZH, df_Pressure, df_Calibration)

            #On réécrit les csv:
            # os.remove(self.tprocessedfile)
            # os.remove(self.pprocessedfile)
            # new_dft.to_csv(self.tprocessedfile, index=False)
            # new_dfp.to_csv(self.pprocessedfile, index=False)

            # self.dftemp = readCSVWithDates(self.tprocessedfile)
            # self.dfpress = readCSVWithDates(self.pprocessedfile)

            return(1)
        
        except Exception as e :
            raise e
        
    def runScript(self, df_ZH, df_Pressure, df_Calibration):
        df_ZH = df_ZH.copy()
        df_Pressure = df_Pressure.copy()
        df_Calibration = df_Calibration.copy()
        script = self.getScript()
        print("Cleaning data...")
        
        try :
            self.cleanup(script, df_ZH, df_Pressure, df_Calibration)
            print("Data successfully cleaned !...")

            # Save the modified text
            # with open(os.path.join(self.pointDir,"script_"+self.point.name+".txt"),'w') as file:
            #     file.write(scriptpartiel)
            print("Script successfully saved")
            
            
        except Exception as e :
            print(e, "==> Clean-up aborted")
            displayCriticalMessage("Error : Clean-up aborted", f'Clean-up was aborted due to the following error : \n"{str(e)}" ' )
            # self.cleanup()

    def editScript(self):
        dig = DialogScript()
        res = dig.exec()
        if res == QtWidgets.QDialog.Accepted:
            self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration)
        self.plotPrevisualizedVar()
    
    # Define the selectMethod function and edit thhe sample_text.txt
    def selectMethod(self,object):
        id = self.buttonGroupMethod.id(object)
        varIndex = self.varList.index(self.varName())
        self.method_dic[self.varName()] = self.buttonGroupMethod.button(id)

        try: 
            with open('saved_text.txt', 'r') as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()
        except FileNotFoundError:
            with open('sample_text.txt', 'r') as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()

        method_key = '# METHOD'
        for i in range(len(data)):
            if data[i].find(method_key) != -1:
                methodsLine = i
            
        # now change the n-th line
        if id == 1:
            method = "remove_outlier_z"
        elif id == 2:
            method = "iqr"
        else:
            method = None
        
        if method:
            data[methodsLine+varIndex*2] = f'self.df_cleaned = self.{method}(self.df_cleaned,"{self.varName()}")\n'
        else:
            data[methodsLine+varIndex*2] = "\n"

        # write everything back
        with open('saved_text.txt', 'w') as file:
            file.writelines( data )
            file.close()
        self.previsualizeCleaning()

    def triggerSetFilter(self):
        self.setFilter(self.varName())
    
    def setFilter(self,var):
        self.filter_dic[var] = self.checkBoxFilter.isChecked()
        try: # TODO make a function so it doesn't repeat
            with open('saved_text.txt', 'r') as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()
        except FileNotFoundError:
            with open('sample_text.txt', 'r') as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()

        filter_key = '# SMOOTHING'
        for i in range(len(data)):
            if data[i].find(filter_key) != -1:
                filterLine = i
        
        data[filterLine+1] = f'to_filter = {self.filter_dic}\n'

        with open('saved_text.txt', 'w') as file: # TODO make a function so it doesn't repeat
            file.writelines( data )
            file.close()
        self.previsualizeCleaning()

    def previsualizeCleaning(self):
        "Cleans data and shows a previsuaization"
        self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration)

        # selected_df = pd.read_csv("selected_points.csv")

        # for i in self.varList[1:]:
        #     df_var = selected_df[["date",i]].dropna()
        #     values = self.df_cleaned.apply(lambda x: np.nan if mdates.date2num(x['date']) in list(mdates.date2num(df_var['date'])) else x[i],axis=1)
        #     self.df_cleaned.loc[:,i] = values

        self.plotPrevisualizedVar()

    def getDF(self):
        "Gets the unified pandas with charge_diff calculated and whitout tension voltage"
        self.df_ZH = self.load_pandas(self.rawCon, "SELECT date, t1, t2, t3, t4 FROM ZH", ["date", "t1", "t2", "t3", "t4"])
        convertDates(self.df_ZH)
        self.df_Pressure = self.load_pandas(self.rawCon, "SELECT date, tension, t_stream FROM Pressure", ["date", "tension", "t_stream"])
        convertDates(self.df_Pressure)
        self.df_Calibration = self.load_pandas(self.rawCon, "SELECT Var, Value FROM Calibration", ["Var", "Value"])

        self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration)
        # intercept = float(df_Calibration.iloc[2][list(df_Calibration.columns)[-1]])
        # dUdH = float(df_Calibration.iloc[3][list(df_Calibration.columns)[-1]])
        # dUdT = float(df_Calibration.iloc[4][list(df_Calibration.columns)[-1]])

        # df_Pressure["charge_diff"] = (df_Pressure["tension"]-df_Pressure["t_stream"]*dUdT-intercept)/dUdH
        # df_Pressure.drop(labels="tension",axis=1,inplace=True)

        # self.df_loaded = df_Pressure.merge(df_ZH, how='outer', on="date").sort_values('date').reset_index().drop('index',axis=1)
        # self.varList = list(self.df_loaded.columns)
        # self.df_cleaned = self.df_loaded.copy().dropna()
        self.df_selected = pd.DataFrame(columns=self.varList)
        self.df_selected.to_csv("selected_points.csv")

        self.mplPrevisualizeCurve = MplCanvasTimeCompare()
        self.toolBar = NavigationToolbar2QT(self.mplPrevisualizeCurve,self)
        self.widgetToolBar.addWidget(self.toolBar)

    def selectPoints(self):
        dig = DialogCleanPoints()
        dig.plot(self.varName(), self.df_loaded, self.df_selected)
        res = dig.exec()
        if res == QtWidgets.QDialog.Accepted:           
            selection = dig.mplSelectCurve.df_selected[["date",self.varName()]]
            self.df_selected = self.df_selected.merge(selection,on=["date"],how="outer",suffixes=(None,"_sel"))           
            self.df_selected[self.varName()] = self.df_selected[self.varName()+"_sel"]
            self.df_selected.drop(self.varName()+"_sel",axis=1, inplace=True)
            self.df_selected.dropna(how="all",subset=self.varList[1:],inplace=True)
            print(self.df_selected)
            self.df_selected.to_csv("selected_points.csv")
            
        self.previsualizeCleaning()

    def resetCleanVar(self):
        self.df_cleaned[self.varName()] = self.df_loaded[self.varName()]

        nan_values = np.empty((self.df_selected.shape[0],1))
        nan_values.fill(np.nan)
        self.df_selected[self.varName()] = nan_values
        self.df_selected.dropna(how="all",subset=self.varList[1:],inplace=True)
        self.df_selected.to_csv("selected_points.csv")

        obj = self.buttonGroupMethod.button(3)
        self.selectMethod(obj)
        self.checkBoxFilter.setChecked(False)
        self.setFilter(self.varName())

    def resetCleanAll(self):
        self.df_selected = pd.DataFrame(columns=self.varList)
        self.df_selected.to_csv("selected_points.csv")
        # self.df_cleaned = self.df_loaded.copy().dropna() # TODO Is it ok the dropna()? 
        self.method_dic = dict.fromkeys(self.varList[1:],self.buttonGroupMethod.button(3))
        os.remove("saved_text.txt") # TODO error
        self.checkBoxFilter.setChecked(False)
        self.previsualizeCleaning()
    
    


if __name__ == '__main__':
    """
    Main function of the script:
    - Create the QApplication object
    - Create the TemperatureViewer dialog and show it
    - Execute the infinite event loop and wait for interaction or exit
    """
    app = QtWidgets.QApplication(sys.argv)

    mainWin = TemperatureViewer()
    mainWin.show()

    app.exec_()
    try:
        os.remove("saved_text.txt")
    except FileNotFoundError:
        pass
