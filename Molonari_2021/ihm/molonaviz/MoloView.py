import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import numpy as np
from MoloModel import MoloModel

class MoloView(FigureCanvasQTAgg):
    """
    Abstract class to implement a view.
    """
    def __init__(self, molomodel : MoloModel, width=5, height=5, dpi=100):
        #Subscribe to the model
        self.model = molomodel
        self.model.register(self)

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MoloView, self).__init__(self.fig)
        self.fig.tight_layout(h_pad=5, pad=5)
        self.axes = self.fig.add_subplot(111)

    def on_update(self):
        """
        This method is called when the data is changed. It must be overloaded for the child classes.
        """
        pass
    
    def retrieve_data(self):
        """
        This method should only be overloaded for concrete classes to fetch data from the model.
        """
        pass

class MoloView1D(MoloView):
    """
    Abstract class to represent 1D views (such the pressure and temperature plots).
    If time_dependent is true, then the x-array is expected to be an array of dates and will be displayed as such.

    There are two main attributes in this class:
        -self.x is a 1D array and will be displayed one the x-axis
        -self.y is a dictionnary of 1D array : the keys are the labels which should be displayed. This is useful to plot many graphs on the same view (quantiles for example). 
    """
    def __init__(self, molomodel: MoloModel,time_dependent=False,ylabel="",xlabel=""):
        super().__init__(molomodel)
        #x and y correspond to the data which should be displayed on the x-axis and y-axis (ex: x=Date,y=Pressure)

        self.x = []
        self.y = {}
        self.xlabel = xlabel
        self.ylabel=ylabel
        self.time_dependent = time_dependent

    def on_update(self):
        self.retrieve_data()
        self.setup_x()
        self.plot_data()
        self.draw()
    
    def setup_x(self):
        """
        This method allows to apply changes to the data on the x-axis (for example, format a date).
        """
        if self.time_dependent:
            self.x = self.format(self.x)
            formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
            self.axes.xaxis.set_major_formatter(formatter)
            self.axes.xaxis.set_major_locator(MaxNLocator(4))
            plt.setp(self.axes.get_xticklabels(), rotation = 15)
        else:
            pass
    
    def format(self,dates2convert):
        """
        Given a 1D array of strings representing dates, return the array converted to the matplotlib date format.
        Here, we suppose that the dates are in format YYYY:mm:dd:hh:mm:ss
        """
        return mdates.datestr2num([date[0:10].replace(":", "/") + ", " + date[11:] for date in dates2convert])
    
    def plot_data(self):
        for index, (label, data) in enumerate(self.y.items()):
            self.axes.plot(self.x, data, label=label)
        self.axes.legend(loc='best')
        self.axes.set_ylabel(self.ylabel)

        self.axes.set_xlabel(self.xlabel)
        self.axes.grid(True)

class MoloView2D(MoloView):
    """
    Abstract class to represent 2D views (such the temperature heat maps)
    """
    def __init__(self, molomodel: MoloModel,time_dependent=False):
        super().__init__(molomodel)

        self.time_dependent = time_dependent
        self.x = []
    
    def on_update(self):
        self.setup_x()
        self.plot_data()
        self.draw()

    def setup_x(self):
        """
        This method allows to apply changes to the data on the x-axis (for example, format a date).
        """
        if self.time_dependent:
            self.x = self.format(self.x)
            formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
            self.axes.xaxis.set_major_formatter(formatter)
            self.axes.xaxis.set_major_locator(MaxNLocator(4))
            plt.setp(self.axes.get_xticklabels(), rotation = 15)
        else:
            pass

    def format(self,dates2convert):
        """
        Given a 1D array of strings representing dates, return the array converted to the matplotlib date format.
        Here, we suppose that the dates are in format YYYY:mm:dd:hh:mm:ss
        """
        return mdates.datestr2num([date[0:10].replace(":", "/") + ", " + date[11:] for date in dates2convert])

    def plot_data(self):
        pass

class PressureView(MoloView1D):
    """
    Concrete class to display the Pressure in "Data arrays and plots" tab.
    """
    def __init__(self, molomodel: MoloModel,time_dependent=False,ylabel="",xlabel=""):
        super().__init__(molomodel,time_dependent=time_dependent,ylabel=ylabel,xlabel=xlabel)
    
    def retrieve_data(self):
        self.x  = self.model.get_dates()
        self.y  = {"":self.model.get_pressure()} #No label required for this one.

class TemperatureView(MoloView1D):
    """
    Concrete class to display the Pressure in "Data arrays and plots" tab.
    """
    def __init__(self, molomodel: MoloModel,time_dependent=False,ylabel="",xlabel=""):
        super().__init__(molomodel,time_dependent=time_dependent,ylabel=ylabel,xlabel=xlabel)
    
    def retrieve_data(self):
        self.x  = self.model.get_dates()
        self.y  = {f"Capteur n°{i}":temp for i,temp in enumerate(self.model.get_temperatures())}