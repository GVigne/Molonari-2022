import sys, os
import numpy as np
import pandas as pd
# Import PyQt sub-modules
from PyQt5 import QtWidgets, QtCore, uic
# Import PyQt5.QtSql classes 
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

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
From_tp_ihm_sql2 = uic.loadUiType(os.path.join(os.path.dirname(__file__),"tp_ihm_sql2.ui"))


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
    Open and read the CSV file. Raise a LoadingError exception if :
     - less than 6 columns are read
     - more than 10 columns are read
    """
    df = pd.read_csv(path, skiprows=1)
    #df = pd.read_csv(trawfile) #### To be fixed
    # Check the number of columns
    if df.shape[1] < 6 or df.shape[1] > 10 :  # Idx + Date + Temp x4
        # Try with another separator
        df = pd.read_csv(path, sep='\t', skiprows=1)
    # Re-Check the number of columns
    if df.shape[1] < 6 or df.shape[1] > 10 :  # Idx + Date + Temp x4
        raise LoadingError(path, "Wrong number of columns in temperature file. Is it a CSV file?")
    return df


def cleanupTemp(df: pd.DataFrame):
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


class TemperatureViewer(From_tp_ihm_sql2[0], From_tp_ihm_sql2[1]):
    """
    Dialog class that inherits from BOTH :
     - the QtDesigner generated_class: UI_TemeperatureViewer 
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
        
        # Connect the "Browse button" 'pushButtonBrowseTemp' to the method 'browseFile'
        self.pushButtonBrowseCleanTemp.clicked.connect(self.browseFile)
        
        # Remove existing SQL database file (if so)
        self.sql = "molonari_temppress.sqlite"
        if os.path.exists(self.sql):
            os.remove(self.sql)

        # Connect to the SQL database and display a critical message in case of failure
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName(self.sql)
        if not self.con.open():
            displayCriticalMessage(f"{str(self.con.lastError().databaseText())}", "Cannot open SQL database")

        # Create data models and associate to corresponding viewers
        self.modelDepth = QSqlTableModel(self, self.con)
        self.modelTemp = QSqlTableModel(self, self.con)
        self.tableViewDataArray.setModel(self.modelTemp)
        self.tableViewDataArray.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers);

        #Refresh button allows arrays and plots to appear
        self.pushButtonRefresh.clicked.connect(self.doRefresh)

        self.lineEditCleanTempFile.setText("C:/Users/benja/Documents/MOLONARI/Molonari-2022/Molonari_2021/studies/study_2022/Point034/processed_data/processed_temperatures.csv")
        self.lineEditCleanPressFile.setText("C:/Users/benja/Documents/MOLONARI/Molonari-2022/Molonari_2021/studies/study_2022/Point034/processed_data/processed_pressure.csv")
        self.lineEditRawTempFile.setText("C:/Users/benja/Documents/MOLONARI/Molonari-2022/Molonari_2021/studies/study_2022/Point034/raw_data/raw_temperatures.csv")
        self.lineEditRawPressFile.setText("C:/Users/benja/Documents/MOLONARI/Molonari-2022/Molonari_2021/studies/study_2022/Point034/raw_data/raw_pressure.csv")


    def __del__(self):
        """
        Destructor
        """
        # Close the SQL connection
        self.con.close()

    def readCSV(self):
        """
        Read the provided CSV files (depths values and gridded temperatures)
        and load it into a Pandas dataframes
        """
        # Retrieve the CSV file paths from lineEditDepthFile and lineEditTempFile
        cleantempfile = self.lineEditCleanTempFile.text()
        cleanpressfile = self.lineEditCleanPressFile.text()
        rawtempfile = self.lineEditRawTempFile.text()
        rawpressfile = self.lineEditRawPressFile.text()
        if cleantempfile and cleanpressfile:
            try :
                # Load the CSV file
                dfcleantemp = loadCSV(cleantempfile)
                # Convert the dates
                convertDates(dfcleantemp)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different clean temp file")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            try :
                dfcleanpress = loadCSV(cleanpressfile)
                convertDates(dfcleanpress)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different clean press file")
                return pd.DataFrame(), pd.DataFrame()
            
            try :
                dfrawtemp = loadCSV(rawtempfile)
                convertDates(dfrawtemp)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different raw temp file")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            try :
                dfrawpress = loadCSV(rawpressfile)
                convertDates(dfrawpress)
                
            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different raw press file")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
        return dfcleantemp, dfcleanpress, dfrawtemp, dfrawpress
    
    
    def writeSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Remove the previous measures table
        dropTableQuery = QSqlQuery(self.con)
        dropTableQuery.exec(
            """       
            DROP TABLE measures
            """
        )
        dropTableQuery.finish()
        
        # Create the table for storing the temperature measures (id, date, temp*4)
        createTableQuery = QSqlQuery(self.con)
        createTableQuery.exec(
            """
            CREATE TABLE measures (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                date TIMESTAMP NOT NULL,
                t1 FLOAT NOT NULL,
                t2 FLOAT NOT NULL,
                t3 FLOAT NOT NULL,
                t4 FLOAT NOT NULL
            )
            """
        )
        createTableQuery.finish()

        # Construct the dynamic insert SQL request
        insertDataQuery = QSqlQuery(self.con)
        insertDataQuery.prepare(
            """
            INSERT INTO measures (
                date,
                t1,
                t2,
                t3,
                t4,

            )
            VALUES (?, ?, ?, ?, ?)
            """
        )
        for ind in df.index:
            insertDataQuery.addBindValue(str(df['Date'][ind]))
            insertDataQuery.addBindValue(str(df['Temp1'][ind]))
            insertDataQuery.addBindValue(str(df['Temp2'][ind]))
            insertDataQuery.addBindValue(str(df['Temp3'][ind]))
            insertDataQuery.addBindValue(str(df['Temp4'][ind]))
            insertDataQuery.exec()
        insertDataQuery.finish()


    def readSQL(self):
        """
        Read the SQL database and display measures
        """
        print("Tables in the SQL Database:", self.con.tables())

        # Read the database and print its content
        selectDataQuery = QSqlQuery(self.con)
        selectDataQuery.exec("SELECT date, t1, t2, t3, t4 FROM measures")
        date, t1, t2, t3, t4 = range(5)
        while selectDataQuery.next() :
            print("  ", selectDataQuery.value(date),
                        selectDataQuery.value(t1),
                        selectDataQuery.value(t2),
                        selectDataQuery.value(t3),
                        selectDataQuery.value(t4))
        selectDataQuery.finish()
        
        # Load the table directly in a QSqlTableModel
        model = QSqlTableModel()
        model.setTable("measures") 
        model.select()
        # Set the model to the GUI table view
        self.tableViewDataArray.setModel(model)
        # Prevent from editing the table
        self.tableViewDataArray.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers);
        
    def doRefresh(self):
        """
        - Load the CSV files into Pandas dataframes
        - Write the dataframes into a SQL database
        - Reload the SQL database into a model and display it as an image and a curve
        """
        try:
            # Read the CSV file
            dfdepth, df = self.readCSV()
            
            # Dump the measures to SQL database
            self.writeSQL(dfdepth, df)
            
            # Read the SQL and update the table/image
            self.readSQL()
            
            # Refresh the plots
            self.refreshCurve()
            
        except Exception as e:
            displayCriticalMessage("Error", f"{str(e)}")

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

    def browseFile(self):
        """
        Display an "Open file dialog" when the user click on the 'Browse' button then
        - Store the selected CSV file path in the LineEdit (temperature measures)
        - Load the CSV file into a Pandas dataframe
        - Write the Pandas dataframe into a SQL database
        - Reload the SQL database into a model and display it in the table view
        """
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Temperature Measures File")[0]
        if filePath:
            self.lineEditCleanTempFile.setText(filePath)
            
            # Read the CSV file
            df = self.readCSV()
            
            # Dump the measures to SQL database
            self.writeSQL(df)
            
            # Read the SQL and update the views
            self.readSQL()
    


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
    