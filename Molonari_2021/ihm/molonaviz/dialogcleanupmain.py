from binhex import openrsrc
from logging import exception
import sys, os

from pkg_resources import run_script
import numpy as np
import pandas as pd
from scipy import stats
# Import PyQt sub-modules
from PyQt5 import QtWidgets, QtCore, uic
# Import PyQt5.QtSql classes 
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
from usefulfonctions import date_to_mdates

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
from datetime import timedelta

from dialogcleanpoints import DialogCleanPoints
from dialogscript import DialogScript
from Database.mainDb import MainDb

# Load "UI" (user interface) XML file produced by QtDesigner
# and construct an object which inherits from the global parent class (PyQt5.QtWidgets.QDialog)
# See https://doc.qt.io/qtforpython-5/PySide2/QtUiTools/ls.loadUiType.html
# This function returns a pair of "types" : (generated_class, base_class) :
#  - generated_class: Ui_TemperatureViewer (contains all graphical controls/views defined with QtDesigner
#  - base_class: PyQt5.QtWidgets.QDialog (parent class of the UI)
From_DialogCleanUpMain= uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcleanupmain.ui"))


class MplCanvasTimeCompare(FigureCanvasQTAgg):
    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeCompare, self).__init__(self.fig)

    def refresh_compare(self, df_or, df_cleaned,id):
        """ Compare original data, semiprocessed data and cleaned data """
        suffix_or = "_or"
        varOr = df_or.dropna()[['date',id]]
        df_compare_or= df_or[["date",id]].merge(varOr,on=["date"],how="outer",suffixes=(None,suffix_or))  # Merge "outer" to get nan values if VarOr is smaller    
        df_compare_or['missing'] = df_compare_or[list(df_compare_or.columns)[-1]]

        df_compare_or.loc[np.isnan(df_compare_or['missing']),'missing'] = True # Gets a mask
        df_compare_or.loc[df_compare_or['missing'] != True, 'missing'] = False
        
        df_compare_or['date'] = mdates.date2num(df_compare_or['date']) # ALWAYS be sure to converte to mdates. Otherwise, plot may not work
        df_compare_or[df_compare_or['missing'] == True].plot.scatter(x='date',y=id,c = 'g',s = 3,ax = self.axes) # Plot the mask
        
        # Compare cleaned data 
        suffix_cl = '_cleaned'
        varCleaned = df_cleaned[["date",id]].dropna() 
        df_compare= varOr.merge(varCleaned,on=["date"],how="outer",suffixes=(None,suffix_cl))     #M Merge "outer"

        df_compare['outliers'] = df_compare[list(df_compare.columns)[-1]]
        mask = df_compare.apply(lambda x: True if x[id]!=x[id+suffix_cl] else False,axis=1) # Creates maks
        point_sizes = df_compare[mask].apply(lambda x: 3 if np.isnan(x[id+suffix_cl]) else 0.2, axis=1) # Deleted points are bigger than modified points by the filter
        if point_sizes.empty: 
            point_sizes = pd.Series([],dtype=np.float64) # Avoids an error when ploting
        
        df_compare['date'] = mdates.date2num(df_compare['date'])
        varCleaned['date'] = mdates.date2num(varCleaned['date'])
        varCleaned.plot(x='date',y=id,ax = self.axes)
        df_compare[mask].plot.scatter(x='date',y=id,c = '#FF6D6D',s =point_sizes,ax = self.axes)
        self.format_axes()
        self.fig.canvas.draw()

    def refresh(self,df_cleaned,id): # Plot without comparing. 
        """ id is the string of the name variable"""
        varCleaned = df_cleaned[["date",id]].dropna() # Get the var
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
               "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %I:%M:%S %p",
               "%Y:%m:%d %H:%M:%S", "%Y:%m:%d %I:%M:%S %p",
               "%m:%d:%Y %H:%M:%S", "%m:%d:%Y %I:%M:%S %p",None)
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


