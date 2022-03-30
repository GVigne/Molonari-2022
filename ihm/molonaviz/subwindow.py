from PyQt5 import QtWidgets, QtGui, QtCore, uic
from widgetpoint import WidgetPoint

class SubWindow(QtWidgets.QMdiSubWindow):
    
    def __init__(self, point, study):
        # Call constructor of parent classes
        super(SubWindow, self).__init__()
        QtWidgets.QMdiSubWindow.__init__(self)
        
        self.name = point.getName() #on donne à la subWindow le nom du point associé
        wdg = WidgetPoint(point, study)
        self.wdg = wdg
    
    def getName(self):
        return self.name
    
    def setPointWidget(self):
        self.setWidget(self.wdg)
        self.wdg.setInfoTab()
        self.wdg.setWidgetInfos()
        self.wdg.setPressureAndTemperatureModels()
    
    def closeEvent(self, event):
        event.accept()
        mdi = self.mdiArea()
        if mdi.viewMode() == QtWidgets.QMdiArea.SubWindowView:
            mdi.removeSubWindow(self)
            mdi.tileSubWindows()
        elif mdi.viewMode() == QtWidgets.QMdiArea.TabbedView:
            mdi.setViewMode(QtWidgets.QMdiArea.SubWindowView)
            mdi.removeSubWindow(self)
            mdi.setViewMode(QtWidgets.QMdiArea.TabbedView)



