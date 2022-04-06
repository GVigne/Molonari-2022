import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

From_DialogCleanPoints = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcleanpoints.ui"))[0]

class MplCanvasTimeScatter(FigureCanvasQTAgg):

    def __init__(self):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeScatter, self).__init__(self.fig)
        
    def refresh(self, times, values):
        # TODO : Still string to date conversion needed!
        print(type(times))
        self.axes.plot(mdates.date2num(times), values,'.',picker=5)
        self.format_axes()
        self.fig.canvas.draw()
    
    def click_connect(self):
        def onpick(event):
            print("Enters the envent")
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
            print(datax[ind])
            print(datay[ind])
            datax = np.delete(datax,ind)
            datay = np.delete(datay,ind)
            datax = pd.Series(mdates.num2date(datax))
            # event.artist.get_figure().clear()
            # event.artist.get_figure().gca().plot(datax,datay,'.',picker=5)
            self.clear()
            self.refresh(datax,datay)
            # self.format_axes()
            # event.artist.get_figure().gca().plot(x,y,'.',color="red")  
            # event.artist.get_figure().canvas.draw()

        self.fig.canvas.mpl_connect("pick_event", onpick)

    def clear(self):
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

    def format_axes(self):
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))

class DialogCleanPoints(QtWidgets.QDialog, From_DialogCleanPoints):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogCleanPoints, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
        self.pushButtonReset.clicked.connect(self.resetSelection)
        self.pushButtonUndo.clicked.connect(self.undoSelection)
        
    def undoSelection(self):
        print("Undo please!!")
    
    def resetSelection(Self):
        print("Reset all!!")
    
    def plot():
        print("plot")