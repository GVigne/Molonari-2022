import sys, os
import numpy as np
import pandas as pd
# Import PyQt sub-modules
from PyQt5 import QtWidgets, uic
# Import PyQt5.QtSql classes 
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

# Load "UI" (user interface) XML file produced by QtDesigner
# and construct an object which inherits from the global parent class (PyQt5.QtWidgets.QDialog)
# See https://doc.qt.io/qtforpython-5/PySide2/QtUiTools/ls.loadUiType.html
# This function returns a pair of "types" : (generated_class, base_class) :
#  - generated_class: Ui_TemperatureViewer (contains all graphical controls/views defined with QtDesigner
#  - base_class: PyQt5.QtWidgets.QDialog (parent class of the UI)
From_tp_ihm_sql = uic.loadUiType(os.path.join(os.path.dirname(__file__),"tp_ihm_sql.ui")) #### Do not forget to load the appropriate UI file


class LoadingError(Exception):
    """
    Override Exception base class for particular case of a file loading error
    """
    def __init__(self, object: str, reason: str):
        self.object = object
        self.reason = reason

    # Override __str__ operator for string representation
    # See https://www.pythontutorial.net/python-oop/python-__str__
    ### TODO
    def __str__(self):
        return f"Error : Couldn't load {self.object}\n{self.reason}"
    ### End TODO
    
def displayCriticalMessage(mainMessage: str, infoMessage: str=''):
    """
    Display a "critical" popup dialog with a main message and a secondary detailed message
    """
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    # https://doc.qt.io/qt-5/qmessagebox.html#details
    ### TODO
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.exec() 
    ### End TODO


def loadCSV(path: str):
    """
    Open and read the CSV file. Raise a LoadingError exception if :
     - less than 6 columns are read
     - more than 10 columns are read
    """
    df = pd.read_csv(path, skiprows=1) #### TODO : Fix the error when reading HOBO file
    
    # Check the number of columns
    if df.shape[1] < 6 or df.shape[1] > 10 :  # Idx + Date + Temp x4
        # Try with another separator
        df = pd.read_csv(path, sep='\t', skiprows=1) #### TODO : Fix the error when reading HOBO file
        
    # Re-Check the number of columns and raise Loading Error exception if error
    # https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python
    ### TODO
    if df.shape[1] < 6 or df.shape[1] > 10 :  # Idx + Date + Temp x4
        raise LoadingError(path, "Wrong number of columns in temperature file. Is it a CSV file?")      
    ### End TODO

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
    ### TODO
    #
    # WARNING: To work in place, you must not replace df using "df = df.dropna"
    #          Otherwise, you must return df from the function and store the result in the call instruction
    #
    # Rename the 6 first columns
    for i in range(0, len(all_cols)) :
        df.columns.values[i] = all_cols[i]
    # Remove lines having at least one missing value [among temperatures!]
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html
    df.dropna(subset=val_cols,inplace=True)
    # Remove last columns [that contains missing values]
    df.dropna(axis=1,inplace=True)
    # Remove first column
    df.drop(["Idx"],axis=1,inplace=True)
    ### End TODO

