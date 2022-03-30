from os.path import dirname, join

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import uic

from dataframemodel import DataFrameModel

from cleanupdialog import CleanupDialog
from computedialog import ComputeDialog
from timeseriesplotcanvas import TimeSeriesPlotCanvas
from timeprofilesimagecanvas import TimeProfilesImageCanvas
from fileutil import FileExists, ConvertDates

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import matplotlib.pyplot as plt

From_DataPointView,_= uic.loadUiType(join(dirname(__file__),"datapointview.ui"))
class DataPointView(QtWidgets.QWidget, From_DataPointView):

    def __init__(self, study, point):
        super(DataPointView, self).__init__()
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)
        
        self.script = ""
        
        self.butReset.clicked.connect(self.reset)
        self.butCleanup.clicked.connect(self.cleanup)
        self.butCompute.clicked.connect(self.compute)
        
        self.checkShowRaw.toggled.connect(self.showRaw)
        self.checkShowRaw.setChecked(False)
        self.showRaw(False)
        
        self.tabDataPoint.setTabVisible(7, False) # Results
        self.tabDataPoint.setTabVisible(8, True) # Inversion
        
        self.startDate = point.lastDate
        self.endDate = point.lastDate
        self.study = study
        self.point = point
        
        self.setWindowTitle("{} View".format(self.point.name))
        self.editSensor.setText(self.point.geometry.sensor.name)
        self.editDate.setDate(self.point.lastDate.date())
        
        self.textGeometry.setPlainText(open(study.descrPath(point,1)).read())
        self.textNotice.setPlainText(open(study.descrPath(point,2)).read())
        self.labelInstall.setPixmap(QtGui.QPixmap(study.descrPath(point,3)))
        
        # TODO : Beware : Column indices are hard coded
        self.plotViewRawTemp = TimeSeriesPlotCanvas("Temperature (K)", [2,3,4,5], self.point.geometry.toStringList())
        self.plotViewRawPress = TimeSeriesPlotCanvas("Tension (V)", [2])
        self.layoutPlotRaw.addWidget(self.plotViewRawTemp)
        self.layoutPlotRaw.addWidget(self.plotViewRawPress)
        self.plotViewTemp = TimeSeriesPlotCanvas("Temperature (K)", [2,3,4,5], self.point.geometry.toStringList())
        self.plotViewPress = TimeSeriesPlotCanvas("Head Differential (m)", [2])
        self.layoutPlotTemp.addWidget(self.plotViewTemp)
        self.layoutPlotPress.addWidget(self.plotViewPress)
        self.plotViewProfiles = TimeProfilesImageCanvas("Temporal Estimation of Temperature (K)", [2])
        self.plotViewRivTemp = TimeSeriesPlotCanvas("River Temperature (K)", [2])
        self.layoutResTemp.addWidget(self.plotViewRivTemp)
        self.layoutResProf.addWidget(self.plotViewProfiles)
        
        index = self.tabDataPoint.indexOf(self.tabPlot)
        self.tabDataPoint.setCurrentIndex(index)

    def loadRaw(self):
        fileName = self.study.rawPath(self.point, 1) # Raw Temperature
        model = DataFrameModel.fromCSV(fileName, skiprows=0, header=1)
        if (model.dataFrame is not None):
            self.tableViewRawTemp.setModel(model)
            self.plotViewRawTemp.setModel(model)
            self.plotViewRawTemp.show()
            
        fileName = self.study.rawPath(self.point, 2) # Raw Tension (for Pressure)
        model = DataFrameModel.fromCSV(fileName, skiprows=0, header=1)
        if (model.dataFrame is not None):
            self.tableViewRawPress.setModel(model)
            self.plotViewRawPress.setModel(model)
            self.plotViewRawPress.show()
                    
        return True
    
    def loadProcessed(self):
        fileName = self.study.processedPath(self.point, 1) # Processed Temperature
        model = DataFrameModel.fromCSV(fileName, header=0)
        if (model.dataFrame is not None):
            self.tableViewTemp.setModel(model)
            self.plotViewTemp.setModel(model)
            # TODO : Overlay stream temperature (from Pressure file) before showing the plot
            self.plotViewTemp.show()
            
        if (model.dataFrame is not None):
            self.startDate = ConvertDates(model.dataFrame.values[0,1]) # Hard coded column index for date
            self.endDate = ConvertDates(model.dataFrame.values[-1,1]) # Hard coded column index for date

        fileName = self.study.processedPath(self.point, 2) # Processed Pressure
        model = DataFrameModel.fromCSV(fileName, header=0)
        if (model.dataFrame is not None):
            self.tableViewPress.setModel(model)
            self.plotViewPress.setModel(model)
            self.plotViewPress.show()

        return True

    def loadResults(self):
        fileName = self.study.resultPath(self.point, 1) # River temperature
        if (FileExists(fileName)):
            model = DataFrameModel.fromCSV(fileName, header=0)
            if (model.dataFrame is not None):
                self.plotViewRivTemp.setModel(model)
                self.plotViewRivTemp.show()
                self.tabDataPoint.setTabVisible(7, True) # Results tab
                
        fileName = self.study.resultPath(self.point, 2) # Temperature profiles
        if (FileExists(fileName)):
            model = DataFrameModel.fromCSV(fileName, header=0, index_col=0)
            if (model.dataFrame is not None):
                self.plotViewProfiles.setModel(model)
                self.plotViewProfiles.show()
                self.tabDataPoint.setTabVisible(7, True) # Results tab
        
        return True
    
    def loadInversion(self):
        # TODO : Load Inversion outputs
        return True
    
    def load(self):
        self.loadRaw()
        self.loadProcessed()
        self.loadResults()
        self.loadInversion()
        return True

    def showRaw(self, show):
        self.tabDataPoint.setTabVisible(1, show) # Raw temperatures
        self.tabDataPoint.setTabVisible(2, show) # Raw tension
        self.tabDataPoint.setTabVisible(3, show) # Raw plots
        
    def reset(self):
        ask = QMessageBox()
        ask.setIcon(QMessageBox.Question)
        ask.setWindowTitle('Warning!')
        ask.setInformativeText("Do you really want to reset the current point?")
        ask.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        ret = ask.exec()
        if ret == QMessageBox.Ok:
            if (self.study.processPoint(self.point)):
                self.tabDataPoint.setTabVisible(7, False) # Results tab
                self.tabDataPoint.setTabVisible(8, False) # Inversion tab
                self.loadProcessed()    

    def cleanup(self):
        diag = CleanupDialog(self, self.point, self.script)
        diag.show()
                
    def cleanupPoint(self, script):
        self.script = script
        if (self.study.cleanupPoint(self.point, self.script)):
            self.tabDataPoint.setTabVisible(7, False) # Results tab
            self.tabDataPoint.setTabVisible(8, False) # Inversion tab
            self.loadProcessed()

    def compute(self):
        diag = ComputeDialog(self, self.startDate, self.endDate, self.study, self.point)
        diag.show()