class DialogCleanupMain(QtWidgets.QDialog, From_DialogCleanUpMain[0]):
    """
    Dialog class that inherits from BOTH :
     - the QtDesigner generated_class: UI_TemperatureViewer 
     - the UI base_class (here QDialog)
    This offers the possibility to access directly the graphical controls variables (i.e. self.editFile)
    """
    def __init__(self,name,cleanupDir,study,con):
        """
        Constructor
        """
        # Call the constructor of parent classes (super)
        super(DialogCleanupMain, self).__init__()
        QtWidgets.QDialog.__init__(self)
        # Configure the initial values of graphical controls 
        # See https://doc.qt.io/qt-5/designer-using-a-ui-file-python.html
        self.setupUi(self)
        
        # Connect the buttons and checkbox
        self.pushButtonSelectPoints.clicked.connect(self.selectPoints)
        self.pushButtonEditCode.clicked.connect(self.editScript)
        self.pushButtonResetVar.clicked.connect(self.resetCleanVar)
        self.pushButtonResetAll.clicked.connect(self.resetCleanAll)

        self.checkBoxChanges.clicked.connect(self.plotPrevisualizedVar)
        self.checkBoxFilter.clicked.connect(self.triggerSetFilter)
        self.checkBoxFC.clicked.connect(self.fromFtoC)
        self.checkBoxCK.clicked.connect(self.fromCtoK)
        

        # connects the radio buttons
        self.buttonGroupMethod.setId(self.radioButtonZScore,1)
        self.buttonGroupMethod.setId(self.radioButtonIQR,2)
        self.buttonGroupMethod.setId(self.radioButtonNone,3)
        
        self.buttonGroupMethod.buttonClicked.connect(self.selectMethod)

        # Initializes radio and check buttons
        self.radioButtonNone.setChecked(True)
        self.checkBoxChanges.setChecked(True)
        self.checkBoxFilter.setChecked(False)
        self.checkBoxFC.setChecked(False)
        self.checkBoxCK.setChecked(False)
        # Initializes connection with database
        self.con = con
        self.mainDb = MainDb(self.con)
        self.name = name
        self.samplingPointDb = self.mainDb.samplingPointDb
        self.path_to_script = self.get_Script_Name()
        self.scriptDir = os.path.dirname(self.path_to_script)
        try:
            self.pointKey = self.samplingPointDb.getIdByname(self.name)
        except TypeError as e:
            displayCriticalMessage(f"{str(e)}", "Point not found in the database. Update the database to use this feature.")
            raise e
        else:
            # Create data models and associate to corresponding viewers
            self.cleanupDir = cleanupDir
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
        #Don't close the connection to the database as it is global.
        pass  
                    
    def load_pandas(self,db, statement, cols):    
        db.transaction()
        query = QSqlQuery(db)
        query.exec(statement)
        table = []
        while query.next():
            values = []
            for i in range(query.record().count()):
                values.append(query.value(i))
            table.append(values)
        df = pd.DataFrame(table)
        df.columns = cols
        db.commit()
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
        id = self.comboBoxRawVar.currentText()
        self.mplPrevisualizeCurve.clear()

        if self.checkBoxChanges.isChecked():
            self.mplPrevisualizeCurve.refresh_compare(self.df_loaded, self.df_cleaned, id)
        else:
            self.mplPrevisualizeCurve.refresh(self.df_cleaned, id)
        

        self.widgetRawData.addWidget(self.mplPrevisualizeCurve)

    def get_Script_Name(self):
        q = QSqlQuery(f'SELECT SamplingPoint.CleanupScript FROM SamplingPoint WHERE SamplingPoint.Name = "{self.name}"')
        q.exec()
        q.next()
        return q.value(0)
            
    def getScript(self):
        try:
            # with open('saved_text.txt', 'r') as f:
            #     sample_text = f.read()
            #     f.close()
            with open(self.path_to_script) as f:
                sample_text = f.read()
                f.close()
        except:
            #Once again,this is too permisive: what if no script was found?
            print("No saved script, show sample script")
            with open(os.path.join(os.path.dirname(self.path_to_script),"sample_text.txt")) as f:
                sample_text = f.read()
                f.close()
        # scriptpartiel = plainTextEdit.toPlainText()
        scriptindente = sample_text.replace("\n", "\n   ")
        script = "def fonction(self, df_ZH, df_Pressure, df_Calibration): \n   " + scriptindente + "\n" + "   return(df_loaded, df_cleaned, varList)"
        return(script)

    def cleanup(self, script, df_ZH, df_Pressure, df_Calibration):
        scriptPyPath = os.path.join(self.scriptDir,"script.py")
        sys.path.append(self.scriptDir) 

        with open(scriptPyPath, "w") as f:
            f.write(script)
            f.close()

        # There are different error in the script, sometimes it will cause the import step to fail, in this case we still have to remove the scripy.py file.
        try:
            from script import fonction
        except Exception as e:
            print(e)
            raise e
        finally:
            os.remove(scriptPyPath)
            del sys.modules["script"]

        try :
            self.df_loaded, self.df_cleaned, self.varList = fonction(self,df_ZH, df_Pressure, df_Calibration)

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
        
    def runScript(self, df_ZH, df_Pressure, df_Calibration,backupScript=None):
        df_ZH = df_ZH.copy()
        df_Pressure = df_Pressure.copy()
        df_Calibration = df_Calibration.copy()
        script = self.getScript()
        
        
        try :
            self.cleanup(script, df_ZH, df_Pressure, df_Calibration)
            
            
        except Exception as e :
            print(e, "==> Clean-up aborted")
            displayCriticalMessage("Error : Clean-up aborted", f'Clean-up was aborted due to the following error : \n"{str(e)}" ' )
            if backupScript:
                self.saveScript(backupScript)
            self.editScript()
            

    def editScript(self):
        dig = DialogScript(self.name, self.path_to_script)
        res = dig.exec()
        if res == QtWidgets.QDialog.Accepted:

            # Save the modified text
            try:
                backupScript = self.openScript()
                dig.updateScript()
                self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration, backupScript) # TODO bug when file fails to run the first time the window is open
                self.plotPrevisualizedVar()
                print("Script successfully updated")
            except Exception as e:
                print(e, "==> Clean-up aborted")
                displayCriticalMessage("Error: Clean-up aborted", f'Clean-up was aborted due to the following error : \n"{str(e)}" ')
                if backupScript:
                    self.saveScript(backupScript)
                self.editScript()
                
                
    
    # Define the selectMethod function and edit the sample_text.txt
    def openScript(self):
        
        try: 
            with open(self.path_to_script) as file:
            # with open('saved_text.txt', 'r') as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()
        except FileNotFoundError:
            # Try to open the base script
            with open(os.path.join(os.path.dirname(self.path_to_script),"sample_text.txt")) as file:
                # read a list of lines into data
                data = file.readlines()
                file.close()
        return data
    
    def saveScript(self, data):
        with open(self.path_to_script, 'w') as file:
            file.writelines( data )
            file.close()
    
    def parseKey(self,data,key):
        for i in range(len(data)):
            if data[i].find(key) != -1:
                line = i
        return line
    def selectMethod(self,object):
        id = self.buttonGroupMethod.id(object)
        varIndex = self.varList.index(self.varName())
        self.method_dic[self.varName()] = self.buttonGroupMethod.button(id)

        data = self.openScript()

        method_key = '# METHOD'
        methodsLine = self.parseKey(data,method_key)
        
            
        # now change the n-th line
        if id == 1:
            method = "remove_outlier_z"
        elif id == 2:
            method = "iqr"
        else:
            method = None
        
        if method:
            data[methodsLine+varIndex*2] = f'df_cleaned = self.{method}(df_cleaned,"{self.varName()}")\n'
        else:
            data[methodsLine+varIndex*2] = "\n"

        # write everything back
        self.saveScript(data)
        self.previsualizeCleaning()
        

    def triggerSetFilter(self):
        self.setFilter(self.varName())
    
    def setFilter(self,var):
        self.filter_dic[var] = self.checkBoxFilter.isChecked()
        data  = self.openScript()

        filter_key = '# SMOOTHING'
        filterLine = self.parseKey(data,filter_key)
        
        data[filterLine+1] = f'to_filter = {self.filter_dic}\n'

        self.saveScript(data)
        self.previsualizeCleaning()

    def fromFtoC(self):
        data = self.openScript()

        fToCKey = "# TEMPERATURE F TO C"
        fToCLine = self.parseKey(data,fToCKey)

        if self.checkBoxFC.isChecked():
            data[fToCLine+1] = 'df_ZH[["t1","t2","t3","t4"]] = df_ZH[["t1","t2","t3","t4"]].apply(lambda x: (x-32)/1.8, axis=1)\n'
            data[fToCLine+2] =  'df_Pressure[["t_stream"]] = df_Pressure[["t_stream"]].apply(lambda x: (x-32)/1.8, axis=1)\n' 
        else:
            data[fToCLine+1] = '\n'
            data[fToCLine+2] = '\n'
        
        self.saveScript(data)
        self.previsualizeCleaning()

    def fromCtoK(self):
        data = self.openScript()

        cToKKey = "# TEMPERATURE C TO K"
        cToKLine = self.parseKey(data,cToKKey)

        if self.checkBoxCK.isChecked():
            data[cToKLine+1] = 'df_cleaned[["t_stream","t1","t2","t3","t4"]] = df_cleaned[["t_stream","t1","t2","t3","t4"]].apply(lambda x: x+273.15, axis=1)\n'
        else:
            data[cToKLine+1] = '\n'

        self.saveScript(data)
        self.previsualizeCleaning()

    def previsualizeCleaning(self):
        "Cleans data and shows a previsuaization"
        self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration)

        # selected_df = pd.read_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))

        # for i in self.varList[1:]:
        #     df_var = selected_df[["date",i]].dropna()
        #     values = self.df_cleaned.apply(lambda x: np.nan if mdates.date2num(x['date']) in list(mdates.date2num(df_var['date'])) else x[i],axis=1)
        #     self.df_cleaned.loc[:,i] = values

        self.plotPrevisualizedVar()

    def getDF(self):
        def getPressureSensorByname(bd, name):
            bd.con.transaction()
            selectQuery = QSqlQuery(bd.con)
            selectQuery.prepare("SELECT PressureSensor FROM SamplingPoint where Name = :name")
            selectQuery.bindValue(":name", name)
            selectQuery.exec_()
            
            selectQuery.next()
            id = int(selectQuery.value(0))
            selectQuery.finish()
            bd.con.commit()
            return id

        "Gets the unified pandas with charge_diff calculated and whitout tension voltage"
        self.df_ZH = self.load_pandas(self.con, f'SELECT Date, Temp1, Temp2, Temp3, Temp4 FROM RawMeasuresTemp WHERE PointKey = {self.pointKey}', ["date", "t1", "t2", "t3", "t4"])
        convertDates(self.df_ZH)
        # Uncomment if original data is in Fahrenheit
        # self.df_ZH[["t1","t2","t3","t4"]] = self.df_ZH[["t1","t2","t3","t4"]].apply(lambda x: (x-32)/1.8, axis=1) 
        self.df_Pressure = self.load_pandas(self.con, f'SELECT Date, Tension, TempBed FROM RawMeasuresPress WHERE PointKey = {self.pointKey}', ["date", "tension", "t_stream"])
        convertDates(self.df_Pressure)
        # Uncomment if original data is in Fahrenheit
        # self.df_Pressure[["t_stream"]] = self.df_Pressure[["t_stream"]].apply(lambda x: (x-32)/1.8, axis=1) 
        idPressureSensor = getPressureSensorByname(self.samplingPointDb,self.name)
        # self.df_Calibration = self.load_pandas(self.con, "SELECT Var, Value FROM Calibration", ["Var", "Value"])
        self.df_Calibration = self.load_pandas(self.con, f'SELECT Name, Intercept, [Du/Dh], [Du/Dt] FROM PressureSensor WHERE id = {idPressureSensor}', ["Name", "Intercept", "dUdH", "dUdT"])
        
        self.mplPrevisualizeCurve = MplCanvasTimeCompare()
        self.toolBar = NavigationToolbar2QT(self.mplPrevisualizeCurve,self)
        self.widgetToolBar.addWidget(self.toolBar)

        ## CODE NOW IN THE SCRIPT
        # intercept = self.df_Calibration.loc[0,"Intercept"]
        # dUdH = self.df_Calibration.loc[0,"dUdH"]
        # dUdT = self.df_Calibration.loc[0,"dUdT"]

        # df_Pressure["charge_diff"] = (df_Pressure["tension"]-df_Pressure["t_stream"]*dUdT-intercept)/dUdH
        # df_Pressure.drop(labels="tension",axis=1,inplace=True)

        # self.df_loaded = df_Pressure.merge(df_ZH, how='outer', on="date").sort_values('date').reset_index().drop('index',axis=1)
        # self.varList = list(self.df_loaded.columns)
        # self.df_cleaned = self.df_loaded.copy().dropna()
        ## END OF SCRIPT CODE
        try:    
            self.runScript(self.df_ZH, self.df_Pressure, self.df_Calibration)
        except Exception as e:
            print(e)
            self.editScript()
        else:
            try:
                self.df_selected = pd.read_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))
            except FileNotFoundError:
                self.df_selected = pd.DataFrame(columns=self.varList)
                self.df_selected.to_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))


            

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
            self.df_selected.to_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))
            
        self.previsualizeCleaning()

    def resetCleanVar(self):
        # self.df_cleaned[self.varName()] = self.df_loaded[self.varName()]

        nan_values = np.empty((self.df_selected.shape[0],1))
        nan_values.fill(np.nan)
        self.df_selected[self.varName()] = nan_values
        self.df_selected.dropna(how="all",subset=self.varList[1:],inplace=True)
        self.df_selected.to_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))

        obj = self.buttonGroupMethod.button(3)
        self.selectMethod(obj)
        self.checkBoxFilter.setChecked(False)
        self.setFilter(self.varName())

    def resetCleanAll(self):
        self.df_selected = pd.DataFrame(columns=self.varList)
        self.df_selected.to_csv(os.path.join(self.scriptDir,f'selected_points_{self.name}.csv'))
        # self.df_cleaned = self.df_loaded.copy().dropna() # TODO Is it ok the dropna()? 
        self.method_dic = dict.fromkeys(self.varList[1:],self.buttonGroupMethod.button(3))
        try:
            os.remove(os.path.join(self.path_to_script))
        except FileNotFoundError:
            pass
        self.filter_dic = dict.fromkeys(self.varList[1:],False)
        self.checkBoxFilter.setChecked(False)
        self.checkBoxFC.setChecked(False)
        self.checkBoxCK.setChecked(False)
        self.previsualizeCleaning()
    
    


