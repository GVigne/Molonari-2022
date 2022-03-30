from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import mdi_rc
import pandas as pd

class DataFrameModel(QtCore.QAbstractTableModel):

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self._dataframe.values[index.row()][index.column()]))
            # other roles (i.e. : editing) look at :
            # https://stackoverflow.com/questions/58234343/display-pandas-dataframe-in-tableview-in-pyqt5-where-column-is-set-as-index
        return QtCore.QVariant()

class MdiChild(QtWidgets.QWidget):
    sequenceNumber = 1

    def __init__(self):
        super(MdiChild, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.tableView = QtWidgets.QTableView(self)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        
        self.graphView = pg.PlotWidget()

        self.layoutVertical = QtWidgets.QVBoxLayout(self)
        self.layoutVertical.addWidget(self.tableView)
        self.layoutVertical.addWidget(self.graphView)

    def loadCsvPanda(self, fileName):
        with open(fileName, "r") as fileInput:
            df = pd.read_csv(fileInput, skiprows=0, header=1)
            model = DataFrameModel(df)
            self.tableView.setModel(model)
            # Plot index (0) and temperature (2)
            # df = df.iloc[3:]  # Doesn't work !
            # Why ? https://stackoverflow.com/questions/16396903/delete-the-first-three-rows-of-a-dataframe-in-pandas 
            self.graphView.plot(df.iloc[:,0],df.iloc[:,2])

    def loadFile(self, fileName):
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.warning(self, "MDI",
                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return False

        self.loadCsvPanda(fileName)
        self.setCurrentFile(fileName)

        return True

    def setCurrentFile(self, fileName):
        self.curFile = QtCore.QFileInfo(fileName).canonicalFilePath()
        self.setWindowTitle(self.userFriendlyCurrentFile())
                            
    def currentFile(self):
        return self.curFile
    
    def userFriendlyCurrentFile(self):
        return self.strippedName(self.curFile)
    
    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()
    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.mdiArea = QtWidgets.QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtWidgets.QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("Molonari")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        if fileName:
            existing = self.findMdiChild(fileName)
            if existing:
                self.mdiArea.setActiveSubWindow(existing)
                return

            child = self.createMdiChild()
            if child.loadFile(fileName):
                self.statusBar().showMessage("File loaded", 2000)
                child.show()
            else:
                child.close()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About Molonari",
                "The <b>Molonari</b> software is strongly copyrigthed by Agnes RIVIERE")

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyCurrentFile())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def createMdiChild(self):
        child = MdiChild()
        self.mdiArea.addSubWindow(child)

        return child

    def createActions(self):
        self.openAct = QtWidgets.QAction(QtGui.QIcon(':/images/open.png'), "&Open...", self,
                shortcut=QtGui.QKeySequence.Open, statusTip="Open an existing file",
                triggered=self.open)

        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut=QtGui.QKeySequence.Quit,
                statusTip="Exit the application",
                triggered=QtWidgets.QApplication.instance().closeAllWindows)

        self.closeAct = QtWidgets.QAction("Cl&ose", self,
                statusTip="Close the active window",
                triggered=self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QtWidgets.QAction("Close &All", self,
                statusTip="Close all the windows",
                triggered=self.mdiArea.closeAllSubWindows)

        self.tileAct = QtWidgets.QAction("&Tile", self, statusTip="Tile the windows",
                triggered=self.mdiArea.tileSubWindows)

        self.cascadeAct = QtWidgets.QAction("&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.mdiArea.cascadeSubWindows)

        self.nextAct = QtWidgets.QAction("Ne&xt", self, shortcut=QtGui.QKeySequence.NextChild,
                statusTip="Move the focus to the next window",
                triggered=self.mdiArea.activateNextSubWindow)

        self.previousAct = QtWidgets.QAction("Pre&vious", self,
                shortcut=QtGui.QKeySequence.PreviousChild,
                statusTip="Move the focus to the previous window",
                triggered=self.mdiArea.activatePreviousSubWindow)

        self.separatorAct = QtWidgets.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtWidgets.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtWidgets.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtWidgets.QApplication.instance().aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addSeparator()
        action = self.fileMenu.addAction("Switch layout direction")
        action.triggered.connect(self.switchLayoutDirection)
        self.fileMenu.addAction(self.exitAct)

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.openAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        settings = QtCore.QSettings('MPT', 'Molonari Software')
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings('MPT', 'Molonari Software')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.mdiArea.subWindowList():
            if window.widget().currentFile() == canonicalFilePath:
                return window
        return None

    def switchLayoutDirection(self):
        if self.layoutDirection() == QtCore.Qt.LeftToRight:
            QtWidgets.QApplication.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            QtWidgets.QApplication.setLayoutDirection(QtCore.Qt.LeftToRight)

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())