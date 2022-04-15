from PyQt5 import QtCore
class MoloModel():
    """
    Abstract class representing a model onto which one or several views may be subscribed.
    """
    dataChanged = QtCore.Signal()

    def __init__(self,queries):
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

class TestModel(MoloModel):
    def __init__(self, queries):
        super().__init__(queries)
    
    def update_df(self):
        pass
    
    def get_temps(self):
        pass
    # def get_depths(self):
    #     depth_array = []
    #     while self.queries[0].next():
    #         depth_array.append(self.queries[0].value(0))
    #     return np.array(depth_array)
    # def get_temps(self):
    #     return