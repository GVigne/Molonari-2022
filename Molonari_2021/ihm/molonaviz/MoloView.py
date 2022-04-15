from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np
from MoloModel import MoloModel

class MoloView(FigureCanvasQTAgg):
    """
    Abstract class to implement a view.
    """
    def __init__(self, molomodel : MoloModel):
        self.model = molomodel
        self.model.register(self)
    
    def on_update(self):
        """
        This method is called when the data is changed. It must be overloaded for the child classes.
        """
        pass

class MoloView1D(MoloView):
    """
    Abstract class to represent 1D views (such the pressure and temperature plots)
    """
    def __init__(self, molomodel: MoloModel):
        super().__init__(molomodel)
    
    def on_update(self):
        pass

class MoloView2D(MoloView):
    """
    Abstract class to represent 2D views (such the temperature heat maps)
    """
    def __init__(self, molomodel: MoloModel):
        super().__init__(molomodel)
    
    def on_update(self):
        pass

class PressureView(MoloView1D):
    """
    Concrete class to display the Pressure in "Data arrays and plots" tab.
    """
    def __init__(self, molomodel: MoloModel):
        super().__init__(molomodel)
    
    def on_update(self):
        temperature  = self.model.get_temperature()