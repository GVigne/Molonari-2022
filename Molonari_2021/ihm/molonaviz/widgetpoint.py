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
from MoloModel import MoloModel, PressureDataModel, TemperatureDataModel, SolvedTemperatureModel, HeatFluxesModel, WaterFluxModel
from MoloView import MoloView,MoloView1D,MoloView2D,PressureView, TemperatureView,UmbrellaView,TempDepthView,TempMapView,AdvectiveFlowView, ConductiveFlowView, TotalFlowView, WaterFluxView

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
        self.comboBoxSelectLayer.currentTextChanged.connect(self.changeDisplayedParams)
        self.radioButtonTherm1.toggled.connect(self.refreshTempDepthView)
        self.radioButtonTherm2.toggled.connect(self.refreshTempDepthView)
        self.radioButtonTherm3.toggled.connect(self.refreshTempDepthView)      
        self.pushButtonReset.clicked.connect(self.reset)
        self.pushButtonCleanUp.clicked.connect(self.cleanup)
        self.pushButtonCompute.clicked.connect(self.compute)
        self.checkBoxRaw_Data.stateChanged.connect(self.checkbox)
        self.pushButtonRefreshBins.clicked.connect(self.refreshbins)
        self.horizontalSliderBins.valueChanged.connect(self.label_update)
        self.tabWidget.setCurrentIndex(3)

        #TO REMOVE
        self.currentdata ="processed"
        self.pointDir = self.point.getPointDir()
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("molonari_slqdb.sqlite")
        self.con.open()
        self.point.name="Point034" #Needs to be changed

        self.setupComboBoxLayers()
        self.setupCheckboxesQuantiles()
        self.setPressureAndTemperatureModels()
        self.setDataPlots()
        self.setResultsPlots()

    def setInfoTab(self):
        select_path,select_notice,select_infos = self.build_infos_queries()

        #Installation image
        select_path.exec()
        select_path.next()
        self.labelSchema.setPixmap(QPixmap(select_path.value(0))) 
        self.labelSchema.setAlignment(QtCore.Qt.AlignHCenter)
        #This allows the image to take the entire size of the widget, however it will be misshapen
        # self.labelSchema.setScaledContents(True)
        # self.labelSchema.setSizePolicy(QtWidgets.QSizePolicy.Ignored,QtWidgets.QSizePolicy.Ignored)
        
        #Notice
        select_notice.exec()
        select_notice.next()
        self.plainTextEditNotice.setPlainText(select_notice.value(0))
        
        #Infos
        self.infosModel = QSqlQueryModel()
        self.infosModel.setQuery(select_infos)
        self.tableViewInfos.setModel(self.infosModel)

    def setupComboBoxLayers(self):
        """
        Setup the Combo box and which will be used to display the parameters
        """
        select_depths_layers = self.build_layers_query()
        select_depths_layers.exec()
        while select_depths_layers.next():
            self.comboBoxSelectLayer.addItem(select_depths_layers.value(0))
    
    def changeDisplayedParams(self,layer):
        """
        Display in the table view the parameters corresponding to the given layer.
        """
        select_params = self.build_params_query(layer)
        self.paramsModel = QSqlQueryModel()
        self.paramsModel.setQuery(select_params)
        self.tableViewParams.setModel(self.paramsModel)
    
    def setupCheckboxesQuantiles(self):
        """
        Display as many checkboxes as there are quantiles in the database, along with the associated RMSE.
        """
        select_quantiles = self.build_global_RMSE_query()
        select_quantiles.exec()
        i=0
        while select_quantiles.next():
            if select_quantiles.value(1) =="0":
                text_checkbox = "Modèle direct"
            else:
                text_checkbox = f"Quantile {select_quantiles.value(1)}"
            quantile_checkbox = QtWidgets.QCheckBox(text_checkbox)
            quantile_checkbox.stateChanged.connect(self.refreshTempDepthView)
            self.gridLayoutQuantiles.addWidget(quantile_checkbox,i,0)
            self.gridLayoutQuantiles.addWidget(QtWidgets.QLabel(f"RMSE: {select_quantiles.value(0)}"),i,1)
            i +=1

    def refreshTempDepthView(self):
        """
        This method is called when a checkbox showing a quantile or a radio buttion is changed. New curves should be plotted in the Temperature per Depth View.
        """
        #Needs to be adapted!
        return

    def setPressureAndTemperatureModels(self):
        # Set the Temperature and Pressure arrays
        select_query = self.build_data_queries(full_query=True) #Query changes according to self.currentdata
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
        self.setPressureAndTemperatureModels()
        self.setDataPlots()

    def reset(self):
        #Needs to be adapted!
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
        #Needs to be adapted!
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
        #Needs to be adapted! Especially self.onMCMCisFinished (when computations are done)
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
        #Needs to be adapted!
        return

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
        #Needs to be adapted!
        return
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
        self.tempmodel = TemperatureDataModel([select_temp])
        self.graphtemp = TemperatureView(self.tempmodel, time_dependent=True,ylabel="Pression différentielle (m)")
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
        if self.computation_type() is not None:
            self.plotFluxes()
            self.plotTemperatureMap()
            self.plotHistos()  
        else:
            # vbox = QtWidgets.QVBoxLayout()
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxWaterFlux.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxAdvectiveFlux.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxTotalFlux.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxConductiveFlux.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxTempMap.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxUmbrella.setLayout(vbox)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel("No model has been computed yet"),QtCore.Qt.AlignCenter)
            self.groupBoxTempDepth.setLayout(vbox)

    def plotTemperatureMap(self):
        select_tempmap = self.build_result_queries(result_type="Temperature",option="2DMap") #This is a list
        self.tempmap_model = SolvedTemperatureModel(select_tempmap)
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

        self.tempmap_model.exec()

    def plotFluxes(self):
        #Plot the heat fluxes
        select_heatfluxes= self.build_result_queries(result_type="2DMap",option="HeatFlows") #This is a list
        self.fluxes_model = HeatFluxesModel(select_heatfluxes)
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

        self.fluxes_model.exec()

        #Plot the water fluxes
        select_waterflux= self.build_result_queries(result_type="WaterFlux") #This is already a list
        self.waterflux_model = WaterFluxModel(select_waterflux)
        self.waterflux_view = WaterFluxView(self.waterflux_model)
        
        self.toolbarWaterFlux = NavigationToolbar(self.waterflux_view, self)
        vbox = QtWidgets.QVBoxLayout()
        self.groupBoxWaterFlux.setLayout(vbox)
        vbox.addWidget(self.waterflux_view)
        vbox.addWidget(self.toolbarWaterFlux)

        self.waterflux_model.exec()
    
    def plotHistos(self):
        pass

    # def histos(self, dfallparams):
    #     self.histos = MplCanvasHisto(dfallparams)
    #     self.toolbarhistos = NavigationToolbar(self.histos, self)
    #     self.vboxhistos.addWidget(self.histos)
    #     self.vboxhistos.addWidget(self.toolbarhistos)

    def label_update(self):
        #Needs to be adapted?
        return
        self.labelBins.setText(str(self.horizontalSliderBins.value()))
    
    def build_infos_queries(self):
        """
        Build and return three queries for the info tab:
        -one to get the path to the image of sampling point (so a .png of .jpg file)
        -one to get the Notice
        -one to get the rest of the information of the sampling point.
        
        This function could be greatly enhanced!
        """
        scheme_path = QSqlQuery(f"""
        SELECT SamplingPoint.Scheme FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}"
        """
        )
        notice = QSqlQuery(f"""
        SELECT SamplingPoint.Notice FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}"
        """
        )
        infos = QSqlQuery(f"""
        SELECT SamplingPoint.Name,SamplingPoint.Longitude,SamplingPoint.Latitude,SamplingPoint.Implentation,SamplingPoint.LastTransfer,SamplingPoint.DeltaH,SamplingPoint.RiverBed FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}"
        """
        )
        return scheme_path,notice,infos

    def build_layers_query(self):
        """
        Build and return a query giving the depths of all the layers.
        """
        return QSqlQuery(f"""
            SELECT Layer.DepthBed FROM Layer 
            JOIN BestParameters ON Layer.id = BestParameters.Layer
            JOIN Point ON BestParameters.PointKey = Point.id
            JOIN SamplingPoint ON Point.SamplingPoint = SamplingPoint.id
            WHERE SamplingPoint.Name ="{self.point.name}"       
        """
        )
    
    def build_params_query(self,depth):
        """
        Build and return the parameters for the given depth.
        """
        return QSqlQuery(f"""
                SELECT BestParameters.log10KBest, BestParameters.LambdaSBest,BestParameters.NBest FROM BestParameters 
                JOIN Layer ON BestParameters.Layer = Layer.id WHERE Layer.DepthBed ={depth}      
        """
        )
    
    def build_global_RMSE_query(self):
        """
        Build and return all the quantiles as well as the associated global RMSE.
        """
        return QSqlQuery(f"""
                SELECT RMSE.RMSET, Quantile.Quantile FROM RMSE 
                JOIN Quantile
                ON RMSE.QuantileID = Quantile.id     
        """
        )
    
    def build_quantiles(self):
        """
        Build and return the quantiles values
        """
        return QSqlQuery(f"""
                SELECT Quantile.Quantile FROM Quantile    
        """
        ) 
    
    def build_data_queries(self, full_query=False, field=""):
        """
        Build and return ONE AND ONLY ONE of the following queries:
        -if full_query is True, then extract the Date, Pressure and all Temperatures (this is for the Data part)
        -if field is not "", then it MUST be either "Temp" or "Pressure". Extract the Date and the corresponding field (this is for the Plot part): either all the temperatures or just the pressure.
        Theses queries take into account the actual value of self.currentdata to make to correct request (to either RawMeasuresTemp or CleanedMeasures)
        """
        if self.currentdata=="raw":
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
        elif self.currentdata == "processed":
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
        Return a list of queries according to the user's wish. The list will either be of length 1 (the model was not computed before), or more than one: in this case, there are as many queries as there are quantiles: the first query corresponds to the default model (quantile 0)
        """
        computation_type = self.computation_type()
        if computation_type is None:
            return None
        elif not computation_type:
            return [self.define_result_queries(result_type=result_type,option=option, quantile=0)]
        else:
            #This could be enhanced by going in the database and seeing which quantiles are available. For now, these available quantiles will be hard-coded
            select_quantiles = self.build_quantiles()
            select_quantiles.exec()
            result = []
            while select_quantiles.next():
                if select_quantiles.value(0) ==0:
                    #Default model should always be the first one
                    result.insert(0,self.define_result_queries(result_type=result_type,option=option, quantile=select_quantiles.value(0)))
                else:
                    result.append(self.define_result_queries(result_type=result_type,option=option, quantile=select_quantiles.value(0)))
            return result
    
    def define_result_queries(self,result_type ="",option="",quantile = 0):
        """
        Build and return ONE AND ONLY ONE query concerning the results.
        -quantile must be a float, and is either 0 (direct result), 0.05,0.5 or 0.95
        -option can be a string (which 2D map should be displayed or a date for the umbrellas) or a float (depth required by user)
        """
        #Water Flux
        if result_type =="WaterFlux":
            return QSqlQuery(f"""SELECT Date.Date, WaterFlow.WaterFlow, Quantile.Quantile FROM WaterFlow
            JOIN Date
            ON WaterFlow.Date = Date.id
            JOIN Quantile
            ON WaterFlow.Quantile = Quantile.id
                WHERE Quantile.Quantile = {quantile}
                AND WaterFlow.PointKey = (SELECT Point.id FROM Point WHERE Point.SamplingPoint = (SELECT SamplingPoint.id FROM SamplingPoint WHERE SamplingPoint.name = "{self.point.name}"))
                ORDER BY Date.Dat
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

if __name__ == '__main__':
    p = Point()
    s = Study()
    app = QtWidgets.QApplication(sys.argv)
    mainWin = WidgetPoint(p,s)
    mainWin.show()
    sys.exit(app.exec_())