import sys, os
import numpy as np
import pandas as pd
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

# Load "UI" (user interface) XML file produced by QtDesigner
# and construct an object which inherits from the global parent class (PyQt5.QtWidgets.QDialog)
# See https://doc.qt.io/qtforpython-5/PySide2/QtUiTools/ls.loadUiType.html
# This function returns a pair of "types" : (generated_class, base_class) :
#  - generated_class: Ui_TemperatureViewer (contains all graphical controls/views defined with QtDesigner
#  - base_class: PyQt5.QtWidgets.QDialog (parent class of the UI)
From_sqlgridview = uic.loadUiType(os.path.join(os.path.dirname(__file__),"sqlgridview.ui"))


class MplCanvasTimeCurve(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeCurve, self).__init__(self.fig)
        
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))

    def refresh(self, times, values):
        # TODO : Still string to date conversion needed!
        self.axes.plot(mdates.date2num(times), values)

class MplCanvasTimeScatter(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeScatter, self).__init__(self.fig)
        
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))
        self.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.setFocus()

    def refresh(self, times, values):
        # TODO : Still string to date conversion needed!
        self.axes.plot(mdates.date2num(times), values,'.',picker=5)
    
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
            datax = np.delete(datax,ind)
            datay = np.delete(datay,ind)
            event.artist.get_figure().clear()
            event.artist.get_figure().gca().plot(datax,datay,'.',picker=5)
            # event.artist.get_figure().gca().plot(x,y,'.',color="red")  
            event.artist.get_figure().canvas.draw()

        self.fig.canvas.mpl_connect("pick_event", onpick)

class MplCanvaTimeDepthImage(FigureCanvasQTAgg):
    
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvaTimeDepthImage, self).__init__(self.fig)
        
        # TODO : test this
        self.fig.tight_layout(h_pad=2, pad=2)
        
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))

    def refresh(self, times, depths, values):
        # TODO : Still string to date conversion needed!
        self.x = mdates.date2num(times)
        
        image = self.axes.imshow(values, cmap=cm.Spectral_r, aspect="auto", extent=[self.x[0], self.x[-1], depths[-1], depths[0]])

        
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
        
        # Connect the "Browse button" 'pushButtonBrowseTemp' to the method 'browseFile*'
        self.pushButtonBrowseTemp.clicked.connect(self.browseFileTemp)
        self.pushButtonBrowseDepth.clicked.connect(self.browseFileDepth)
        self.pushButtonRefresh.clicked.connect(self.refresh)

        self.pushButtonBrowseRawZH.clicked.connect(self.browseFileRawZH)
        self.pushButtonBrowseRauPressure.clicked.connect(self.browseFileRawPressure)
        
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
        self.modelDepth = QSqlQueryModel(self)
        self.modelTemp = QSqlTableModel(self, self.con)
        self.comboBoxDepth.setModel(self.modelDepth)
        self.tableView.setModel(self.modelTemp)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Create a timer for asynchronous launch of refresh
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.doRefresh)
        
        # TODO : to be removed
        # self.lineEditDepthFile.setText("/home/fors/Projets/molonari/main/studies/study_2022/Point034/results/direct_model_results/depths.csv")
        # self.lineEditTempFile.setText("/home/fors/Projets/molonari/main/studies/study_2022/Point034/results/direct_model_results/solved_temperatures.csv")
        # self.refreshImage()
        # self.refreshCurve()
        
        
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
    def readSQL(self):
        """
        Read the SQL database and display measures
        """
        print("Tables in the SQL Database:", self.con.tables())

        #selectDataQuery = QSqlQuery(self.con)
        #selectDataQuery.exec("SELECT depth FROM solved_depth")
        #print("Rows in the solved_depth table:", selectDataQuery.size()) # TODO : why -1 ??
        #selectDataQuery.finish()
        
        # Update depths combo box
        self.modelDepth.setQuery("SELECT depth FROM solved_depth", self.con) 
        print("Rows in the solved_depth table:", self.modelDepth.rowCount())
        
        # Update temperature table
        self.modelTemp.setTable("solved_temp") 
        self.modelTemp.select()
        print("Rows in the solved_temp table:", self.modelTemp.rowCount())
        print("Columns in the solved_temp table:", self.modelTemp.columnCount())

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
            # self.plotRawSQL()

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
            self.plotRawSQL()

    def refresh(self):
        """
        Update status message and trigger a timer
        This permits to display the status message 
        """
        self.labelStatus.setText("Please wait while loading your files...")
        self.timer.start(200) # ms
        
    def doRefresh(self):
        """
        - Load the CSV files into Pandas dataframes
        - Write the dataframes into a SQL database
        - Reload the SQL database into a model and display it as an image and a curve
        """
        self.timer.stop()
        try:
            # Read the CSV file
            dfdepth, df = self.readCSV()
            
            # Dump the measures to SQL database
            self.writeSQL(dfdepth, df)
            
            # Read the SQL and update the table/image
            self.readSQL()
            
            # Refresh the plots
            self.refreshImage()
            self.refreshCurve()
            
        except Exception as e:
            displayCriticalMessage("Error", f"{str(e)}")
            
        self.labelStatus.setText("")


    def refreshImage(self):
        """
        Display the image according
        """
        
        # If not ready, return
        if self.modelTemp.rowCount() <= 0:
            return 
        
        # https://stackoverflow.com/questions/24245245/pyqt-qstandarditemmodel-how-to-get-a-row-as-a-list
        # TODO : how to guarantee that dates in the model are stored as datetime (and not strings)?
        times = [self.modelTemp.data(self.modelTemp.index(r,1)) for r in range(self.modelTemp.rowCount())]
        depths = [self.modelDepth.data(self.modelDepth.index(r,0)) for r in range(self.modelDepth.rowCount())]
        temperatures = [[self.modelTemp.data(self.modelTemp.index(r,c+2)) for r in range(self.modelTemp.rowCount())] for c in range(0, self.ndepth)]

        self.mplTempImage = MplCanvaTimeDepthImage()
        self.mplTempImage.refresh(times, depths, temperatures)
        self.widgetImage.layout().addWidget(self.mplTempImage)
        
        
    def refreshCurve(self):
        """
        Display the curve according the selected depth in the combo box
        """
        
        # If not ready, return
        if self.modelTemp.rowCount() <= 0:
            return 
        
        # Retrieve the current combo box index
        id = self.comboBoxDepth.currentIndex()
        
        #https://stackoverflow.com/questions/24245245/pyqt-qstandarditemmodel-how-to-get-a-row-as-a-list
        # TODO : how to guarantee that dates in the model are stored as datetime (and not strings)?
        times = [self.modelTemp.data(self.modelTemp.index(r,1)) for r in range(self.modelTemp.rowCount())]
        temperatures = [self.modelTemp.data(self.modelTemp.index(r,id+2)) for r in range(self.modelTemp.rowCount())]

        self.mplTempCurve = MplCanvasTimeCurve()
        self.mplTempCurve.refresh(times, temperatures)
        self.widgetCurve.layout().addWidget(self.mplTempCurve)
        


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
    