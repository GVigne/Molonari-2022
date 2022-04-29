import os
import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, uic
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

From_DialogCleanPoints = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogcleanpoints.ui"))[0]

class MplCanvasTimeScatter(FigureCanvasQTAgg):

    def __init__(self, button, df_selected,id): # Figure initializer
        """button is the undo button, id is the name of the current variable (string)"""
        self.id = id
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super(MplCanvasTimeScatter, self).__init__(self.fig)
        self.df_selected = df_selected
        self.r = pd.DataFrame(columns=["date",self.id])
        self.undo_list = [] 
        self.undoButton = button

    def create_selector(self):
        self.selector = RectangleSelector(self.axes, self.selec_function, useblit=True) # Rectangle selector

    def selec_function(self, event1, event2):
        """Uptdates the plot with the selected pooints by the Rectangle Selector"""
        artist = list(self.axes.lines)[0]
        x,y = artist.get_data()
        x = pd.Series(mdates.num2date(x))
        y = pd.Series(y)
        self.x, self.y = x.copy(), y.copy()
        self.mask = np.zeros(len(x), dtype=bool)
        self.mask = self.inside(event1, event2) # Gets the mask of the points inside the rectangle

        data = pd.concat([self.x,self.y],axis=1,keys=["date",self.id])

        self.rectangle = data[self.mask]
        self.out_rectangle = data[~self.mask]

        self.df_selected = pd.concat([self.df_selected,self.rectangle]) # Updates df_selected

        self.undo_list.append(self.rectangle.shape[0])  # Updates undo_list with the amount of points selected
        # Refresh plot
        self.clear()
        self.refresh(self.out_rectangle["date"],self.out_rectangle[self.id],'blue')
        self.refresh(self.df_selected["date"],self.df_selected[self.id],"red")
        self.create_selector()
        self.undoButton.setEnabled(True)  

    def inside(self, event1, event2):
        """Returns a boolean mask of the points inside the rectangle defined by
        event1 and event2."""
        # Note: Could use points_inside_poly, as well
        x0, x1 = sorted([event1.xdata, event2.xdata])
        x0 = mdates.num2date(x0)
        x1 = mdates.num2date(x1)
        y0, y1 = sorted([event1.ydata, event2.ydata])
        mask = ((self.x > x0) & (self.x < x1) &
                (self.y > y0) & (self.y < y1))
        return mask   
        
    def refresh(self, times: pd.Series, values: pd.Series, color):
        if color=="blue":  # Blue line can be selected, then p != 0
            p = 4
            ms = 1
        else: # Red line cannot be selected, then p=0
            p = 0
            ms = 1
        self.axes.plot(mdates.date2num(times), values,'.',c=color,picker=p,markersize=ms)
        
        self.format_axes()
        self.fig.canvas.draw()

    
    def click_connect(self):
        def onpick(event):
            ind = event.ind # Get the indices of the selected points
            datax,datay = event.artist.get_data()
            datax_,datay_ = [datax[i] for i in ind],[datay[i] for i in ind] 
            if len(ind) > 1:  
                # In case there were several points selected at one click (because they were too close),
                # get the closest point to the mouse event            
                msx, msy = event.mouseevent.xdata, event.mouseevent.ydata
                dist = np.sqrt((np.array(datax_)-msx)**2+(np.array(datay_)-msy)**2)
                
                ind = [ind[np.argmin(dist)]]
                x = datax[ind][0]
                y = datay[ind][0]

            else:
                x = datax_[0]
                y = datay_[0]
            
            datax = np.delete(datax,ind) # Delete from the current data
            datay = np.delete(datay,ind)

            datax = pd.Series(mdates.num2date(datax))
            datay = pd.Series(datay)

            x = mdates.num2date(x)
            
            self.r = pd.DataFrame([[x,y]],columns=["date",self.id])
            self.df_selected = pd.concat([self.df_selected,self.r]) # Add it to the selected data
            self.undo_list.append(1)
            # Refresh plot
            self.clear()
            self.refresh(datax,datay,'blue')
            self.refresh(self.df_selected["date"],self.df_selected[self.id],"red")
            self.create_selector()
            self.undoButton.setEnabled(True)  
            

        self.fig.canvas.mpl_connect("pick_event", onpick)


    def clear(self):
        """ Clears figure and creates one again """
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

    def format_axes(self):
        # Beautiful time axis
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))
    
    def undo(self):
        """ recovers the last selected points in order """
        artist = list(self.axes.lines)[0]
        n=self.undo_list.pop()
        x = self.df_selected.iloc[-n:,0]
        y = self.df_selected.iloc[-n:,1]
        
        datax, datay = artist.get_data() 
        datax = pd.Series(mdates.num2date(datax))
        datax = np.append(datax,x)
        datay = np.append(datay,y)

        self.df_selected = self.df_selected[:-n]

        self.clear()
        self.refresh(datax,datay,'blue')
        self.refresh(self.df_selected["date"],self.df_selected[self.id],"red")
        self.create_selector()

        return self.df_selected.shape[0]
    
    def reset(self, times: pd.Series, values: pd.Series, color):
        """ cleans every selected point """
        self.df_selected = pd.DataFrame(columns=["date",self.id]) 
        self.r = pd.DataFrame(columns=["date",self.id])
        self.refresh(times, values, color)
        self.create_selector()



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
        
    def plot(self,  varName, df : pd.DataFrame, df_selected : pd.DataFrame):
        self.id = varName
        self.df_original = df.copy().dropna()
        self.df_selected = df_selected.copy()[["date",self.id]].dropna() # Takes the variable only
        self.mplSelectCurve = MplCanvasTimeScatter(self.pushButtonUndo, self.df_selected, self.id)
        self.mplSelectCurve.clear()
        self.mplSelectCurve.refresh(self.df_original["date"], self.df_original[self.id],"blue")
        ## TODO Create function to execute if df_selected.shape[0] > 0 to update red and blue dots
        if self.df_selected.shape[0]: # If there are more than 1 selected points
            artist = list(self.mplSelectCurve.axes.lines)[0]
            x,y = artist.get_data()
            x = pd.Series(mdates.num2date(x))
            y = pd.Series(y)

            mask = self.df_original.apply(lambda x: True if mdates.date2num(x['date']) in list(mdates.date2num(self.df_selected['date'])) else False,axis=1) # Get mask
            
            data = pd.concat([x,y],axis=1,keys=["date",self.id])
 
            not_selected = data[~mask]

            self.mplSelectCurve.undo_list.append(self.df_selected.shape[0])

            self.mplSelectCurve.clear()
            self.mplSelectCurve.refresh(not_selected["date"],not_selected[self.id],'blue')
            self.mplSelectCurve.refresh(self.df_selected["date"],self.df_selected[self.id],"red")
            self.mplSelectCurve.undoButton.setEnabled(True)  

        self.mplSelectCurve.create_selector()
        self.mplSelectCurve.click_connect()


        self.toolBar = NavigationToolbar2QT(self.mplSelectCurve,self)

        self.widgetToolBar.addWidget(self.toolBar)
        self.widgetScatter.addWidget(self.mplSelectCurve)