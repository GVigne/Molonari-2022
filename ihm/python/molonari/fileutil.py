import pandas as pd
from PyQt5 import QtCore
from math import log10, floor

# https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
def RoundTo1(x):
    return round(x, -int(floor(log10(abs(x)))))

def DirExists(path):
    if not path or not QtCore.QDir(path).exists():
        return False
    return True

def FileExists(path):
    if not path or not QtCore.QFile(path).exists():
        return False
    return True

# Convert dates from a list of strings by testing 2 different input format     
def ConvertDates(dates):
    formats = (None, "%m/%d/%y %H:%M:%S", "%m/%d/%y %I:%M:%S %p")
    for f in formats:
        try:
            # Convert strings to datetime objects (rounded to 1 minute)
            new_dates = pd.to_datetime(dates, format=f).round('T')
            return new_dates

        except ValueError:
            continue
        
            # Convert strings to datetime objects (Second date format)
            #mask = new_dates.isnull() # Find all dates which have not been converted yet
            #old_locale = locale.getlocale(locale.LC_TIME) 
            #locale.setlocale(locale.LC_TIME, "en_US.utf8")
            #new_dates[mask] = pd.to_datetime(dates, format="%m/%d/%y %I:%M:%S %p") # Handle AM / PM
            #locale.setlocale(locale.LC_TIME, old_locale)
