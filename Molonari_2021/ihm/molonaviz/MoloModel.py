from PyQt5 import QtCore
from PyQt5.QtCore import QObject
import numpy as np

class MoloModel(QObject):
    """
    Abstract class representing a model onto which one or several views may be subscribed.
    """
    dataChanged = QtCore.Signal()

    def __init__(self,queries):
        super(MoloModel, self).__init__()
        self.queries = queries
        self.df= None
    
    def exec(self):
        """
        Exec all queries and notify the subscribed views that the data has been modified.
        """
        for i in self.queries:
            i.exec()
        self.update_df()
        self.dataChanged.emit()

    def update_df(self):
        """
        This function must be overloaded if data has to be added to a panda dataframe.
        """
        pass
    
    def register(self,view):
        """
        Subscribe the given view to the MoloModel.
        """
        self.dataChanged.connect(view.on_update)

class PressureDataModel(MoloModel):
    """
    A model to display the presure as given by the captors (raw or cleaned data).
    """
    def __init__(self, queries):
        super().__init__(queries)
        self.array_data = []

    def update_df(self):
        while self.queries[0].next():
            self.array_data.append([self.queries[0].value(0),self.queries[0].value(1)]) #Date, Pressure
        self.array_data = np.array(self.array_data)

    def get_pressure(self):
        return self.array_data[:,1]
    
    def get_dates(self):
        return self.array_data[:,0]

class TemperatureDataModel(MoloModel):
    """
    A model to display the presure as given by the captors (raw or cleaned data).
    """
    def __init__(self, queries):
        super().__init__(queries)
        self.array_data = []

    def update_df(self):
        while self.queries[0].next():
            self.array_data.append([self.queries[0].value(0),self.queries[0].value(1),self.queries[0].value(2),self.queries[0].value(3),self.queries[0].value(4),self.queries[0].value(5)]) #Date, Temp1 to 4, Temp_Bed
        self.array_data = np.array(self.array_data)

    def get_temperatures(self):
        return [self.array_data[:, i] for i in range(1,6)]
    
    def get_dates(self):
        return self.array_data[:,0]