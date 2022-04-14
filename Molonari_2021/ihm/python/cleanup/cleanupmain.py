import sys, os
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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from dialogcleanpoints import DialogCleanPoints

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
        suffix = '_cleaned'
        varCleaned = df_cleaned.dropna()[["date",id]]
        df_compare = df_or[["date",id]].join(varCleaned.set_index("date"),on="date",rsuffix=suffix)
        df_compare['outliers'] = df_compare[list(df_compare.columns)[-1]]

        df_compare.loc[np.isnan(df_compare['outliers']),'outliers'] = True
        df_compare.loc[df_compare['outliers'] != True, 'outliers'] = False

        df_compare['date'] = mdates.date2num(df_compare['date'])
        df_compare[df_compare['outliers'] == False].plot(x='date',y=id,ax = self.axes)
        df_compare[df_compare['outliers'] == True].plot.scatter(x='date',y=id,c = 'r',s = 3,ax = self.axes)
        self.format_axes()
        self.fig.canvas.draw()

    def refresh(self,df_cleaned,id):
        df = df_cleaned.copy().dropna()
        df['date'] = mdates.date2num(df['date'].copy())
        df.plot(x='date',y=id,ax = self.axes)       
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



class MplCanvasTimeScatter(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeScatter, self).__init__(self.fig)
        

    def refresh(self, times, values):
        # TODO : Still string to date conversion needed!
        self.axes.plot(mdates.date2num(times), values,'.',picker=5)
        self.format_axes()
        self.fig.canvas.draw()
    
    def click_connect(self):
        def onpick(event):
            ind = event.ind
            datax,datay = event.artist.get_data()
            datax_,datay_ = [datax[i] for i in ind],[datay[i] for i in ind]
            if len(ind) > 1:              
                msx, msy = event.mouseevent.xdata, event.mouseevent.ydata
                dist = np.sqrt((np.array(datax_)-msx)**2+(np.array(datay_)-msy)**2)
                
                ind = [ind[np.argmin(dist)]]
                x = datax[ind]
                y = datay[ind]
            else:
                x = datax_
                y = datay_
            print(datax[ind])
            print(datay[ind])
            datax = np.delete(datax,ind)
            datay = np.delete(datay,ind)
            datax = pd.Series(mdates.num2date(datax))
            # event.artist.get_figure().clear()
            # event.artist.get_figure().gca().plot(datax,datay,'.',picker=5)
            self.clear()
            self.refresh(datax,datay)
            # self.format_axes()
            # event.artist.get_figure().gca().plot(x,y,'.',color="red")  
            # event.artist.get_figure().canvas.draw()

        self.fig.canvas.mpl_connect("pick_event", onpick)

    def clear(self):
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

    def format_axes(self):
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))

        
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
        self.pushButtonPrevisualize.clicked.connect(self.previsualizeCleaning)
        self.pushButtonSelectPoints.clicked.connect(self.selectPoints)

        self.checkBoxChanges.clicked.connect(self.plotPrevisualizedVar)
        self.pushButtonResetVar.clicked.connect(self.resetCleanVar)
        self.pushButtonResetAll.clicked.connect(self.resetCleanAll)


        self.checkBoxChanges.setChecked(True)
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
        self.comboBoxRawVar.addItems(list(self.df_loaded.columns)[1:])
        self.varName = self.comboBoxRawVar.currentText
        self.comboBoxRawVar.currentIndexChanged.connect(self.plotPrevisualizedVar)

        self.cleanedVars = []

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


    def plotRawSQL(self):    
        
        # Load the table directly in a QSqlTableModel

        model = QSqlTableModel(None, self.rawCon) # Without parent but with connection
        model.setTable("Pressure") # Name of the table
        model.select() # "Upload" the table
        
        while model.canFetchMore():
            model.fetchMore()

        if model.rowCount() <= 0:
            return 
        
        times = [model.data(model.index(r,1)) for r in range(model.rowCount())]
        values = [model.data(model.index(r,1+2)) for r in range(model.rowCount())]
        
        self.mplRawPressureCurve = MplCanvasTimeScatter()
        self.mplRawPressureCurve.refresh(times, values)
        self.mplRawPressureCurve.click_connect()

        self.widgetRawData.addWidget(self.mplRawPressureCurve)

                
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
        "Refresh plot"
        if self.varName() in self.cleanedVars:
            self.pushButtonPrevisualize.setEnabled(False)
        else:
            self.pushButtonPrevisualize.setEnabled(True)
        try:
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
            

    def previsualizeCleaning(self):
        "Cleans data and shows a previsuaization"
        if self.radioButtonZScore.isChecked():
            self.df_cleaned = self.remove_outlier_z(self.df_cleaned,self.varName())
        elif self.radioButtonIQR.isChecked():
            self.df_cleaned = self.iqr(self.df_cleaned,self.varName())
        else:
            pass
        values = self.df_cleaned.apply(lambda x: np.nan if mdates.date2num(x['date']) in list(mdates.date2num(self.df_selected['date'])) else x[self.varName()],axis=1)
        self.df_cleaned.loc[:,self.varName()] = values

        self.cleanedVars.append(self.varName())

        self.plotPrevisualizedVar()

    def getDF(self):
        "Gets the unified pandas with charge_diff calculated and whitout tension voltage"
        df_ZH = self.load_pandas(self.rawCon, "SELECT date, t1, t2, t3, t4 FROM ZH", ["date", "t1", "t2", "t3", "t4"])
        convertDates(df_ZH)
        df_Pressure = self.load_pandas(self.rawCon, "SELECT date, tension, t_stream FROM Pressure", ["date", "tension", "t_stream"])
        convertDates(df_Pressure)
        df_Calibration = self.load_pandas(self.rawCon, "SELECT Var, Value FROM Calibration", ["Var", "Value"])


        intercept = float(df_Calibration.iloc[2][list(df_Calibration.columns)[-1]])
        dUdH = float(df_Calibration.iloc[3][list(df_Calibration.columns)[-1]])
        dUdT = float(df_Calibration.iloc[4][list(df_Calibration.columns)[-1]])

        df_Pressure["charge_diff"] = (df_Pressure["tension"]-df_Pressure["t_stream"]*dUdT-intercept)/dUdH
        df_Pressure.drop(labels="tension",axis=1,inplace=True)

        self.df_loaded = df_Pressure.join(df_ZH.set_index("date"), on="date")
        self.df_cleaned = self.df_loaded.copy().dropna()
        self.df_selected = pd.DataFrame(columns=["date","value"])
        # self.df_loaded= df_Pressure.merge(df_ZH, on="date")

        self.mplPrevisualizeCurve = MplCanvasTimeCompare()

    def selectPoints(self):
        dig = DialogCleanPoints()
        dig.plot(self.varName(), self.df_loaded, self.df_selected)
        res = dig.exec()
        if res == QtWidgets.QDialog.Accepted:
            self.df_selected = dig.mplSelectCurve.df_selected
        print(self.df_selected)
        self.previsualizeCleaning()

    def resetCleanVar(self):
        self.cleanedVars.remove(self.varName())
        self.df_cleaned[self.varName()] = self.df_loaded[self.varName()]
        self.df_selected = pd.DataFrame(columns=["date","value"])
        self.plotPrevisualizedVar()

    def resetCleanAll(self):
        self.cleanedVars = []
        self.df_selected = pd.DataFrame(columns=["date","value"])
        self.df_cleaned = self.df_loaded.copy().dropna()
        self.plotPrevisualizedVar()


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

    sys.exit(app.exec_())
    