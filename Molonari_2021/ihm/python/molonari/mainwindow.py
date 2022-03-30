# Requirements :
# python3 -m pip install --user pyqt5
# python3 -m pip install --user matplotlib
# python3 -m pip install --user pandas
# sudo apt-get install python3-pyqt5  
# sudo apt-get install pyqt5-dev-tools
# sudo apt-get install qttools5-dev-tools

import sys
import os
import locale
from queue import Queue

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5 import uic

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor

import datapointview as dpv

from preferencesdialog import PreferencesDialog

from study import Study
from studydialog import StudyDialog

from importpointdialog import ImportPointDialog

from queuethread import *

From_MainWindow,dummy = uic.loadUiType(os.path.join(os.path.dirname(__file__),"mainwindow.ui"))
class MainWindow(QtWidgets.QMainWindow,From_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        
        # Create Queue and redirect sys.stdout to this queue
        self.queue = Queue()
        sys.stdout = WriteStream(self.queue)
        
        # Just to know the current locale
        print("MolonaViz - 0.0.1beta - 2021-04-23")
        print("Using locale:{}".format(locale.getlocale()))

        self.actionNew_Study.triggered.connect(self.newStudy)
        self.actionOpen_Study.triggered.connect(self.openStudy)
        self.actionSave_As_Study.triggered.connect(self.saveAsStudy)
        self.actionEdit_Study.triggered.connect(self.editStudy)
        
        self.actionImport_Point.triggered.connect(self.importPoint)
        self.actionOpen_Point.triggered.connect(self.openCurPoint)
        self.actionRemove_Point.triggered.connect(self.removeCurPoint)
        
        self.actionAbout_MolonaViz.triggered.connect(self.about)

        self.actionTile_Win.triggered.connect(self.mdiArea.tileSubWindows)
        self.actionCascade_Win.triggered.connect(self.mdiArea.cascadeSubWindows)
        self.actionNext_Win.triggered.connect(self.mdiArea.activateNextSubWindow)
        self.actionPrevious_Win.triggered.connect(self.mdiArea.activatePreviousSubWindow)
        self.actionClose_Win.triggered.connect(self.mdiArea.closeActiveSubWindow)
        self.actionClose_All_Win.triggered.connect(self.mdiArea.closeAllSubWindows)
        self.actionPreferences.triggered.connect(self.showPreferences)
        
        self.treePoints.doubleClicked.connect(self.openPoint)
        
        #self.currentStudy = Study.createDefault()
        # TODO : to be removed
        self.currentStudy = Study.createOpen("/home/fors/molonari_data/my_study3")

        self.pointModel = QtGui.QStandardItemModel()
        self.treePoints.setModel(self.pointModel)
        
        self.sensorModel = QtGui.QStandardItemModel()
        self.treeSensors.setModel(self.sensorModel)
        
        self.loadSensors()
        self.loadPoints()
        
        self.updateStatus()
        
        # TODO : To be removed
        self.selectPoint("point41")
        self.openCurPoint()

    #@pyqtSlot(str)
    def append_text(self,text):
        self.textEditMessages.moveCursor(QTextCursor.End)
        self.textEditMessages.insertPlainText( text )

    def newStudy(self):
        diag = StudyDialog(self, 0)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            self.currentStudy = diag.getStudy()
            self.currentStudy.create()
            self.loadSensors()
            self.loadPoints()
        self.updateStatus()
            
    def openStudy(self):
        diag = StudyDialog(self, 1)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            study = diag.getStudy()
            if not study.isValid(True):
                # TODO : Use the trace window in place of all QMessageBox
                QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Cannot open study!')
            else:
                self.currentStudy = study
                self.loadSensors()
                self.loadPoints()
        self.updateStatus()
        
    def saveAsStudy(self):
        diag = StudyDialog(self, 3, self.currentStudy)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            newStudy = diag.getStudy()
            self.currentStudy.saveAs(newStudy)
        self.updateStatus()
        
    def editStudy(self):
        diag = StudyDialog(self, 2, self.currentStudy)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            newStudy = diag.getStudy()
            if newStudy.isValid(True):
                self.currentStudy.edit(newStudy)
                self.loadSensors()
                self.loadPoints()
            else:
                QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Study not valid!')
        self.updateStatus()
        
    def importPoint(self):
        diag = ImportPointDialog(self, self.sensorModel)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            # TODO : Progress bar
            point = diag.getPoint()
            src = diag.getSourceFiles()
            if self.currentStudy.importPoint(point,src):
                if (self.currentStudy.processPoint(point)):
                    if (self.loadPoints()):
                        self.selectPoint(point.name)
                        self.openCurPoint()

    def selectPoint(self, pointName):
        items = self.pointModel.findItems(pointName)
        if (len(items) > 0):
            index = self.pointModel.indexFromItem(items[0])
            self.treePoints.selectionModel().setCurrentIndex(index,QtCore.QItemSelectionModel.SelectCurrent);
        
    def openPoint(self, index):
        # TODO: Test if point is not already opened
        item = self.pointModel.itemFromIndex(index)
        point = item.data(QtCore.Qt.UserRole)
        child = dpv.DataPointView(self.currentStudy, point)
        self.mdiArea.addSubWindow(child)
        child.load()
        child.show()
        
    def openCurPoint(self):
        index = self.treePoints.selectedIndexes()
        if len(index) > 0:
            self.openPoint(index[0])
            
    def removeCurPoint(self):
        index = self.treePoints.selectedIndexes()
        if len(index) > 0:
            item = self.pointModel.itemFromIndex(index[0])
            point = item.data(QtCore.Qt.UserRole)
            self.currentStudy.removePoint(point)
            self.pointModel.removeRows(index[0].row(), 1)
        if self.pointModel.rowCount() == 0:
            self.pointModel.appendRow(QtGui.QStandardItem("No point yet"))

    def loadSensors(self):
        self.sensorModel.clear()
        isValid = self.currentStudy.isValid()
        if isValid:
            isValid = False
            dirs = os.listdir(self.currentStudy.sensorDir)
            for mydir in dirs:
                sensor = self.currentStudy.loadSensor(mydir)
                item = QtGui.QStandardItem(mydir)
                item.setData(sensor, QtCore.Qt.UserRole)
                self.sensorModel.appendRow(item)
                item.appendRow(QtGui.QStandardItem("intercept = {:.2f}".format(float(sensor.intercept))))
                item.appendRow(QtGui.QStandardItem("dudh = {:.2f}".format(float(sensor.dudh))))
                item.appendRow(QtGui.QStandardItem("dudt = {:.2f}".format(float(sensor.dudt))))
                isValid = True
        if not isValid:
            self.sensorModel.appendRow(QtGui.QStandardItem("No sensor yet"))
        return isValid
        
    def loadPoints(self):
        self.pointModel.clear()
        isValid = self.currentStudy.isValid()
        if isValid:
            isValid = False
            dirs = os.listdir(self.currentStudy.descrPath())
            for mydir in dirs:
                point = self.currentStudy.loadPoint(mydir, self.sensorModel)
                item = QtGui.QStandardItem(mydir)
                item.setData(point, QtCore.Qt.UserRole)
                self.pointModel.appendRow(item)
                isValid = True
        if not isValid:
            self.pointModel.appendRow(QtGui.QStandardItem("No point yet"))
        return isValid
    
    def showPreferences(self):
        diag = PreferencesDialog(self)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            pref = diag.getPreferences()
            pref.save()
            '''self.loadSensors()'''
        return True
        
    def about(self):
        QtWidgets.QMessageBox.about(self, "About MolonaViz",
                "The <b>MolonaViz</b> software is copyrighted by Geosciences Research Center of MINES ParisTech.")

    def updateStatus(self):
        isValid = self.currentStudy.isValid()
        if isValid:
            self.setWindowTitle("MolonaViz - %s" % (self.currentStudy.name))
        else:
            self.setWindowTitle("MolonaViz")
        self.actionSave_As_Study.setEnabled(isValid)
        self.actionEdit_Study.setEnabled(isValid)
        self.actionImport_Point.setEnabled(isValid)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    
    # Create thread that will listen on the other end of the queue, and send the text to the textedit in our application
    thread = QThread()
    my_receiver = MyReceiver(mainWin.queue)
    my_receiver.mysignal.connect(mainWin.append_text)
    my_receiver.moveToThread(thread)
    thread.started.connect(my_receiver.run)
    thread.start()
        
    sys.exit(app.exec_())
    
    
