from csv import excel_tab
import unicodedata
import string
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets
from datetime import datetime
from traitlets.config.application import catch_config_error
from errors import *
import matplotlib.dates as mdates
import os, glob
from sensors import Shaft
from sensors import Thermometer
from sensors import PressureSensor

def clean_filename(filename: str, char_limit: int= 255, replace=' '):

    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in valid_filename_chars)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    
    return cleaned_filename[:char_limit] 


def celsiusToKelvin(df: pd.DataFrame):

    """
    Inplace
    """
    
    columnsNames = list(df.head(0))

    temps = [columnsNames[i] for i in range(1,5)]
    for temp in temps:
        df[temp] = df[temp]+273.15
    
    # change columns names
    df.columns = ['Date Heure, GMT+01:00', 'Température 1 (K)', 'Température 2 (K)', 'Température 3 (K)', 'Température 4 (K)']
    
def SQl_to_pandas(date):
    format =("%Y:%m:%d:%H:%M:%S","%Y:%m:%d:%H:%M")
    for f in format:
        try:
            return pd.to_datetime(date, format=f)
        except Exception:
            continue

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

def readCSVWithDates(path: str, skiprows=0, sep=','):
    try:
        df = pd.read_csv(path, skiprows=skiprows, sep=sep)
        # TODO : this takes toooooo long each time we read a CSV file !!!
        convertDates(df)
    except Exception as e :
        raise LoadingError(f"{str(e)}") 
        return pd.DataFrame()
    return df

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


def displayInfoMessage(mainMessage: str, infoMessage: str=''):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.exec_() 

def displayInfoMessage(mainMessage: str, infoMessage: str=''):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.exec_() 

def displayWarningMessage(mainMessage: str, infoMessage: str=''):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.exec_() 

def displayConfirmationMessage(mainMessage: str, infoMessage: str=''):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
    return msg.exec_()

def displayCriticalMessage(mainMessage: str, infoMessage: str=''):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(mainMessage)
    msg.setInformativeText(infoMessage)
    msg.exec_() 

def date_to_mdates(dates2convert):
        """
        Given a 1D array of strings representing dates, return the array converted to the matplotlib date format.
        Here, we suppose that the dates are in format YYYY:mm:dd:hh:mm:ss
        """
        return mdates.datestr2num([date[0:10].replace(":", "/") + ", " + date[11:] for date in dates2convert])
    
def getShaftsDb(sensorDir):
    sdir = os.path.join(sensorDir, "shafts", "*.csv")
    files = glob.glob(sdir)
    files.sort()
    shafts = []
    for file in files:
        shaft = Shaft()
        shaft.setShaftFromFile(file)
        shafts.append(shaft)
    return shafts

def getThermometersDb(sensorDir):
    sdir = os.path.join(sensorDir, "temperature_sensors", "*.csv")
    files = glob.glob(sdir)
    files.sort()
    thermometers = []
    for file in files:
        thermometer = Thermometer()
        thermometer.setThermometerFromFile(file)
        thermometers.append(thermometer)
    return thermometers

def getPressureSensorsDb(sensorDir):
    sdir = os.path.join(sensorDir, "pressure_sensors", "*.csv")
    files = glob.glob(sdir)
    files.sort()
    pressure_sensors = []
    for file in files:
        psensor = PressureSensor()
        psensor.setPressureSensorFromFile(file)
        pressure_sensors.append(psensor)
    return pressure_sensors
