from PyQt5 import QtCore
from PyQt5.QtCore import QObject
import numpy as np

class MoloModel(QObject):
    """
    Abstract class representing a model onto which one or several views may be subscribed.
    If there are different queries for different quantiles, then the first query MUST be the on which corresponds to the default model.
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

class WaterFluxModel(MoloModel):
    """
    A model to display the water fluxes.
    """
    def __init__(self, queries):
        super().__init__(queries)
        self.flows = {}
        self.dates=[]
    
    def update_df(self):
        #Initialize data structures
        self.queries[0].next()
        self.dates.append(self.queries[0].value(0))
        self.flows[self.queries[0].value(2)] = [self.queries[0].value(1)]
        while self.queries[0].next():
            self.dates.append(self.queries[0].value(0)) #Dates
            self.flows[self.queries[0].value(2)].append(self.queries[0].value(1)) #Flow
        for i in range(1,len(self.queries)):
            self.queries[i].next()
            self.flows[self.queries[i].value(2)] = [self.queries[i].value(1)]
            #Add the other flows for the different quantiles if they exist
            while self.queries[i].next():
                self.flows[self.queries[i].value(2)].append(self.queries[i].value(1))
    
    def get_water_flow(self):
        """
        Return a dictionnary with keys beings the quantiles and values being the arrays of associated flows.
        """
        return {key:np.array(value) for index, (key,value) in enumerate(self.flows.items())}
    
    def get_dates(self):
        return np.array(self.dates)

class SolvedTemperatureModel(MoloModel):
    """
    A model to representing the temperature, depth and time. Can be used for umbrellas, temperature heat map or temperature per depth.
    """
    def __init__(self, queries):
        super().__init__(queries)
    
    def update_df(self):
        self.dates = []
        self.data = {}
        self.depths = []
        while self.queries[0].next():
            self.dates.append(self.queries[0].value(0))
        self.dates = np.array(self.dates)
        while self.queries[1].next():
            self.depths.append(np.float64(self.queries[1].value(0)))
        self.depths = np.array(self.depths)

        for i in range(2,len(self.queries)):
            query = self.queries[i]
            query.next()
            array_data = [np.float64(query.value(2))]
            quantile = query.value(3)
            while query.next():
                array_data.append(np.float64(query.value(2)))
            array_data = np.array(array_data)
            nb_elems = array_data.shape[0]
            x = len(self.depths) #One hundred cells
            y = nb_elems//x
            array_data = np.transpose(array_data.reshape(x,y))#Now this is the color map with y-axis being the depth and x-axis being the time
            self.data[quantile] = array_data

    
    def get_temperatures_cmap(self,quantile):
        """
        Given a quantile, return the associated heat map.
        """
        return self.data[quantile]
    
    def get_depths(self):
        return self.depths
    
    def get_dates(self):
        return self.dates
    
    def get_depth_by_temp(self,date, quantile):
        """
        Return two lists: the temperature and depth for given date and quantile. The date must be in the database format (YYYY:mm:dd:hh:mm:ss)
        """
        return self.array_data[quantile][:,np.where(self.dates==date)[0][0]],self.depths
    
    def get_temp_by_date(self,depth,quantile):
        """
        Return the temperatures for a given depth and quantile.
        """
        return self.array_data[quantile][np.where(self.depths == depth)[0][0],:]
    
class HeatFluxesModel(MoloModel):
    """
    A model to display the three heat fluxes (advective, conductive, total)
    """
    def __init__(self, queries):
        super().__init__(queries)

    def update_df(self):
        self.dates = []
        self.array_data = []
        self.depths = []
        while self.queries[0].next():
            self.dates.append(self.queries[0].value(0))
            self.array_data.append([np.float64(self.queries[0].value(1)),np.float64(self.queries[0].value(2)),np.float64(self.queries[0].value(3))]) #Advective, conductive, total
            self.depths.append(np.float64(self.queries[0].value(4)))
        self.dates = np.array(self.dates)
        self.array_data = np.array(self.array_data)
        self.depths = np.array(self.depths)

        self.advective = self.build_picture(self.array_data[:,0],nb_cells =len(self.depths))
        self.conductive = self.build_picture(self.array_data[:,1],nb_cells =len(self.depths))
        self.total = self.build_picture(self.array_data[:,2],nb_cells =len(self.depths))

    def build_picture(self,flow, nb_cells):
        """
        Given a 1D numpy array, convert it into a 100*nb_cells picture. Used to convert data from the database into a 2D map with respect to the number of cells. 
        """
        nb_elems = flow.shape[0]
        x = nb_cells #One hundred cells
        y = nb_elems//x
        return np.transpose(flow.reshape(x,y))#Now this is the color map with y-axis being the depth and x-axis being the time
    
    def get_depths(self):
        return self.depths
    
    def get_dates(self):
        return self.dates
    
    def get_advective_flow(self):
        return self.advective
    
    def get_conductive_flow(self):
        return self.conductive
    
    def get_total_flow(self):
        return self.total

class ParamsDistributionModel(MoloModel):
    def __init__(self, queries):
        super().__init__(queries)
    
    def update_df(self):
        pass