# if __name__ == '__main__':
#     """
#     Main function of the script:
#     - Create the QApplication object
#     - Create the TemperatureViewer dialog and show it
#     - Execute the infinite event loop and wait for interaction or exit
#     """
#     app = QtWidgets.QApplication(sys.argv)

#     mainWin = DialogCleanupMain()
#     mainWin.show()

#     app.exec_()
#     try:
#         os.remove("saved_text.txt")
#     except FileNotFoundError:
#         pass
#     try:
#         os.remove("selected_points.csv")
#     except FileNotFoundError:
#         pass
    # lower_limit = max(mainWin.df_cleaned[["t_stream"]].first_valid_index(),mainWin.df_cleaned[["charge_diff"]].first_valid_index(),mainWin.df_cleaned[["t4"]].first_valid_index())
    # upper_limit = min(mainWin.df_cleaned[["t_stream"]].last_valid_index(),mainWin.df_cleaned[["charge_diff"]].last_valid_index(),mainWin.df_cleaned[["t4"]].last_valid_index())
    # print(mainWin.df_cleaned)
    # print(mainWin.df_cleaned.loc[lower_limit:upper_limit,:])
    # cleaned = mainWin.df_cleaned.loc[lower_limit:upper_limit,:]
    # zh = cleaned[["date","t1","t2","t3","t4"]]
    # zh.to_csv("processed_temperatures_P51-1.csv")
    # press = cleaned[["date","charge_diff","t_stream"]]
    # press.to_csv("processed_pressures_P51-1.csv")