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
#  - generated_class: Ui_TemperatureViewer (contains all graphical controls/views defined with QtDesigner)
#  - base_class: PyQt5.QtWidgets.QDialog (parent class of the UI)
From_sqlgridview = uic.loadUiType(os.path.join(os.path.dirname(__file__),"model_view_sql.ui"))

# Inherits from QSqlQueryModel (assume that Date/Time column is the 2nd one - ID is the first)
class TimeCurveModel(QSqlQueryModel): # TODO : add here indices for columns to be displayed
    
    # Create a user-defined signal to be emitted each time select method is called
    # Do not put that in the constructor (otherwise, signal doesn't work)
    tableFilled = QtCore.Signal()
    
    def __init__(self, parent, database, tableName):
        # Call parent constructor
        super(TimeCurveModel, self).__init__(parent)
        
        # Store attributes
        self.database = database
        self.tableName = tableName
        self.queryStr = f"SELECT * from {tableName}"
        
    # Override select method to emit the tableFilled signal
    def select(self):
        # Clear the model
        self.clear()

        # Execute the query
        self.setQuery(self.queryStr, self.database)
                
        #https://forum.qt.io/topic/108841/editing-data-in-table-view-row-grater-than-256-qsqltablemodel
        while self.canFetchMore() :
            self.fetchMore()

        # Emit the signal
        self.tableFilled.emit()

    # Clear the model
    def clear(self):
        # Call parent select method
        super(TimeCurveModel, self).clear()
        
        # Emit the signal
        self.tableFilled.emit()
        
        
# Inherits from FigureCanvasQTAgg
class MplCanvasTimeCurve(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111) # Single plot
        super(MplCanvasTimeCurve, self).__init__(self.fig)
        
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))


    # Set the model and connect its tableFilled signal to refresh slot
    def setModel(self, model):
        self.model = model
        model.tableFilled.connect(self.refresh)


    # Display the variable (3rd column) as a function of time and redraw the view
    # TODO : display several columns according indices provided in the constructor
    def refresh(self):
        
        #https://stackoverflow.com/questions/24245245/pyqt-qstandarditemmodel-how-to-get-a-row-as-a-list
        # Extract the values from the model
        times = [self.model.data(self.model.index(r,1)) for r in range(self.model.rowCount())]
        temperatures = [self.model.data(self.model.index(r,2)) for r in range(self.model.rowCount())]
        
        # Clear, display and refresh the plot
        self.axes.clear()
        self.axes.plot(mdates.date2num(times), temperatures)
        self.fig.canvas.draw()


        
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
        
        # Connect the "Browse button" 'pushButtonBrowseTemp' to the method 'browseFileTemp*'
        self.pushButtonBrowseTemp.clicked.connect(self.browseFileTemp)
        
        # Create the plot view
        self.mplTempCurve = MplCanvasTimeCurve()
        self.tabPlot.layout().addWidget(self.mplTempCurve)

        # Remove existing SQL database file (if so)
        self.sql = "molonari_temp.sqlite"
        if os.path.exists(self.sql):
            os.remove(self.sql)

        # Connect to the SQL database and display a critical message in case of failure
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sql)
        if not self.con.open():
            displayCriticalMessage(f"{str(self.con.lastError().databaseText())}", "Cannot open SQL database")

        # Create data model
        self.modelTemp = TimeCurveModel(self, self.con, "measures")
        
        # Set the model to observer views
        self.tableView.setModel(self.modelTemp)
        self.mplTempCurve.setModel(self.modelTemp)

        # Prevent the table from edition
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Create a timer for asynchronous launch of refresh
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.doRefresh)
        
        # TODO : to be removed
        self.lineEditTempFile.setText(os.path.join(os.path.dirname(__file__),"processed_temperatures_34.csv"))
        self.timer.start(200) # ms
        
    def __del__(self):
        """
        Destructor
        """
        # Close the SQL connection
        self.con.close()


    def readCSV(self):
        """
        Read the provided CSV files (cleaned (processed) temperatures)
        and load it into a Pandas dataframe
        """
        # Retrieve the CSV file paths from lineEditTempFile
        tempfile = self.lineEditTempFile.text()
        if tempfile:
           
            try :
                # Load the CSV file
                dftemp = loadCSV(tempfile)
                
                # Convert the dates
                convertDates(dftemp)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different temperatures file")
                return pd.DataFrame()
            
        return dftemp
    
    
    def writeSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        
        # Remove the previous measures table
        
        self.con.transaction()
        dropTableQuery = QSqlQuery(self.con)
        dropTableQuery.exec(
            """       
            DROP TABLE measures
            """
        )
        dropTableQuery.finish()
        self.con.commit()

        # Create the table for storing the temperature cleaned measures (id, date, temp*4)
        
        self.con.transaction()
        createTableQuery = QSqlQuery(self.con)
        createTableQuery.exec(
            """
            CREATE TABLE measures (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                date DATETIME NOT NULL,
                t1 FLOAT NOT NULL,
                t2 FLOAT NOT NULL,
                t3 FLOAT NOT NULL,
                t4 FLOAT NOT NULL
            )
            """
        )
        createTableQuery.finish()
        self.con.commit()
        
        # Construct the dynamic insert SQL request and execute it
        
        self.con.transaction()
        insertDataQuery = QSqlQuery(self.con)
        insertDataQuery.prepare(
            """
            INSERT INTO measures (
                date,
                t1,
                t2,
                t3,
                t4
            )
            VALUES (?, ?, ?, ?, ?)
            """
        )
        date, t1, t2, t3, t4 = range(5)
        for ind in df.index:
            insertDataQuery.addBindValue(str(df.iloc[ind,date]))  #### Convert to standard python type (String)
            insertDataQuery.addBindValue(float(df.iloc[ind,t1]))
            insertDataQuery.addBindValue(float(df.iloc[ind,t2]))
            insertDataQuery.addBindValue(float(df.iloc[ind,t3]))
            insertDataQuery.addBindValue(float(df.iloc[ind,t4]))
            insertDataQuery.exec()
        insertDataQuery.finish()
        self.con.commit()

        

    def readSQL(self):
        """
        Read the SQL database and display measures
        """
        print("Tables in the SQL Database:", self.con.tables())
        
        # Reset and update temperature table model (and automatically update views)
        self.modelTemp.select()
        print("Rows in the measures table:", self.modelTemp.rowCount())
        print("Columns in the measures table:", self.modelTemp.columnCount())

                
    def browseFileTemp(self):
        """
        Display an "Open file dialog" when the user click on the 'Browse' button then
        store the selected CSV file path in the LineEdit (processed temperature)
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Processed Temperature File")[0]
        if filePath:
            self.lineEditTempFile.setText(filePath)
            
            # Update status message and trigger a timer 
            self.timer.start(200) # ms

        
    def doRefresh(self):
        """
        - Load the CSV files into Pandas dataframes
        - Write the dataframes into a SQL database
        - Reload the SQL database into a model (views are automatically notified)
        """
        self.timer.stop()
        try:
            # Read the CSV file
            dftemp = self.readCSV()
            
            # Dump the measures to SQL database
            self.writeSQL(dftemp)
            
            # Read the SQL and update the table/image
            self.readSQL()
            
        except Exception as e:
            displayCriticalMessage("Error", f"{str(e)}")


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
    