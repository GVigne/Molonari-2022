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
        self.df_selected = pd.DataFrame(columns=["date","value"]) 
        
    def refresh(self, times, values, color):
        print("Types: ")
        # print(type(times))
        # print(type(values))
        # print(type(times.iloc[-1]))
        # print(type(values.iloc[-1]))
        self.axes.plot(mdates.date2num(times), values,'.',c=color,picker=5)
        self.format_axes()
        self.fig.canvas.draw()
    
    def click_connect(self):
        def onpick(event):
            print("Enters the envent")
            ind = event.ind
            datax,datay = event.artist.get_data()
            print("len datax: ",datax.shape)
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
            
            # print("Types in event: ")
            # print(type(datax))
            # print(type(datay))
            # print(type(datax[-1]))
            # print(type(datay[-1]))

            datax = np.delete(datax,ind)
            datay = np.delete(datay,ind)
            datax = pd.Series(mdates.num2date(datax))
            x = mdates.num2date(x)
            
            # print(type(datax))
            # print(type(datax.iloc[-1]))
            
            

            self.clear()
            self.refresh(datax,datay,'blue')
            self.refresh(self.selected_x,self.selected_y,"red")  


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
    
    def plot(self,combobox,df):
        print("entra al plot")
        self.mplPrevisualizeCurve = MplCanvasTimeScatter()
        self.mplPrevisualizeCurve.click_connect()
        id = combobox.currentIndex()

        self.mplPrevisualizeCurve.clear()
        self.mplPrevisualizeCurve.refresh(df["date"], df[list(df.columns)[id+1]],"blue")
        
        self.widgetScatter.addWidget(self.mplPrevisualizeCurve)