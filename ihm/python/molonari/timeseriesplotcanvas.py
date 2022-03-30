import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

from fileutil import ConvertDates

class TimeSeriesPlotCanvas(FigureCanvas):
    def __init__(self, title, varIdx, varNames=None):
        self.fig = Figure()
        FigureCanvas.__init__(self,self.fig)
        self.title = title
        self.varIdx= varIdx
        self.varNames = varNames
        
    def setModel(self,dfm):
        # TODO : Observe the model (notify) using animated matplotlib :
        # https://stackoverflow.com/questions/11371255/update-lines-in-matplotlib
        # https://stackoverflow.com/questions/10944621/dynamically-updating-plot-in-matplotlib
        self.model = dfm
        
    def show(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        # Get dataframe
        df = self.model.dataFrame
        
        # Get abscissa dates
        dates = df.iloc[:,1]

        # Convert dates
        xarray = ConvertDates(dates)
        
        # Plot all variables
        for i in range(len(self.varIdx)):
            yarray = df.iloc[:,self.varIdx[i]]
            if self.varNames is None:
                self.ax.plot(xarray,yarray)
            else:
                self.ax.plot(xarray,yarray,label=self.varNames[i])
        
        if not self.varNames is None:
            # Add a legend, and position it on the lower right (with no box)
            self.ax.legend(loc="lower right", frameon=False)
        
        #https://matplotlib.org/stable/api/dates_api.html
        #days = mdates.WeekdayLocator(byweekday=MO) # Tick on monday
        #self.ax.xaxis.set_major_locator(days)
        
        #https://www.delftstack.com/howto/matplotlib/matplotlib-set-number-of-ticks/
        self.ax.xaxis.set_major_locator(MaxNLocator(4)) # 4 ticks maximum (let matplotlib choosing the best value)
        self.ax.xaxis.set_minor_locator(mdates.DayLocator())
                
        #https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-with-matplotlib/introduction-to-matplotlib-plots/plot-time-series-data-in-python/
        xformatter = mdates.DateFormatter('%b %d %Y') # %b stands for month abreviation
        self.ax.xaxis.set_major_formatter(xformatter)
        
        # Some cosmetics
        self.ax.grid(True)
        self.ax.set_ylabel(self.title)
        # Rotate X labels
        #plt.setp(ax.xaxis.get_majorticklabels(), 'rotation', 90)
        
        self.draw()
    