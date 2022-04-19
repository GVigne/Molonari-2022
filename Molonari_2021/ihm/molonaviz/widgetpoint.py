import sys
import os
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlQueryModel, QSqlDatabase, QSqlQuery
import pandas as pd
from sympy import true
from pandasmodel import PandasModel
from dialogcleanup import DialogCleanup
from dialogcompute import DialogCompute
from point import Point
from study import Study
from mplcanvas import MplCanvas, MplCanvasHisto, MplCanvaHeatFluxes, MplTempbydepth
from compute import Compute
import numpy as np
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from usefulfonctions import *
from dialogreset import DialogReset
from MoloModel import MoloModel, PressureDataModel, TemperatureDataModel, SolvedTemperatureModel,HeatFluxesModel
from MoloView import MoloView,MoloView1D,MoloView2D,PressureView, TemperatureView,UmbrellaView,TempDepthView,TempMapView,AdvectiveFlowView,ConductiveFlowView,TotalFlowView

From_WidgetPoint = uic.loadUiType(os.path.join(os.path.dirname(__file__),"widgetpoint.ui"))[0]

class WidgetPoint(QtWidgets.QWidget,From_WidgetPoint):
    
    def __init__(self, point: Point, study: Study):
        # Call constructor of parent classes
        super(WidgetPoint, self).__init__()
        QtWidgets.QWidget.__init__(self)
        
        self.setupUi(self)
        
        self.point = point
        self.study = study
        
        self.computeEngine = Compute(self.point)

        # Link every button to their function

        self.pushButtonReset.clicked.connect(self.reset)
        self.pushButtonCleanUp.clicked.connect(self.cleanup)
        self.pushButtonCompute.clicked.connect(self.compute)
        self.checkBoxRaw_Data.stateChanged.connect(self.checkbox)
        self.pushButtonRefreshBins.clicked.connect(self.refreshbins)
        self.horizontalSliderBins.valueChanged.connect(self.label_update)
        self.tabWidget.setCurrentIndex(3)

        #TO REMOVE
        self.pointDir = self.point.getPointDir()
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("molonari_slqdb.sqlite")
        self.con.open()
        self.point.name="Point034" #Needs to be changed

        self.setPressureAndTemperatureModels()
        self.setDataPlots()
        self.setResultsPlots()

    def setInfoTab(self):
        # Set the "Infos" tab
            #Installation
        self.labelSchema.setPixmap(QPixmap(self.pointDir + "/info_data" + "/config.png"))
        self.labelSchema.setAlignment(QtCore.Qt.AlignHCenter)

        #This allows the image to take the entire size of the widget, however it will be misshapen
        # self.labelSchema.setScaledContents(True)
        # self.labelSchema.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Ignored)
            #Notice
        file = open(self.pointDir + "/info_data" + "/notice.txt", encoding="charmap", errors="surrogateescape")
        notice = file.read()
        self.plainTextEditNotice.setPlainText(notice)
        file.close()
            #Infos
        infoFile = self.pointDir + "/info_data" + "/info.csv"
        dfinfo = pd.read_csv(infoFile, header=None)
        self.infosModel = PandasModel(dfinfo)
        self.tableViewInfos.setModel(self.infosModel)
        self.tableViewInfos.horizontalHeader().hide()
        self.tableViewInfos.verticalHeader().hide()
        self.tableViewInfos.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tableViewInfos.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

    def setPressureAndTemperatureModels(self):
        # Set the Temperature and Pressure models
        self.currentdata = "processed"
        if self.checkBoxRaw_Data.isChecked():
            self.currentdata = "raw"

        select_query = self.build_data_queries(full_query=True)
        self.currentDataModel = QSqlQueryModel()
        self.currentDataModel.setQuery(select_query)
        self.tableViewDataArray.setModel(self.currentDataModel)

    def setWidgetInfos(self):
        pointName = self.point.getName()
        pointPressureSensor = self.point.getPressureSensor()
        pointShaft = self.point.getShaft()

        self.setWindowTitle(pointName)
        self.lineEditSensor.setText(pointPressureSensor)
        self.lineEditShaft.setText(pointShaft)
    
    
    def checkbox(self):
        """
        Change the type of data displayed (raw or processed) when the checkbox changes state.
        """
        if self.checkBoxRaw_Data.isChecked():
            self.currentdata = "raw"
        else :
            self.currentdata = "processed"

        select_query = self.build_data_queries(full_query=True) #Query changes according to self.currentdata
        self.currentDataModel = QSqlQueryModel()
        self.currentDataModel.setQuery(select_query)
        self.tableViewDataArray.setModel(self.currentDataModel)

        # if self.currentdata == "processed"
        #     self.dftemp = readCSVWithDates(self.TemperatureDir)
        #     self.dfpress = readCSVWithDates(self.PressureDir)
        #     self.currentTemperatureModel.setData(self.dftemp)
        #     self.currentPressureModel.setData(self.dfpress)
        
        # elif self.currentdata == "raw":
        #     self.dftemp = pd.read_csv(self.TemperatureDir, skiprows=1)
        #     self.dfpress = pd.read_csv(self.PressureDir, skiprows=1)
        #     self.currentTemperatureModel.setData(self.dftemp)
        #     self.currentPressureModel.setData(self.dfpress)  


    def reset(self):
        #This needs to be redone from scratch to be compatible with the SQL database
        return
        dlg = DialogReset()
        res = dlg.exec_()
        if res == QtWidgets.QDialog.Accepted:
            print("Resetting data...")
            self.point.processData(self.study.getSensorDir())
            self.point.reset()
            #On actualise les modèles
            if self.checkBoxRaw_Data.isChecked():
                self.dfpress = pd.read_csv(self.PressureDir, skiprows=1)
                self.dftemp = pd.read_csv(self.TemperatureDir, skiprows=1)
            else:
                self.dfpress = readCSVWithDates(self.PressureDir)
                self.dftemp = readCSVWithDates(self.TemperatureDir)   
            self.currentTemperatureModel.setData(self.dftemp)
            self.currentPressureModel.setData(self.dfpress)
            self.graphpress.update_(self.dfpress)
            self.graphtemp.update_(self.dftemp, dfpressure=self.dfpress)

            self.directmodeliscomputed = False
            self.MCMCiscomputed = False
            ##Clear des layouts :
            clearLayout(self.vboxwaterdirect)
            clearLayout(self.vboxwaterMCMC)
            clearLayout(self.vboxfluxesdirect)
            clearLayout(self.vboxfluxesMCMC)
            clearLayout(self.vboxfrisetempdirect)
            clearLayout(self.vboxfrisetempMCMC)
            clearLayout(self.vboxintertempdirect)
            clearLayout(self.vboxintertempMCMC)
            clearLayout(self.vboxsolvedtempdirect)
            clearLayout(self.vboxsolvedtempMCMC)
            clearLayout(self.vboxhistos)
            self.tableViewBestParams.setModel(PandasModel())

            self.setResultsPlots()
            print("Data successfully reset !")
            


    def cleanup(self):
        #This needs to be redone from scratch to be compatible with the SQL database
        return
        if self.currentdata == "raw":
            print("Please clean-up your processed data. Click again on the raw data box")
        else:
            dlg = DialogCleanup()
            res = dlg.exec_()
            if res == QtWidgets.QDialog.Accepted:
                script = dlg.getScript()
                print("Cleaning data...")
                try :
                    self.dftemp, self.dfpress = self.point.cleanup(script, self.dftemp, self.dfpress)
                    print("Data successfully cleaned !...")
                    
                    #On actualise les modèles
                    self.currentTemperatureModel.setData(self.dftemp)
                    self.currentPressureModel.setData(self.dfpress)
                    self.graphpress.update_(self.dfpress)
                    self.graphtemp.update_(self.dftemp, dfpressure=self.dfpress)
                    print("Plots successfully updated")
                except Exception as e :
                    print(e, "==> Clean-up aborted")
                    displayCriticalMessage("Error : Clean-up aborted", f'Clean-up was aborted due to the following error : \n"{str(e)}" ' )
    

    def compute(self):
        return
        
        sensorDir = self.study.getSensorDir()

        dlg = DialogCompute()
        res = dlg.exec()

        if res == 10 : #Direct Model
            params, nb_cells = dlg.getInputDirectModel()
            # compute = Compute(self.point)
            # compute.computeDirectModel(params, nb_cells, sensorDir)
            self.computeEngine.computeDirectModel(params, nb_cells, sensorDir)

            self.setDataFrames('DirectModel')
            self.comboBoxDepth.clear()
            for depth in self.dfdepths.values.tolist():
                self.comboBoxDepth.insertItem(len(self.dfdepths.values.tolist()), str(depth))

            if self.directmodeliscomputed :
                print('Direct Model is computed')
                self.graphwaterdirect.update_(self.dfwater)
                self.graphsolvedtempdirect.update_(self.dfsolvedtemp, self.dfdepths)
                self.graphintertempdirect.update_(self.dfsolvedtemp, self.dfdepths)
                self.graphfluxesdirect.update_(self.dfadvec, self.dfconduc, self.dftot, self.dfdepths)
                self.parapluies.update_(self.dfsolvedtemp, self.dfdepths)
                self.paramsModel.setData(self.dfparams)
                print("Model successfully updated !")

            else :

                #Flux d'eau
                clearLayout(self.vboxwaterdirect)
                self.plotWaterFlowsDirect(self.dfwater)

                #Flux d'énergie
                clearLayout(self.vboxfluxesdirect)
                self.plotFriseHeatFluxesDirect(self.dfadvec, self.dfconduc, self.dftot, self.dfdepths)

                #Frise de température
                clearLayout(self.vboxfrisetempdirect)
                self.plotFriseTempDirect(self.dfsolvedtemp, self.dfdepths)
                #Parapluies
                clearLayout(self.vboxsolvedtempdirect)
                self.plotParapluies(self.dfsolvedtemp, self.dfdepths)

                #Température à l'interface
                clearLayout(self.vboxintertempdirect)
                self.plotInterfaceTempDirect(self.dfsolvedtemp, self.dfdepths)
                
                # Les paramètres utilisés
                self.setParamsModel(self.dfparams)

                self.directmodeliscomputed = True
                print("Model successfully created !")

    
        if res == 1 : #MCMC
            nb_iter, priors, nb_cells, quantiles = dlg.getInputMCMC()
            self.nb_quantiles = len(quantiles)
            with open(self.MCMCDir+"/nb_quantiles", "w") as f:
                f.write(str(self.nb_quantiles))
                f.close()
            # compute = Compute(self.point)
            # compute.computeMCMC(nb_iter, priors, nb_cells, sensorDir)
            self.computeEngine.MCMCFinished.connect(self.onMCMCFinished)
            self.computeEngine.computeMCMC(nb_iter, priors, nb_cells, sensorDir, quantiles)

    def onMCMCFinished(self):

        self.setDataFrames('MCMC')

        self.comboBoxDepth.clear()
        for depth in self.dfdepths.values.tolist():
            self.comboBoxDepth.insertItem(len(self.dfdepths.values.tolist()), str(depth))

        if self.MCMCiscomputed :
            print('MCMC is computed')
            self.graphwaterMCMC.update_(self.dfwater)
            self.graphsolvedtempMCMC.update_(self.dfsolvedtemp, self.dfdepths)
            self.graphintertempMCMC.update_(self.dfintertemp, self.dfdepths, nb_quantiles=self.nb_quantiles)
            self.graphfluxesMCMC.update_(self.dfadvec, self.dfconduc, self.dftot, self.dfdepths)
            self.histos.update_(self.dfallparams)
            self.parapluiesMCMC.update_(self.dfsolvedtemp, self.dfdepths)
            self.BestParamsModel.setData(self.dfbestparams)
            print("Model successfully updated !")

        else :

            #Flux d'eau
            clearLayout(self.vboxwaterMCMC)
            self.plotWaterFlowsMCMC(self.dfwater)

            #Flux d'énergie
            clearLayout(self.vboxfluxesMCMC)
            self.plotFriseHeatFluxesMCMC(self.dfadvec, self.dfconduc, self.dftot, self.dfdepths)

            #Frise de température
            clearLayout(self.vboxfrisetempMCMC)
            self.plotFriseTempMCMC(self.dfsolvedtemp, self.dfdepths)
            #Parapluies
            clearLayout(self.vboxsolvedtempMCMC)
            self.plotParapluiesMCMC(self.dfsolvedtemp, self.dfdepths)
            #Température à l'interface
            clearLayout(self.vboxintertempMCMC)
            self.plotInterfaceTempMCMC(self.dfintertemp, self.dfdepths, self.nb_quantiles)

            #Histogrammes
            clearLayout(self.vboxhistos)
            self.histos(self.dfallparams)
            #Les meilleurs paramètres
            self.setBestParamsModel(self.dfbestparams)

            self.MCMCiscomputed = True
            print("Model successfully created !")

    def refreshbins(self):
        if self.MCMCiscomputed:
            bins = self.horizontalSliderBins.value()
            self.histos.refresh(bins)
        else :
            print("Please run the MCMC first")

    def setDataPlots(self):
        #Pressure :
        select_pressure = self.build_data_queries(field ="Pressure")
        self.pressuremodel = PressureDataModel([select_pressure])
        self.graphpress = PressureView(self.pressuremodel, time_dependent=True,ylabel="Pression différentielle (m)")
        self.toolbarPress = NavigationToolbar(self.graphpress, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxPress.setLayout(vbox)
        vbox.addWidget(self.graphpress)
        vbox.addWidget(self.toolbarPress)

        self.pressuremodel.exec()

        #Temperatures :
        select_temp = self.build_data_queries(field ="Temp")
        self.tempmodel = TemperatureDataModel([select_pressure])
        self.graphtemp = TemperatureView(self.pressuremodel, time_dependent=True,ylabel="Pression différentielle (m)")
        # self.graphtemp = MplCanvas(temp_array, "temperature")
        self.toolbarTemp = NavigationToolbar(self.graphtemp, self)
        vbox2 = QtWidgets.QVBoxLayout()
        self.groupBoxTemp.setLayout(vbox2)
        vbox2.addWidget(self.graphtemp)
        vbox2.addWidget(self.toolbarTemp)

        self.tempmodel.exec()
    
    def setResultsPlots(self):
        """
        Display the results in the corresponding tabs.
        """
        self.vboxwaterdirect = QtWidgets.QVBoxLayout()
        self.groupBoxWaterDirect.setLayout(self.vboxwaterdirect)
        self.vboxwaterMCMC = QtWidgets.QVBoxLayout()
        self.groupBoxWaterMCMC.setLayout(self.vboxwaterMCMC)
        
        if self.computation_type() is not None:
            self.plotFluxes()
            self.plotTemperatureMap()
            
            #Les paramètres
            # self.setParamsModel()
            self.plotHistos()  
        else:
            self.vboxwaterdirect.addWidget(QtWidgets.QLabel("No model has been computed yet"))
            self.vboxfluxesdirect.addWidget(QtWidgets.QLabel("No model has been computed yet"))
            self.vboxfrisetempdirect.addWidget(QtWidgets.QLabel("No model has been computed yet"))
            self.vboxintertempdirect.addWidget(QtWidgets.QLabel("No model has been computed yet"))
            self.vboxsolvedtempdirect.addWidget(QtWidgets.QLabel("No model has been computed yet"))
        

    def setDataFrames(self, mode:str):

        if mode == 'DirectModel':
            self.dfwater = readCSVWithDates(self.directmodelDir + "/solved_flows.csv")
            self.dfdepths = pd.read_csv(self.directdepthsdir)
            self.dfsolvedtemp = readCSVWithDates(self.directmodelDir + "/solved_temperatures.csv")
            #self.dfintertemp = self.dfsolvedtemp[self.dfsolvedtemp.columns[0:2]]
            #C'EST ICI QU'ON AJOUTE LE CHOIX DE LA PROFONDEUR ?
            self.dfadvec = readCSVWithDates(self.directmodelDir + "/advective_flux.csv")
            self.dfconduc = readCSVWithDates(self.directmodelDir + "/conductive_flux.csv")
            self.dftot = readCSVWithDates(self.directmodelDir + "/total_flux.csv")
            self.dfparams = pd.read_csv(self.directmodelDir + "/params.csv")
            self.dfparams = self.dfparams[self.dfparams.columns[1:]].round(decimals=3)

        elif mode == 'MCMC':
            self.dfwater = readCSVWithDates(self.MCMCDir + "/MCMC_flows_quantiles.csv")
            self.dfsolvedtemp = readCSVWithDates(self.MCMCDir + "/solved_temperatures.csv")
            self.dfdepths = pd.read_csv(self.MCMCdepthsdir)
            self.dfintertemp = readCSVWithDates(self.MCMCDir + "/MCMC_temps_quantiles.csv")
            #C'EST ICI QU'ON AJOUTE LE CHOIX DE LA PROFONDEUR ?
            self.dfallparams = pd.read_csv(self.MCMCDir + "/MCMC_all_params.csv")
            self.dfadvec = readCSVWithDates(self.MCMCDir + "/advective_flux.csv")
            self.dfconduc = readCSVWithDates(self.MCMCDir + "/conductive_flux.csv")
            self.dftot = readCSVWithDates(self.MCMCDir + "/total_flux.csv")
            self.dfbestparams = pd.read_csv(self.MCMCDir + "/MCMC_best_params.csv")
            self.dfbestparams = self.dfbestparams[self.dfbestparams.columns[1:]].round(decimals=3)
            #print(self.dfbestparams)
            with open(self.MCMCDir+"/nb_quantiles", "r") as f:
                self.nb_quantiles = int(f.read())
                f.close()

    def plotWaterFlows(self):
        select_flows = self.build_data_queries(field="Temp")
        
        

        self.graphwaterdirect = MplCanvas(flows_array, "water flow")
        self.toolbarwaterdirect = NavigationToolbar(self.graphwaterdirect, self)
        self.vboxwaterdirect.addWidget(self.graphwaterdirect)
        self.vboxwaterdirect.addWidget(self.toolbarwaterdirect)
    
    def plotWaterFlowsDirect(self):
        return

    def plotTemperatureMap(self):
        select_tempmap = self.build_result_queries(result_type="Temperature",option="2DMap")
        self.tempmap_model = SolvedTemperatureModel([select_tempmap])
        date = "" #TO DO
        depth = ""#TO DO
        self.umbrella_view = UmbrellaView(self.tempmap_model, date)
        self.tempmap_view = TempMapView(self.tempmap_model)
        self.depth_view = TempDepthView(self.tempmap_model,depth,title=f"Température à la profondeur {depth} m")
        
        self.toolbarUmbrella = NavigationToolbar(self.umbrella_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxUmbrella.setLayout(vbox)
        vbox.addWidget(self.umbrella_view)
        vbox.addWidget(self.toolbarUmbrella)

        self.toolbarTempMap = NavigationToolbar(self.tempmap_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxTempMap.setLayout(vbox)
        vbox.addWidget(self.tempmap_view)
        vbox.addWidget(self.toolbarTempMap)

        self.toolbarDepth = NavigationToolbar(self.depth_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxTempDepth.setLayout(vbox)
        vbox.addWidget(self.tempmap_view)
        vbox.addWidget(self.toolbarDepth)

    def plotFluxes(self):
        #Plot the heat fluxes
        select_heatfluxes= self.build_result_queries(result_type="2DMap",option="HeatFlows") 
        self.fluxes_model = HeatFluxesModel([select_heatfluxes])
        self.advective_view = AdvectiveFlowView(self.fluxes_model)
        self.conductive_view = ConductiveFlowView(self.fluxes_model)
        self.totalflux_view = TotalFlowView(self.fluxes_model)

        self.toolbarAdvective = NavigationToolbar(self.advective_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxAdvectiveFlux.setLayout(vbox)
        vbox.addWidget(self.advective_view)
        vbox.addWidget(self.toolbarAdvective)

        self.toolbarConductive = NavigationToolbar(self.conductive_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxConductiveFlux.setLayout(vbox)
        vbox.addWidget(self.conductive_view)
        vbox.addWidget(self.toolbarConductive)

        self.toolbarTotalFlux = NavigationToolbar(self.totalflux_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxTotalFlux.setLayout(vbox)
        vbox.addWidget(self.totalflux_view)
        vbox.addWidget(self.toolbarTotalFlux)

    
    def setParamsModel(self):
        pass
    
    def plotHistos(self):
        pass
        
    def plotWaterFlowsMCMC(self, dfwater):
        select_flows1 = self.build_result_queries(result_type="WaterFlux",quantile=0.5)
        select_flows2 = self.build_result_queries(result_type="WaterFlux",quantile=0.05)
        select_flows3 = self.build_result_queries(result_type="WaterFlux",quantile=0.95)
        select_flows1.exec()
        select_flows2.exec()
        select_flows3.exec()
        #This is ugly, it should be changed!
        flows_array = []
        while select_flows1.next():
            flows_array.append([select_flows1.value(0),select_flows1.value(1),select_flows2.value(1),select_flows3.value(1)]) #Date, Flows with 0.5, Flows with 0.05, Flows with 0.95
        flows_array = np.array(flows_array)
        self.graphwaterMCMC = MplCanvas(flows_array, "water flow with quantiles")
        self.toolbarwaterMCMC = NavigationToolbar(self.graphwaterMCMC, self)
        self.vboxwaterMCMC.addWidget(self.graphwaterMCMC)
        self.vboxwaterMCMC.addWidget(self.toolbarwaterMCMC)
    
    def plotFriseHeatFluxesDirect(self, dfadvec, dfconduc, dftot, dfdepths):
        self.graphfluxesdirect = MplCanvaHeatFluxes(dfadvec, dfconduc, dftot, dfdepths)
        self.toolbarfluxesdirect = NavigationToolbar(self.graphfluxesdirect, self)
        self.vboxfluxesdirect.addWidget(self.graphfluxesdirect)
        self.vboxfluxesdirect.addWidget(self.toolbarfluxesdirect)       

    def plotFriseHeatFluxesMCMC(self, dfadvec, dfconduc, dftot, dfdepths):
        self.graphfluxesMCMC = MplCanvaHeatFluxes(dfadvec, dfconduc, dftot, dfdepths)
        self.toolbarfluxesMCMC = NavigationToolbar(self.graphfluxesMCMC, self)
        self.vboxfluxesMCMC.addWidget(self.graphfluxesMCMC)
        self.vboxfluxesMCMC.addWidget(self.toolbarfluxesMCMC)      
    
    def plotFriseTempDirect(self):
        select_temps = self.build_result_queries(result_type ="2DMap", option="Temperature", quantile=0)
        select_temps.exec()
        #This is ugly, it should be changed!
        temps_array = []
        while select_temps.next():
            temps_array.append([select_temps.value(0),select_temps.value(1), select_temps.value(2)]) #Date, Flows, Depths
        temps_array = np.array(temps_array)
        self.graphsolvedtempdirect = MplCanvas(temps_array, "frise")
        self.toolbarsolvedtempdirect = NavigationToolbar(self.graphsolvedtempdirect, self)
        self.vboxfrisetempdirect.addWidget(self.graphsolvedtempdirect)
        self.vboxfrisetempdirect.addWidget(self.toolbarsolvedtempdirect)

    def plotFriseTempMCMC(self):
        select_temps1 = self.build_result_queries(result_type ="2DMap", option="Temperature", quantile=0.05)
        select_temps2 = self.build_result_queries(result_type ="2DMap", option="Temperature", quantile=0.5)
        select_temps3 = self.build_result_queries(result_type ="2DMap", option="Temperature", quantile=0.95)
        select_temps1.exec()
        select_temps2.exec()
        select_temps3.exec()
        #This is ugly, it should be changed!
        temps_array = []
        while select_temps1.next():
            temps_array.append([select_temps1.value(0),select_temps1.value(1),select_temps2.value(1),select_temps3.value(1), select_temps1.value(2)]) #Date, Flows0.05,Flows 0.5, Flows 0.95, Depths
        temps_array = np.array(temps_array)

        self.graphsolvedtempMCMC = MplCanvas(temps_array, "frise")
        self.toolbarsolvedtempMCMC = NavigationToolbar(self.graphsolvedtempMCMC, self)
        self.vboxfrisetempMCMC.addWidget(self.graphsolvedtempMCMC)
        self.vboxfrisetempMCMC.addWidget(self.toolbarsolvedtempMCMC)
    
    def plotInterfaceTempDirect(self, dfintertemp, depths):
        self.graphintertempdirect = MplTempbydepth(dfintertemp, "direct", depths)
        self.toolbarintertempdirect = NavigationToolbar(self.graphintertempdirect, self)
        self.vboxintertempdirect.addWidget(self.graphintertempdirect)
        self.vboxintertempdirect.addWidget(self.toolbarintertempdirect)
    
    def plotInterfaceTempMCMC(self, dfintertemp, depths, nb_quantiles):
        self.graphintertempMCMC = MplTempbydepth(dfintertemp, "MCMC", depths, nb_quantiles=nb_quantiles)
        self.toolbarintertempMCMC = NavigationToolbar(self.graphintertempMCMC, self)
        self.vboxintertempMCMC.addWidget(self.graphintertempMCMC)
        self.vboxintertempMCMC.addWidget(self.toolbarintertempMCMC)
    
    def histos(self, dfallparams):
        self.histos = MplCanvasHisto(dfallparams)
        self.toolbarhistos = NavigationToolbar(self.histos, self)
        self.vboxhistos.addWidget(self.histos)
        self.vboxhistos.addWidget(self.toolbarhistos)

    def plotParapluies(self, dfsolvedtemp, dfdepths):
        return
        select_umb = self.build_result_queries(result_type ="Umbrella",quantile=0)
        select_temps.exec()
        #This is ugly, it should be changed!
        temps_array = []
        while select_temps.next():
            temps_array.append([select_temps.value(0),select_temps.value(1), select_temps.value(2)]) #Date, Flows, Depths
        temps_array = np.array(temps_array)
        self.parapluies = MplCanvas(dfsolvedtemp, "parapluies", dfdepths)
        self.toolbarparapluies = NavigationToolbar(self.parapluies, self)
        self.vboxsolvedtempdirect.addWidget(self.parapluies)
        self.vboxsolvedtempdirect.addWidget(self.toolbarparapluies)
    
    def plotParapluiesMCMC(self, dfsolvedtemp, dfdepths):
        self.parapluiesMCMC = MplCanvas(dfsolvedtemp, "parapluies", dfdepths)
        self.toolbarparapluiesMCMC = NavigationToolbar(self.parapluiesMCMC, self)
        self.vboxsolvedtempMCMC.addWidget(self.parapluiesMCMC)
        self.vboxsolvedtempMCMC.addWidget(self.toolbarparapluiesMCMC)

    def setBestParamsModel(self, dfbestparams):
        self.BestParamsModel = PandasModel(self.dfbestparams)
        self.tableViewBestParams.setModel(self.BestParamsModel)
        self.tableViewBestParams.resizeColumnsToContents()
        self.tableViewBestParams.verticalHeader().hide()
        self.tableViewBestParams.verticalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableViewBestParams.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableViewBestParams.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableViewBestParams.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableViewBestParams.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    
    def setParamsModel(self, dfparams):
        self.paramsModel = PandasModel(self.dfparams)
        self.tableViewParams.setModel(self.paramsModel)
        self.tableViewParams.resizeColumnsToContents()
        self.tableViewParams.verticalHeader().hide()
        self.tableViewParams.verticalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableViewParams.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableViewParams.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableViewParams.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.tableViewParams.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    
    def label_update(self):
        self.labelBins.setText(str(self.horizontalSliderBins.value()))
    
    def build_data_queries(self, full_query=False, field=""):
        """
        Build and return ONE AND ONLY ONE of the following queries:
        -if full_query is True, then extract the Date, Pressure and all Temperatures (this is for the Data part)
        -if field is not "", then it MUST be either "Temp" or "Pressure". Extract the Date and the corresponding field (this is for the Plot part): either all the temperatures or just the pressure.
        Theses queries take into account the actual value of self.currentdata to make to correct request (to either RawMeasuresTemp or CleanedMeasures)

        This function was made so that all SQL queries are in the same place and not scattered throughout the code.
        """
        computation_type = self.computation_type()
        if computation_type is None:
            return None
        elif not computation_type:
            #Raw data
            if full_query:
                return QSqlQuery(f"""SELECT RawMeasuresTemp.Date, RawMeasuresTemp.Temp1, RawMeasuresTemp.Temp2, RawMeasuresTemp.Temp3, RawMeasuresTemp.Temp4, RawMeasuresPress.TempBed, RawMeasuresPress.Pressure
                            FROM RawMeasuresTemp, RawMeasuresPress
                            WHERE RawMeasuresTemp.Date = RawMeasuresPress.Date
                                AND RawMeasuresPress.PointKey=RawMeasuresTemp.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                            """
                )
            elif field =="Temp":
                return QSqlQuery(f"""SELECT RawMeasuresTemp.Date, RawMeasuresTemp.Temp1, RawMeasuresTemp.Temp2, RawMeasuresTemp.Temp3, RawMeasuresTemp.Temp4, RawMeasuresPress.TempBed
                            FROM RawMeasuresTemp, RawMeasuresPress
                            WHERE RawMeasuresTemp.Date = RawMeasuresPress.Date
                                AND RawMeasuresPress.PointKey=RawMeasuresTemp.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                            """
                )
            elif field =="Pressure":
                return QSqlQuery(f"""SELECT RawMeasuresPress.Date,RawMeasuresPress.Pressure FROM RawMeasuresPress
                        WHERE RawMeasuresPress.PointKey= (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                        """
                )
        else:
            #Display cleaned measures
            if full_query:
                return QSqlQuery(f"""SELECT CleanedMeasures.Date, CleanedMeasures.Temp1, CleanedMeasures.Temp2, CleanedMeasures.Temp3, CleanedMeasures.Temp4, CleanedMeasures.TempBed, CleanedMeasures.Pressure
                        FROM CleanedMeasures
                        WHERE CleanedMeasures.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                            """
                )
            elif field =="Temp":
                return QSqlQuery(f"""SELECT CleanedMeasures.Date, CleanedMeasures.Temp1, CleanedMeasures.Temp2, CleanedMeasures.Temp3, CleanedMeasures.Temp4, CleanedMeasures.TempBed
                        FROM CleanedMeasures
                        WHERE CleanedMeasures.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                            """
                )
            elif field =="Pressure":
                return QSqlQuery(f"""SELECT CleanedMeasures.Date, CleanedMeasures.Pressure
                        FROM CleanedMeasures
                        WHERE CleanedMeasures.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                            """
                )
    def computation_type(self):
        """
        Return None if no computation was made: else, return False if only the direct model was computed and True if the MCMC was computed.
        """
        q = QSqlQuery("SELECT COUNT(*) FROM Quantile")
        q.exec()
        q.next()
        if q.value(0) ==0:
            return None
        elif q.value(0) ==1:
            return False
        else: 
            return True
    def build_result_queries(self,result_type ="",option=""):
        """
        Return a list of queries according to the user's wish. The list will either be of length 1 (the model was not computed before), or more than one: in this case, there are as many queries as there are quantiles, and they are ordered in the following way:
        1) default model
        2) quantile 0.05
        3) quantile 0.5
        4) quantile 0.95
        """
        computation_type = self.computation_type()
        if computation_type is None:
            return None
        elif not computation_type:
            return [self.define_result_queries(result_type=result_type,option=option, quantile=0)]
        else:
            #This could be enhanced by going in the database and seeing which quantiles are available. For now, these available quantiles will be hard-coded
            return [self.define_result_queries(result_type=result_type,option=option, quantile=1) for i in [0,0.05,0.5,0.95]]
    
    def define_result_queries(self,result_type ="",option="",quantile = 0):
        """
        Build and return ONE AND ONLY ONE query concerning the results.
        -quantile must be a float, and is either 0 (direct result), 0.05,0.5 or 0.95
        -option can be a string (which 2D map should be displayed or a date for the umbrellas) or a float (depth required by user)
        """
        #Water Flux
        if result_type =="WaterFlux":
            return QSqlQuery(f"""SELECT Date.Date, WaterFlow.WaterFlow FROM WaterFlow
            JOIN Date
            ON WaterFlow.Date = Date.id
                WHERE WaterFlow.Quantile = (SELECT Quantile.id FROM Quantile WHERE Quantile.Quantile = {quantile})
                AND WaterFlow.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
                """
            )
        elif result_type =="2DMap":
            if option=="Temperature":
                return QSqlQuery(f"""SELECT Date.Date, TemperatureAndHeatFlows.Temperature, TemperatureAndHeatFlows.Depth FROM TemperatureAndHeatFlows
            JOIN Date
            ON TemperatureAndHeatFlows.Date = Date.id
            JOIN Depth
            ON TemperatureAndHeatFlows.Depth = Depth.id
                WHERE TemperatureAndHeatFlows.Quantile = (SELECT Quantile.id FROM Quantile WHERE Quantile.Quantile = {quantile})
                AND  TemperatureAndHeatFlows.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
                    """
            )
            elif option=="HeatFlows":
                return QSqlQuery(f"""SELECT Date.Date, TemperatureAndHeatFlows.AdvectiveFlow,TemperatureAndHeatFlows.ConductiveFlow,TemperatureAndHeatFlows.TotalFlow, TemperatureAndHeatFlows.Depth FROM TemperatureAndHeatFlows
            JOIN Date
            ON TemperatureAndHeatFlows.Date = Date.id
            JOIN Depth
            ON TemperatureAndHeatFlows.Depth = Depth.id
                WHERE TemperatureAndHeatFlows.Quantile = (SELECT Quantile.id FROM Quantile WHERE Quantile.Quantile = {quantile})
                AND  TemperatureAndHeatFlows.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
                    """
            )
        elif result_type =="Umbrella":
            return QSqlQuery(f"""SELECT TemperatureAndHeatFlows.Temperature, Depth.Depth FROM TemperatureAndHeatFlows
            JOIN Depth
            ON TemperatureAndHeatFlows.Depth = Depth.id
                WHERE TemperatureAndHeatFlows.Date = (SELECT Date.id FROM Date WHERE Date.Date = "{option}") 
                AND TemperatureAndHeatFlows.Quantile = (SELECT Quantile.id FROM Quantile WHERE Quantile.Quantile = {quantile})
                AND  TemperatureAndHeatFlows.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
            """) 
        elif result_type =="TempPerDepth":
            return QSqlQuery(f"""
            SELECT Date.Date, TemperatureAndHeatFlows.Temperature FROM TemperatureAndHeatFlows
            JOIN Date
            ON TemperatureAndHeatFlows.Date = Date.id
                WHERE TemperatureAndHeatFlows.Depth = (SELECT Depth.id from Depth where Depth.Depth = {option})
                AND TemperatureAndHeatFlows.Quantile = (SELECT Quantile.id FROM Quantile WHERE Quantile.Quantile = {quantile})
                AND  TemperatureAndHeatFlows.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
            """)

"""
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = WidgetPoint()
    mainWin.show()
    sys.exit(app.exec_())
"""
 
# p = Point()
# s = Study()
# app = QtWidgets.QApplication(sys.argv)
# mainWin = WidgetPoint(p,s)
# mainWin.show()
# sys.exit(app.exec_())
