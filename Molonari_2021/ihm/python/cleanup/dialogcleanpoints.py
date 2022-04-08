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

    def __init__(self, button):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeScatter, self).__init__(self.fig)
        self.df_selected = pd.DataFrame(columns=["date","value"]) 
        self.r = pd.DataFrame(columns=["date","value"]) 
        self.undoButton = button
        
    def refresh(self, times: pd.Series, values: pd.Series, color):
        if color=="blue":
            p = 4
        else:
            p = 0
        self.axes.plot(mdates.date2num(times), values,'.',c=color,picker=p)
        self.format_axes()
        self.fig.canvas.draw()
    
    def click_connect(self):
        def onpick(event):
            
            ind = event.ind
            datax,datay = event.artist.get_data()
            datax_,datay_ = [datax[i] for i in ind],[datay[i] for i in ind]
            if len(ind) > 1:              
                msx, msy = event.mouseevent.xdata, event.mouseevent.ydata
                dist = np.sqrt((np.array(datax_)-msx)**2+(np.array(datay_)-msy)**2)
                
                ind = [ind[np.argmin(dist)]]
                x = datax[ind][0]
                y = datay[ind][0]

            else:
                x = datax_[0]
                y = datay_[0]
            
            datax = np.delete(datax,ind)
            datay = np.delete(datay,ind)

            datax = pd.Series(mdates.num2date(datax))
            datay = pd.Series(datay)

            x = mdates.num2date(x)
            
            self.r = pd.DataFrame([[x,y]],columns=["date","value"])
            self.df_selected = pd.concat([self.df_selected,self.r])


            self.clear()
            self.refresh(datax,datay,'blue')
            self.refresh(self.df_selected["date"],self.df_selected["value"],"red")
            self.undoButton.setEnabled(True)  


        self.fig.canvas.mpl_connect("pick_event", onpick)

    def clear(self):
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

    def format_axes(self):
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))
    
    def undo(self):
        # self.refresh(self.df_selected["date"],self.df_selected["value"],"red")
        artist = list(self.axes.lines)[0]
        x = self.df_selected.iloc[-1,0]
        y = self.df_selected.iloc[-1,1]

        datax, datay = artist.get_data() 
        datax = pd.Series(mdates.num2date(datax))
        datax = np.append(datax,x)
        
        datay = np.append(datay,y)
        self.df_selected = self.df_selected[:-1]

        self.clear()
        self.refresh(datax,datay,'blue')
        self.refresh(self.df_selected["date"],self.df_selected["value"],"red")
        return self.df_selected.shape[0]
    
    def reset(self, times: pd.Series, values: pd.Series, color):

        self.df_selected = pd.DataFrame(columns=["date","value"]) 
        self.r = pd.DataFrame(columns=["date","value"])
        self.refresh(times, values, color)



class DialogCleanPoints(QtWidgets.QDialog, From_DialogCleanPoints):
    
    def __init__(self):
        # Call constructor of parent classes
        super(DialogCleanPoints, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
        self.pushButtonReset.clicked.connect(self.resetSelection)
        self.pushButtonUndo.clicked.connect(self.undoSelection)
        self.pushButtonUndo.setEnabled(False)
        
    def undoSelection(self):
        # self.mplSelectCurve.clear()
        numSelected = self.mplSelectCurve.undo()
        if numSelected == 0:
            self.pushButtonUndo.setEnabled(False)
    
    def resetSelection(self):
        self.mplSelectCurve.clear()
        self.mplSelectCurve.reset(self.df_original["date"], self.df_original[self.id],"blue")
        self.pushButtonUndo.setEnabled(False)
        
    def plot(self,varName,df):
        self.df_original = df
        
        self.mplSelectCurve = MplCanvasTimeScatter(self.pushButtonUndo)
        self.mplSelectCurve.click_connect()
        self.id = varName

        self.mplSelectCurve.clear()
        self.mplSelectCurve.refresh(self.df_original["date"], self.df_original[self.id],"blue")
        
        self.widgetScatter.addWidget(self.mplSelectCurve)