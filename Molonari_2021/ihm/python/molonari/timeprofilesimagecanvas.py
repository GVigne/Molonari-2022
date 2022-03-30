import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import ticker

from fileutil import ConvertDates

class TimeProfilesImageCanvas(FigureCanvas):
    def __init__(self, title, varIdx, varNames=None):
        self.fig = Figure()
        FigureCanvas.__init__(self,self.fig)
        self.title = title
        self.varIdx= varIdx
        self.varNames = varNames
        
    def setModel(self,dfm):
        self.model = dfm
        
    def show(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        # Get dataframe
        df = self.model.dataFrame
        
        # Show profiles
        cax = self.ax.imshow(df)

        # X axis
        dates = pd.to_datetime(df.columns)
        self.ax.set_xticks(np.arange(0.9, len(df.columns),1))
        self.ax.set_xticklabels(dates.strftime('%b %d %Y'))
        self.ax.locator_params(axis='x', nbins=10)
        self.fig.autofmt_xdate()
        
        # Y axis
        self.ax.set_yticks(np.arange(0.5, len(df.index), 1))
        self.ax.set_yticklabels(np.round(df.index,2))
        self.ax.locator_params(axis='y', nbins=5)
        self.ax.set_ylabel("Depth [m]")
        
        # General parameters
        self.ax.set_title("Temporal Estimation of Temperature (K)")
        self.fig.colorbar(cax)
        
        #https://www.delftstack.com/howto/matplotlib/matplotlib-set-number-of-ticks/
        #self.ax.xaxis.set_major_locator(ticker.MaxNLocator(4)) # 4 ticks maximum (let matplotlib choosing the best value)
        #self.ax.xaxis.set_minor_locator(mdates.DayLocator())
        #https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-with-matplotlib/introduction-to-matplotlib-plots/plot-time-series-data-in-python/
        #xformatter = mdates.DateFormatter('%b %d %Y') # %b stands for month abreviation
        #self.ax.xaxis.set_major_formatter(xformatter)
        
        #https://stackoverflow.com/questions/11586989/pandas-matplotlib-use-dataframe-index-as-axis-tick-labels
        #self.ax.yaxis.set_major_locator(ticker.MaxNLocator(5)) # 5 ticks maximum (let matplotlib choosing the best value)
        #self.ax.set_yticks(range(len(df.index)))
        #self.ax.set_yticklabels(np.round(df.index, 2))
        #self.ax.set_ylabel("Depth [m]")

        #self.ax.set_title(self.title)
        
        #self.fig.colorbar(cax)
        
        #self.draw()
    