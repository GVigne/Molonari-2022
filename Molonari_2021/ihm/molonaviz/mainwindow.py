import sys, os, shutil
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from queue import Queue

from study import Study
from point import Point
from subwindow import SubWindow
from dialogstudy import DialogStudy
from dialogfindstudy import DialogFindStudy
from dialogimportpoint import DialogImportPoint
from dialogaboutus import DialogAboutUs
from queuethread import *
from usefulfonctions import *
from errors import *


From_MainWindow = uic.loadUiType(os.path.join(os.path.dirname(__file__),"mainwindow.ui"))[0]

class MainWindow(QtWidgets.QMainWindow,From_MainWindow):
    
    def __init__(self):
        # Call constructor of parent classes
        super(MainWindow, self).__init__()
        QtWidgets.QMainWindow.__init__(self)
        
        self.setupUi(self)
        
        # Create Queue and redirect sys.stdout to this queue
        self.queue = Queue()
        sys.stdout = WriteStream(self.queue)
        # sys.stderr = WriteStream(self.queue)
        print("MolonaViz - 0.0.2beta - 2022-03-29")

        self.mdi = QtWidgets.QMdiArea()
        self.setCentralWidget(self.mdi)
        self.mdi.setTabsMovable(True)
        self.mdi.setTabsClosable(True)

        self.currentStudy = None

        self.pSensorModel = QtGui.QStandardItemModel()
        self.treeViewPressureSensors.setModel(self.pSensorModel)
        self.treeViewPressureSensors.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.shaftModel = QtGui.QStandardItemModel()
        self.treeViewShafts.setModel(self.shaftModel)
        self.treeViewShafts.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.thermometersModel = QtGui.QStandardItemModel()
        self.treeViewThermometers.setModel(self.thermometersModel)
        self.treeViewThermometers.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.pointModel = QtGui.QStandardItemModel()
        self.treeViewDataPoints.setModel(self.pointModel)
        self.treeViewDataPoints.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.menubar.setNativeMenuBar(False) #Permet d'afficher la barre de menu dans la fenêtre
        self.setWindowFlags(QtCore.Qt.WindowTitleHint)
        self.setWindowTitle("MolonaViz")

        self.actionQuit_MolonaViz.triggered.connect(self.exitApp)
        self.actionAbout_MolonaViz.triggered.connect(self.aboutUs)
        self.actionOpen_Study.triggered.connect(self.openStudy)
        self.actionCreate_Study.triggered.connect(self.createStudy)
        self.actionClose_Study.triggered.connect(self.closeStudy)
        self.actionImport_Point.triggered.connect(self.importPoint)
        self.actionOpen_Point.triggered.connect(self.openPointTimer)
        self.actionRemove_Point.triggered.connect(self.removePoint)
        self.actionSwitch_To_Tabbed_View.triggered.connect(self.switchToTabbedView)
        self.actionSwitch_To_SubWindow_View.triggered.connect(self.switchToSubWindowView)
        self.actionSwitch_To_Cascade_View.triggered.connect(self.switchToCascadeView)
        
        self.actionData_Points.triggered.connect(self.changeDockPointsStatus)

        self.treeViewDataPoints.doubleClicked.connect(self.openPointTimer)
        self.treeViewDataPoints.clicked.connect(self.actualizeMenuPoints)
        self.treeViewDataPoints.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeViewDataPoints.customContextMenuRequested.connect(self.menuContextTree)

        self.actionRemove_Point.setEnabled(False)
        self.actionImport_Point.setEnabled(False)
        self.actionOpen_Point.setEnabled(False)

        self.pushButtonClear.clicked.connect(self.clearText)

        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.openPoint)

        #On adapte la taille de la fenêtre principale à l'écran
        # screenSize = QtWidgets.QDesktopWidget().screenGeometry(-1)
        # self.setGeometry(screenSize)
        # self.setMaximumWidth(self.geometry().width())
        # self.setMaximumHeight(self.geometry().height())
        
        #On ouvre automatiquement une étude
        self.currentStudy = Study(rootDir="../../studies/study_2022")
        self.openStudy()
    
    def appendText(self,text):
        self.textEditApplicationMessages.moveCursor(QtGui.QTextCursor.End)
        self.textEditApplicationMessages.insertPlainText(text)
    
    def clearText(self):
        self.textEditApplicationMessages.clear()
        print("MolonaViz - 0.0.2beta - 2022-03-29")
    
    def exitApp(self):
        QtWidgets.QApplication.quit()
    
    def aboutUs(self):
        dlg = DialogAboutUs()
        dlg.exec_()
    
    def changeDockPointsStatus(self):
        if self.actionData_Points.isChecked() == True :
            self.dockDataPoints.hide()
            self.actionData_Points.setChecked(False)
        else :
            pass

    def menuContextTree(self, position):

        menu = QtWidgets.QMenu()
        menu.addAction(self.actionImport_Point)
        menu.addAction(self.actionOpen_Point)
        menu.addAction(self.actionRemove_Point)

        self.actualizeMenuPoints()

        menu.exec_(self.treeViewDataPoints.mapToGlobal(position))
    
    def actualizeMenuPoints(self):

        if len(self.treeViewDataPoints.selectedIndexes()) != 0:
            if self.treeViewDataPoints.selectedIndexes()[0].parent().data(QtCore.Qt.UserRole) == None:
                pointname = self.treeViewDataPoints.selectedIndexes()[0].data(QtCore.Qt.UserRole).getName()
            else:
                pointname = self.treeViewDataPoints.selectedIndexes()[0].parent().data(QtCore.Qt.UserRole).getName()
            self.actionOpen_Point.setEnabled(True)
            self.actionOpen_Point.setText(f"Open {pointname}")
            self.actionRemove_Point.setEnabled(True)
            self.actionRemove_Point.setText(f"Remove {pointname}")

        else:
            self.actionOpen_Point.setEnabled(False)
            self.actionOpen_Point.setText("Open Point")
            self.actionRemove_Point.setEnabled(False)
            self.actionRemove_Point.setText("Remove Point")


    def createStudy(self):
        dlg = DialogStudy()
        res = dlg.exec_()
        errors = False
        if res == QtWidgets.QDialog.Accepted:
            try :
                self.currentStudy = dlg.setStudy()
                self.currentStudy.saveStudyToText()
                try :
                    self.openStudy() #on ouvre automatiquement une étude qui vient d'être créée
                except LoadingError as e :
                    print(e)
                    print('Study creation aborted')
                    displayCriticalMessage('Study creation aborted', f'An error occured \n Please check "Application messages" for further information')
                    shutil.rmtree(self.currentStudy.getRootDir())
                    self.currentStudy = None
                    return None
                except Exception as e :
                    try :
                        print(e)
                    except :
                        print('Unknown error')
                    print('Study creation aborted')
                    displayCriticalMessage('Study creation aborted', f'An error occured. Please check "Application messages" for further information')
                    shutil.rmtree(self.currentStudy.getRootDir())
                    self.currentStudy = None
                    return None
            except EmptyFieldError as e:
                displayCriticalMessage(f"{str(e)} \nPlease try again")
                self.createStudy()
            except FileNotFoundError as e:
                displayCriticalMessage(f"{str(e)} \nPlease try again")
                self.createStudy()
            except Exception as error:
                print(f'error : {str(error)}')
                self.currentStudy = None
            print("New study successfully created")

    def openStudy(self):
        if self.currentStudy == None : #si on ne vient pas de créer une étude
            dlg = DialogFindStudy()
            res = dlg.exec_()
            if res == QtWidgets.QDialog.Accepted:
                try :
                    self.currentStudy = Study(rootDir=dlg.getRootDir())
                except FileNotFoundError as e:
                    displayCriticalMessage(f"{str(e)} \nPlease try again")
                    self.openStudy()
            else :
                return None
        try :
            self.currentStudy.loadStudyFromText() #charge le nom de l'étude et son sensorDir
            self.setWindowTitle(f'MolonaViz – {self.currentStudy.getName()}')
        except TextFileError as e:
            infoMessage = f"You might have selected the wrong root directory \n\nIf not, please see the Help section "
            displayCriticalMessage(str(e), infoMessage)
            self.currentStudy = None
            return None
        try :
            self.currentStudy.loadPressureSensors(self.pSensorModel)
        except Exception :
            raise LoadingError("pressure sensors")
        try : 
            self.currentStudy.loadShafts(self.shaftModel)
        except Exception :
            raise LoadingError("shafts")
        try :
            self.currentStudy.loadThermometers(self.thermometersModel)
        except Exception :
            raise LoadingError("thermometers")
        try :
            self.currentStudy.loadPoints(self.pointModel)
        except Exception :
            raise LoadingError('points')

        #le menu point n'est pas actif tant qu'aucune étude n'est ouverte et chargée
        self.menuPoint.setEnabled(True)
        self.actionClose_Study.setEnabled(True)
        self.actionImport_Point.setEnabled(True)

        #on n'autorise pas l'ouverture ou la création d'une étude s'il y a déjà une étude ouverte
        self.actionOpen_Study.setEnabled(False) 
        self.actionCreate_Study.setEnabled(False)
    
    def closeStudy(self):

        #On ferme tous les points ouverts
        openedSubWindows = self.mdi.subWindowList()
        for subWin in openedSubWindows:
            subWin.close()

        #On remet les modèles à zéro
        self.pSensorModel.clear()
        self.shaftModel.clear()
        self.thermometersModel.clear()
        self.pointModel.clear()

        self.setWindowTitle("MolonaViz")

        self.menuPoint.setEnabled(False)
        self.actionClose_Study.setEnabled(False)
        self.actionImport_Point
        self.actionOpen_Study.setEnabled(True) 
        self.actionCreate_Study.setEnabled(True)
        self.actionImport_Point.setEnabled(False)
        self.actionRemove_Point.setText(f"Remove Point")
        self.actionRemove_Point.setEnabled(False)
        self.actionOpen_Point.setText(f"Open Point")
        self.actionOpen_Point.setEnabled(False)

        self.currentStudy = None

    def importPoint(self):
        point = Point()
        dlg = DialogImportPoint()
        res = dlg.exec()
        if res == QtWidgets.QDialog.Accepted:
            try :
                name, infofile, prawfile, trawfile, noticefile, configfile  = dlg.getPointInfo()
                point = self.currentStudy.addPoint(name, infofile, prawfile, trawfile, noticefile, configfile) 
                point.loadPoint(self.pointModel)
            except Exception as e :
                print(f"Point import aborted : {str(e)}")
                displayCriticalMessage('Point import aborted', f"Couldn't import point due to the following error : \n{str(e)}")
           
    def openPointTimer(self):
        point = self.treeViewDataPoints.selectedIndexes()[0].data(QtCore.Qt.UserRole)
        if point == None:
            point = self.treeViewDataPoints.selectedIndexes()[0].parent().data(QtCore.Qt.UserRole)
        print(f"Opening {point.getName()} ...")
        self.timer.start(200)

    def openPoint(self):
        point = self.treeViewDataPoints.selectedIndexes()[0].data(QtCore.Qt.UserRole)
        if point == None:
            point = self.treeViewDataPoints.selectedIndexes()[0].parent().data(QtCore.Qt.UserRole)

        if point.getName() not in [openedSubwindow.getName() for openedSubwindow in self.mdi.subWindowList()]:
            subWin = SubWindow(point, self.currentStudy)
            subWin.setPointWidget()

            if self.mdi.viewMode() == QtWidgets.QMdiArea.SubWindowView and not self.actionSwitch_To_Cascade_View.isEnabled():
                self.mdi.addSubWindow(subWin)
                subWin.show()
                self.mdi.cascadeSubWindows()

            elif self.mdi.viewMode() == QtWidgets.QMdiArea.SubWindowView and not self.actionSwitch_To_SubWindow_View.isEnabled():
                self.mdi.addSubWindow(subWin)
                subWin.show()
                self.mdi.tileSubWindows()

            elif self.mdi.viewMode() == QtWidgets.QMdiArea.TabbedView:
                self.switchToSubWindowView()
                self.mdi.addSubWindow(subWin)
                subWin.show()
                self.mdi.tileSubWindows()
                self.switchToTabbedView()

            print(" ==> done")

        else:
            print(f"{point.getName()} is already open")
        
    def removePoint(self):
        title = "Warning ! You are about to delete a point"
        message = "All point data will be deleted. Are you sure you want to proceed ?"
        msgBox = displayConfirmationMessage(title, message)
        
        if msgBox == QtWidgets.QMessageBox.Ok:
            point = self.treeViewDataPoints.selectedIndexes()[0].data(QtCore.Qt.UserRole)
            if point == None:
                point = self.treeViewDataPoints.selectedIndexes()[0].parent().data(QtCore.Qt.UserRole)
            pointname = point.getName()
            pointItem = self.pointModel.findItems(pointname)[0]
            
            point.delete() #supprime le dossier du rootDir

            pointIndex = self.pointModel.indexFromItem(pointItem)
            self.pointModel.removeRow(pointIndex.row()) #supprime l'item du model

            #On ferme la fenêtre associée au point qu'on enlève
            openedSubWindows = self.mdi.subWindowList()
            for subWin in openedSubWindows:
                if subWin.getName() == pointname:
                    subWin.close()
            
            print(f"{pointname} successfully removed")

            if len(self.treeViewDataPoints.selectedIndexes()) != 0:
                self.actionOpen_Point.setEnabled(True)
                self.actionOpen_Point.setText(f"Open {pointname}")
                self.actionRemove_Point.setEnabled(True)
                self.actionRemove_Point.setText(f"Remove {pointname}")  
            else:
                self.actionRemove_Point.setText(f"Remove Point")
                self.actionOpen_Point.setText(f"Open Point")
                self.actionOpen_Point.setEnabled(False)
                self.actionRemove_Point.setEnabled(False)

        else : 
            #displayInfoMessage("Point removal aborted")
            print("Point removal aborted")

    def switchToTabbedView(self):
        self.mdi.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.actionSwitch_To_Tabbed_View.setEnabled(False)
        self.actionSwitch_To_SubWindow_View.setEnabled(True)
        self.actionSwitch_To_Cascade_View.setEnabled(True)

    def switchToSubWindowView(self):
        self.mdi.setViewMode(QtWidgets.QMdiArea.SubWindowView)
        self.mdi.tileSubWindows()
        self.actionSwitch_To_Tabbed_View.setEnabled(True)
        self.actionSwitch_To_SubWindow_View.setEnabled(False)
        self.actionSwitch_To_Cascade_View.setEnabled(True)

    def switchToCascadeView(self):
        self.mdi.setViewMode(QtWidgets.QMdiArea.SubWindowView)
        self.mdi.cascadeSubWindows()
        self.actionSwitch_To_Tabbed_View.setEnabled(True)
        self.actionSwitch_To_SubWindow_View.setEnabled(True)
        self.actionSwitch_To_Cascade_View.setEnabled(False)
        


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle('windows')
    app.setWindowIcon(QtGui.QIcon("MolonavizIcon.png")) #à modifier quand l'icone est prête
    mainWin = MainWindow()
    mainWin.showMaximized()

    # Create thread that will listen on the other end of the queue, and send the text to the textedit in our application
    thread = QtCore.QThread()
    my_receiver = MyReceiver(mainWin.queue)
    my_receiver.mysignal.connect(mainWin.appendText)
    my_receiver.moveToThread(thread)
    thread.started.connect(my_receiver.run)
    thread.start()

    sys.exit(app.exec_())