def convertDates(df: pd.DataFrame):
    """
    Convert dates from a list of strings by testing several different input formats
    Try all date formats already encountered in HOBO files
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
    # Try different date format
    for f in formats:
        try:
            # Convert strings to datetime objects
            new_times = pd.to_datetime(times, format=f)
            # Check that new_times are well converted (ordered). If not Raise a ValueError.
            ### TODO
            # Convert datetime series to numpy array of integers (timestamps)
            new_ts = new_times.values.astype(np.int64)
            # If times are not ordered, this is not the appropriate format
            test = np.sort(new_ts) - new_ts
            if np.sum(abs(test)) != 0 :
                raise ValueError()
            ### End TODO
            # Else, the conversion is a success
            df[df.columns[0]] = new_times
            return
        
        except ValueError:
            continue
    
    # None of the known format are valid
    raise ValueError("Cannot convert dates: No known formats match your data!")


class TemperatureViewer(From_tp_ihm_sql[0], From_tp_ihm_sql[1]):
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
        
        # Add a "Browse button" in the GUI and connect it to the method 'browseFile'
        ### TODO
        self.pushButtonBrowse.clicked.connect(self.browseFile)
        ### End TODO
        
        # Remove existing SQL database file (if so)
        self.sqlfile = "molonari_temp.sqlite"
        if os.path.exists(self.sqlfile):
            os.remove(self.sqlfile)

        # Connect to the SQL database and display a critical message in case of failure
        ### TODO
        self.con = QSqlDatabase.addDatabase("QSQLITE") # Store the connection in class member
        self.con.setDatabaseName(self.sqlfile) # Connect to the SQL file
        if not self.con.open(): # Open the database
            displayCriticalMessage(f"{str(self.con.lastError().databaseText())}", "Cannot open SQL database")
        ### End TODO


    def __del__(self):
        """
        Destructor
        """
        # Close the SQL connection
        ### TODO
        self.con.close()
        ### End TODO


    def readCSV(self):
        """
        Read the provided CSV file and load it into a Pandas dataframe
        """
        # Retrieve the CSV file path from lineEditTempFile
        ### TODO
        trawfile = self.lineEditTempFile.text()
        ### End TODO
        if trawfile:
            try :
                # Load the CSV file
                dftemp = loadCSV(trawfile)
                
                # Cleanup the dataframe
                cleanupTemp(dftemp)
                
                # Convert the dates
                convertDates(dftemp)
                
                return dftemp

            except Exception as e :
                displayCriticalMessage(f"{str(e)}", "Please choose a different file")
    
        # If failure, return an empty dataframe
        return pd.DataFrame()
    
    
    def writeSQL(self, df: pd.DataFrame):
        """
        Write the given Pandas dataframe into the SQL database
        """
        # Remove the previous measures table (if so)
        dropTableQuery = QSqlQuery() #### Current opened connection is not mandatory
        ### TODO
        dropTableQuery.exec(
            """       
            DROP TABLE measures
            """
        )
        ### End TODO
        dropTableQuery.finish()
        
        # Create the table for storing the temperature measures (id, date, temp*4)
        ### TODO
        createTableQuery = QSqlQuery(self.con) #### But it's better to indicate the current connection in query constructors
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
        createTableQuery.finish() #### Do not forget to finish your queries (close the transaction and free memory)
        ### End TODO

        # Construct the dynamic insert SQL request and execute it
        ### TODO
        
        # For large dataset, initialize a transaction to speedup the insertion
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
        for ind in df.index:
            insertDataQuery.addBindValue(str(df['Date'][ind]))  #### Convert to standard python type (String)
            insertDataQuery.addBindValue(float(df['Temp1'][ind]))
            insertDataQuery.addBindValue(float(df['Temp2'][ind]))
            insertDataQuery.addBindValue(float(df['Temp3'][ind]))
            insertDataQuery.addBindValue(float(df['Temp4'][ind]))
            insertDataQuery.exec_()
        insertDataQuery.finish()

        # Commit the transaction
        self.con.commit()
        
        ### End TODO


    def readSQL(self):
        """
        Read the SQL database and display measures
        """
        print("Tables in the SQL Database:", self.con.tables())

        # Read the database and print its content using SELECT
        selectDataQuery = QSqlQuery(self.con)
        ### TODO
        selectDataQuery.exec("SELECT date, t1, t2, t3, t4 FROM measures")
        date, t1, t2, t3, t4 = range(5)
        while selectDataQuery.next() :
            print("  ", selectDataQuery.value(date),
                        selectDataQuery.value(t1),
                        selectDataQuery.value(t2),
                        selectDataQuery.value(t3),
                        selectDataQuery.value(t4))
        ### End TODO
        selectDataQuery.finish()
        
        # Re-Load the table directly in a QSqlTableModel
        ### TODO
        self.model = QSqlTableModel(self, self.con)
        self.model.setTable("measures") 
        self.model.select()
        ### End TODO
        
        # Set the model to the GUI table view
        ### TODO
        self.tableView.reset()
        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        ### End TODO
        
        # Prevent from editing the table
        ### TODO
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers);
        ### End TODO

        
    def browseFile(self):
        """
        Display an "Open file dialog" when the user click on the 'Browse' button then
        - Store the selected CSV file path in the LineEdit (temperature measures)
        - Load the CSV file into a Pandas dataframe
        - Write the Pandas dataframe into a SQL database
        - Reload the SQL database into a model and display it in the table view
        """
        # Open a "File Dialog" window and retrieve the path
        ### TODO
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Get Temperature Measures File")[0]
        ### End TODO
        
        if filePath:
            # Update the lineEditTempFile
            ### TODO
            self.lineEditTempFile.setText(filePath)
            ### End TODO
        
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
    
