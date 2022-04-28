import os, shutil
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtSql import QSqlQuery

from pyheatmy import *
from point import Point
from Database.mainDb import MainDb
from usefulfonctions import SQl_to_pandas


class ColumnMCMCRunner(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    
    def __init__(self, col, nb_iter: int, priors: dict, nb_cells: str, quantiles: list):
        # Call constructor of parent classes
        super(ColumnMCMCRunner, self).__init__()
        
        self.col = col
        self.nb_iter = nb_iter
        self.priors = priors
        self.nb_cells = nb_cells
        self.quantiles = quantiles
        
    def run(self):
        print("Launching MCMC...")

        all_priors = [["Couche 1", self.col._real_z[-1], self.priors]]
        
        self.col.compute_mcmc(self.nb_iter, all_priors, self.nb_cells, self.quantiles)

        self.finished.emit()


class Compute(QtCore.QObject):

    """
    How to use this class : 
    - Create a Compute object : compute = Compute(point: Point)
    - Create an associated Column object : compute.setColumn()
    - Launch the computation :
        - with given parameters : compute.computeDirectModel(params: tuple, nb_cells: int, sensorDir: str)
        - with parameters inferred from MCMC : compute.computeMCMC(nb_iter: int, priors: dict, nb_cells: str, sensorDir: str)
    """
    MCMCFinished = QtCore.pyqtSignal()

    def __init__(self, db, point: Point=None):
        # Call constructor of parent classes
        super(Compute, self).__init__()
        self.thread = QtCore.QThread()

        self.point = point
        self.col = None
        
        self.mainDb = MainDb(db)
    
    def setColumn(self):
        shaft_depth = QSqlQuery(f"""SELECT Depth1,
                                Depth2,
                                Depth3,
                                Depth4
                            FROM Shaft 
                            WHERE Shaft.id=(SELECT Samplingpoint.Shaft FROM Samplingpoint WHERE Samplingpoint.Name = "{self.point.name}");
""")
        shaft_depth.exec()
        shaft_depth.next()
        shaft_depth_array = [shaft_depth.value(i) for i in range(4)]

        select_p_meas = QSqlQuery(f"""SELECT Precision
                            FROM PressureSensor WHERE PressureSensor.id=(SELECT Samplingpoint.PressureSensor FROM Samplingpoint WHERE Samplingpoint.Name = "{self.point.name}") """)
        select_t_meas = QSqlQuery(f"""SELECT Error FROM Thermometer 
                                    JOIN Shaft ON
                                    Thermometer.id = Shaft.Thermo_model
                                    WHERE Shaft.id=(SELECT Samplingpoint.Shaft FROM Samplingpoint WHERE Samplingpoint.Name = "{self.point.name}")
                                """)
        select_p_meas.exec()
        select_p_meas.next()
        select_t_meas.exec()
        select_t_meas.next()

        select_temps = QSqlQuery(f"""SELECT Date.Date, CleanedMeasures.Temp1, CleanedMeasures.Temp2, CleanedMeasures.Temp3, CleanedMeasures.Temp4
                        FROM CleanedMeasures
                        JOIN Date
                        ON CleanedMeasures.Date = Date.id
                        WHERE CleanedMeasures.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                        ORDER BY Date.Date; """)
        select_temps.exec()
        temps_array = []
        while select_temps.next():
            temps_array.append((SQl_to_pandas(select_temps.value(0)), [select_temps.value(i) for i in range(1,5)]))

        select_press =QSqlQuery(f"""SELECT Date.Date, CleanedMeasures.Pressure, CleanedMeasures.TempBed
                        FROM CleanedMeasures
                        JOIN Date
                        ON CleanedMeasures.Date = Date.id
                        WHERE CleanedMeasures.PointKey = (SELECT id FROM SamplingPoint WHERE SamplingPoint.Name = "{self.point.name}")
                        ORDER BY Date.Date """)
        select_press.exec()
        press_array = []
        while select_press.next():
            press_array.append((SQl_to_pandas(select_press.value(0)), [select_press.value(1),select_press.value(2)]))

        col_dict = {
	        "river_bed": self.point.rivBed, 
            "depth_sensors": shaft_depth_array,
	        "offset": self.point.deltaH,
            "dH_measures": press_array,
	        "T_measures": temps_array,
            "sigma_meas_P": select_p_meas.value(0),
            "sigma_meas_T": select_t_meas.value(0)
            }
        self.col = Column.from_dict(col_dict)
        
    def computeMCMC(self, nb_iter: int, priors: dict, nb_cells: str, quantiles: tuple):
        
        self.nb_cells = nb_cells
        if self.thread.isRunning():
            print("Please wait while previous MCMC is finished")
            return
    
        # Initialisation de la colonne
        self.setColumn()
        self.quantiles = quantiles

        # Lancement de la MCMC
        #self.col.compute_mcmc(nb_iter, priors, nb_cells, quantile = (.05, .5, .95))

        self.mcmc_runner = ColumnMCMCRunner(self.col, nb_iter, priors, nb_cells, quantiles = self.quantiles)
        self.mcmc_runner.finished.connect(self.endMCMC)
        self.mcmc_runner.moveToThread(self.thread)
        self.thread.started.connect(self.mcmc_runner.run)
        self.thread.start()


    def endMCMC(self):

        self.thread.quit()
        print("MCMC finished")

        best_params = self.col.get_best_param()[0]

        # Sauvegarde des résultats de la MCMC
        resultsDir = os.path.join(self.point.getPointDir(), 'results', 'MCMC_results')
        self.saveBestParams(resultsDir)
        self.saveAllParams(resultsDir)
        
        # Lancement du modèle direct avec les paramètres inférés
        self.col.compute_solve_transi(best_params, self.nb_cells)
        
        # Sauvegarde des différents résultats du modèle direct
        self.saveResults(resultsDir)

        # Sauvegarde des quantiles
        self.saveFlowWithQuantiles(resultsDir)
        self.saveTempWithQuantiles(resultsDir)

        self.MCMCFinished.emit()
        

    def computeDirectModel(self, params: tuple, nb_cells: int, depths):

        # Initialisation de la colonne
        self.setColumn()

        # Lancement du modèle direct
        n = [i for i in range(len(depths))] #Layer name
        layersListInput = [(str(n[i]), depths[i], params[0][i],params[1][i],params[2][i],params[3][i]) for i in range(len(depths))]
        # return {"Premier":layersListInput, "Second":self.col.depth_sensors}

        self.col.compute_solve_transi(layersListCreator(layersListInput), nb_cells)

        # Sauvegarde des différents résultats du modèle direct
        resultsDir = os.path.join(self.point.getPointDir(), 'results', 'direct_model_results')
        self.saveLayers()
        self.updatePointinDb(nb_cells)
        self.saveResults(resultsDir)
        # self.saveParams(params, resultsDir)
    
    def saveLayers(self):
        pass
    
    def updatePointinDb(self,nb_cells):
        """
        Update the number of cell in the database.
        """
        pass

    def saveParams(self, params: tuple, resultsDir: str):
        """
        Sauvegarde les paramètres du modèle direct dans un fichier csv en local
        Pour accéder au fichier : pointDir --> results --> direct_model_results --> params.csv
        """

        params_dict = {
            'moinslog10K': [params[0]], 
            'n': [params[1]], 
            'lambda_s': [params[2]], 
            'rhos_cs': [params[3]]
        }

        df_params = pd.DataFrame.from_dict(params_dict)

        params_file = os.path.join(resultsDir, 'params.csv')
        df_params.to_csv(params_file, index=True)
        
        '''
        SQL : INSERT INTO Layer (DepthBed) VALUES (1) WHERE id = layer
        '''
            
        #Find the id related to the SamplingPoint
        query_test = QSqlQuery()
        query_test.exec_(f"SELECT id FROM Point WHERE SamplingPoint = (SELECT id FROM SamplingPoint WHERE PointName = {self.point.getName()})")
        query_test.first()
        self.point_id = query_test.value(0)
        
        #Find the bestParameter related to the id found
        query_test.exec_(f"SELECT Layer FROM BestParameters WHERE PointKey = {self.point_id}") # Return 1,2,3
        query_test.first()
        while True:
            l = query_test.value(0)
            query_de_ins = QSqlQuery()
            query_de_ins.exec_(f"DELETE FROM BestParameters WHERE PointKey = {self.point_id} AND Layer = {l} ")
            query_de_ins.exe_(f"""
                              INSERT INTO BestParameters
                              VALUES {params_dict["moinslog10K"],params_dict["n"],params_dict["lambda_s"],params_dict["rhos_cs"],l,self.point_id}
                              """)
            if not (query_test.next()): break
        
        query_new = QSqlQuery()
        query_new.exec_(f"""UPDATE Layer SET DepthBed={self.tableWidget.item(id,0).text()} WHERE id = {layer}""")
        
  
    def saveBestParams(self, resultsDir: str):
        """
        Sauvegarde les meilleurs paramètres inférés par la MMC dans un fichier csv en local
        Pour accéder au fichier : pointDir --> results --> MCMC_results --> MCMC_best_params.csv
        """

        best_params = self.col.get_best_param()[0]

        best_params_dict = {
            'moinslog10K':[best_params[0]], 
            'n':[best_params[1]], 
            'lambda_s':[best_params[2]], 
            'rhos_cs':[best_params[3]]
        }

        df_best_params = pd.DataFrame.from_dict(best_params_dict)

        best_params_file = os.path.join(resultsDir, 'MCMC_best_params.csv')
        df_best_params.to_csv(best_params_file, index=True)

    def saveAllParams(self, resultsDir: str):

        all_moins10logK = self.col.get_all_moinslog10K()
        all_n = self.col.get_all_n()
        all_lambda_s = self.col.get_all_lambda_s()
        all_rhos_cs = self.col.get_all_rhos_cs()

        all_params_dict = {
            'moinslog10K': all_moins10logK, 
            'n': all_n, 
            'lambda_s': all_lambda_s, 
            'rhos_cs': all_rhos_cs
        }

        df_all_params = pd.DataFrame.from_dict(all_params_dict)

        all_params_file = os.path.join(resultsDir, 'MCMC_all_params.csv')
        df_all_params.to_csv(all_params_file, index=True)
    


    def saveFlowWithQuantiles(self, resultsDir: str):

        times = self.col.times_solve

        flows = self.col.flows_solve[0,::]
        #quantile05 = self.col.get_flows_quantile(0.05)
        #quantile50 = self.col.get_flows_quantile(0.5)
        #quantile95 = self.col.get_flows_quantile(0.95)
        QUANTILES = []
        for quantile in self.quantiles :
            QUANTILES.append(self.col.get_flows_quantile(quantile)[0,::])

        # Formatage des dates
        n_dates = len(times)
        times_string = np.zeros((n_dates,1))
        times_string = times_string.astype('str')
        for i in range(n_dates):
            times_string[i,0] = times[i].strftime('%y/%m/%d %H:%M:%S')

        # Création du dataframe
        np_flows_quantiles = np.zeros((n_dates,len(QUANTILES)+1))
        for i in range(n_dates):
            np_flows_quantiles[i,0] = flows[i]
            for k in range(len(QUANTILES)):
                np_flows_quantiles[i,k+1] = QUANTILES[k][i]
        np_flows_times_and_quantiles = np.concatenate((times_string, np_flows_quantiles), axis=1)
        columns_names = ["Date Heure, GMT+01:00", 
        "Débit d'eau échangé (m/s) - pour les meilleurs paramètres"]
        for quantile in self.quantiles :
            columns_names.append(f"Débit d'eau échangé (m/s) - quantile {quantile}")
        df_flows_quantiles = pd.DataFrame(np_flows_times_and_quantiles, 
        columns=columns_names)
    
        # Sauvegarde sous forme d'un fichier csv
        flows_quantiles_file = os.path.join(resultsDir, 'MCMC_flows_quantiles.csv')
        df_flows_quantiles.to_csv(flows_quantiles_file, index=False)
    

    def saveTempWithQuantiles(self, resultsDir: str):
        
        times = self.col.times_solve

        dataframe_list = []

        # Formatage des dates
        n_dates = len(times)
        times_string = np.zeros((n_dates,1))
        times_string = times_string.astype('str')
        for i in range(n_dates):
            times_string[i,0] = times[i].strftime('%y/%m/%d %H:%M:%S')

        for l in range(self.col.temps_solve.shape[0]):

            temp = self.col.temps_solve[l,:] #température à la lème profondeur
            QUANTILES = []
            for quantile in self.quantiles :
                QUANTILES.append(self.col.get_temps_quantile(quantile)[l,:])

            # Création du dataframe
            np_temps_quantiles = np.zeros((n_dates,len(QUANTILES)+1))
            for i in range(n_dates):
                np_temps_quantiles[i,0] = temp[i]
                for k in range(len(QUANTILES)):
                    np_temps_quantiles[i, k+1] = QUANTILES[k][i]

            np_temps_times_and_quantiles = np.concatenate((times_string, np_temps_quantiles), axis=1)
            columns_names = ["Date Heure, GMT+01:00", 
            f"Température à la profondeur {l} (K) - pour les meilleurs paramètres"]
            for quantile in self.quantiles :
                columns_names.append(f"Température à la profondeur {l} (K) - quantile {quantile}") #À modifier pour avoir les vrais noms
            df_temps_quantiles = pd.DataFrame(np_temps_times_and_quantiles, 
            columns=columns_names)
            dataframe_list.append(df_temps_quantiles)

        df_temps_quantiles = dataframe_list[0]
        for i in range (1, len(dataframe_list)) :
            dataframe = dataframe_list[i]
            df_temps_quantiles = pd.concat([df_temps_quantiles, dataframe[dataframe.columns[1:]]], axis=1)
        # Sauvegarde sous forme d'un fichier csv
        temps_quantiles_file = os.path.join(resultsDir, 'MCMC_temps_quantiles.csv')
        df_temps_quantiles.to_csv(temps_quantiles_file, index=False)


    def saveResults(self, resultsDir: str):

        """
        Sauvegarde les différents résultats calculés sous forme de fichiers csv en local :
        - profils de températures calculés aux différentes profondeurs
        - chronique des flux d'eau échangés entre la nappe et la rivière

        Les résultats sont disponibles respectivement dans les fichiers suivants :
        - pointDir --> results --> solved_temperatures.csv
        - pointDir --> results --> solved_flows.csv

        Prend en argument :
        - la colonne sur laquelle les calculs ont été faits (type: Column)
        - le chemin d'accès vers le dossier 'results' du point (type: str)
        Ne retourne rien
        """
        
        temps = self.col.temps_solve
        times = self.col.times_solve
        flows = self.col.flows_solve[0,::]
        advective_flux = self.col.get_advec_flows_solve()
        conductive_flux = self.col.get_conduc_flows_solve()
        depths = self.col.get_depths_solve()
        times = self.col.get_times_solve()
        flows_for_insertion = self.col.flows_solve
        layers = self.col._layersList
        
        try:
            params = self.col.get_all_params()
        except:
            params = []
        
        try:
            quantiles = [0] + self.col.get_quantiles()
        except:
            quantiles = [0]
        
        ## Formatage des dates
        n_dates = len(times)
        times_string = np.zeros((n_dates,1))
        times_string = times_string.astype('str')
        for i in range(n_dates):
            times_string[i,0] = times[i].strftime('%y/%m/%d %H:%M:%S')
       

        self.mainDb.dateDb.insert(times)
        self.mainDb.depthDb.insert(depths)
        self.mainDb.quantileDb.insert(quantiles)
        self.mainDb.parametersDistributionDb.insert(params)
        self.mainDb.layerDb.insert(layers)
        self.mainDb.lastParametersDb.insert(layers)
        
        self.mainDb.temperatureAndHeatFlowsDb.insert_quantile_0(temps, advective_flux, conductive_flux, flows_for_insertion)
        if len(quantiles) > 1:
            self.mainDb.temperatureAndHeatFlowsDb.insert_quantiles(self.col, quantiles)