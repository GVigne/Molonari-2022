import sys
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
from datetime import datetime

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as colors
import numpy as np
from matplotlib.ticker import MaxNLocator


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, pdf, datatype, depths=None, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout(h_pad=5, pad=5)
        self.pdf = pdf #This is no longer a data frame: it should just be "data"
        self.datatype = datatype
        self.depths = depths
        self.list_Curves = ["pressure", "temperature", "water flow", "temperature interface", "temperature with quantiles", "water flow with quantiles"]
        if self.datatype in self.list_Curves:
            self.setTime()
            self.setCurves()
        elif self.datatype == "frise":
            self.setTime()
            self.setFrises()
        elif self.datatype == "parapluies":
            self.setParapluies()

    def setTime(self):
        self.x = mdates.date2num(self.pdf[:,0])
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))
        plt.setp(self.axes.get_xticklabels(), rotation = 15)
        #self.axes.set_xlabel("Dates") Inutile

    def setCurves(self):
        if self.datatype == "temperature":
            #On a 4 colonnes de températures
            for i in range(1,5):
                data = self.pdf[:,i]
                self.axes.plot(self.x, data, label=f"Capteur n°{i}")
            #On rajoute la température du capteur de pression
            last_temp = self.pdf[:,5]
            self.axes.plot(self.x, last_temp, label = "Capteur de pression")
            self.axes.legend(loc='best')
            self.axes.set_ylabel("Températures (K)")
        
        #elif self.datatype == "temperature with quantiles":
            #On a 4 colonnes de températures
            #for i in range(1,5):
            #    data = self.pdf[self.pdf.columns[i]].values.tolist()
             #   self.axes.plot(self.x, data, label=f"{self.pdf.columns[i]}")
            #self.axes.legend(loc='best')
            #self.axes.set_ylabel("Températures (K)")
        
        elif self.datatype == "water flow with quantiles" or self.datatype == "temperature with quantiles":
            quantiles = list(self.pdf.columns)
            for i in range(1,len(quantiles)):
                data = self.pdf[self.pdf.columns[i]].values.tolist()
                self.axes.plot(self.x, data, label=f"{quantiles[i]}")
            self.axes.legend(loc="best")
            if self.datatype == "water flow with quantiles":
                self.axes.set_ylabel("Débit d'eau (m/s)")
            else :
                self.axes.set_ylabel("Températures (K)")

        else : 
            data = self.pdf[:,1]
            self.axes.plot(self.x, data)
            if self.datatype == "pressure":
                self.axes.set_ylabel("Pression différentielle (m)")
            elif self.datatype == "water flow":
                self.axes.set_ylabel("Débit d'eau (m/s)")
            elif self.datatype =="temperature interface":
                self.axes.set_ylabel("Température de l'interface (K)")
        
        self.axes.grid(True)
    
    def setFrises(self):
        profils = self.pdf.to_numpy()
        profils = profils[:,1:].astype(np.float)
        profils = np.transpose(profils) #à vérifier
        #profils = np.flipud(profils) #à vérifier
        depths = self.depths[self.depths.columns[0]].values.tolist()
        image = self.axes.imshow(profils, cmap=cm.Spectral_r, aspect="auto", extent=[self.x[0], self.x[-1], float(depths[-1]), float(depths[0])], data="float")
        self.axes.xaxis_date()
        self.axes.set_ylabel("Profondeur (m)")
        self.colorbar = plt.colorbar(image, ax=self.axes)

    def setParapluies(self):
        #Détermination du pas pour tracer 10 profils
        profils = self.pdf.to_numpy()
        n = profils.shape[0]
        pas = n // 10
        self.axes.set_xlabel("Température en K")
        self.axes.set_ylabel("Profondeur en m")
        self.axes.set_ylim(float(self.depths.values[-1]), float(self.depths.values[0]))
        try :
            for i in range(10):
                self.axes.plot(profils[i*pas, 1:], self.depths, label=profils[i*pas,0])
                #print(profils[i, 1:])
        except IndexError :
            print('Not enough values in files')
        self.axes.legend(loc='best', fontsize='xx-small')

    def update_(self, new_pdf, depths=None):
        self.axes.clear()
        self.pdf = new_pdf
        self.depths = depths
        if self.datatype in self.list_Curves :
            #print("hello curve")
            self.setTime()
            self.setCurves()
        elif self.datatype == "frise":
            #print("hello frise")
            self.setTime()
            self.colorbar.remove()
            self.setFrises()
        elif self.datatype == "parapluies":
            self.setParapluies()
        self.draw()


class MplCanvasHisto(FigureCanvasQTAgg):

    def __init__(self, df, bins=60, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(221), self.fig.add_subplot(222), self.fig.add_subplot(223), self.fig.add_subplot(224)
        super(MplCanvasHisto, self).__init__(self.fig)
        self.fig.tight_layout(h_pad=2, pad=2)
        self.df = df
        self.bins = bins
        self.setHistos()
    
    def setHistos(self):
        colors = ['green', 'blue', 'orange', 'pink']
        for i in range(4):
            data = self.df[self.df.columns[i+1]].values.tolist()
            self.ax[i].hist(data, edgecolor='black', bins=self.bins, alpha=.3, density=True, color=colors[i])
        self.ax[0].set_title("Histogramme a posteriori des -log10K")
        self.ax[1].set_title("Histogramme a posteriori des n")
        self.ax[2].set_title("Histogramme a posteriori des lambda_s")
        self.ax[3].set_title("Histogramme a posteriori des rho_s * c_s")
        self.ax[3].tick_params(labelsize = 'small', labelrotation = 25)
        self.fig.tight_layout()
    
    def update_(self, new_df):
        self.df = new_df
        for ax in self.ax :
            ax.clear()
        self.setHistos()
        self.draw()
    
    def refresh(self, bins):
        self.bins = bins
        for ax in self.ax :
            ax.clear()
        self.setHistos()
        self.draw()

class MplTempbydepth(FigureCanvasQTAgg):

    def __init__(self, pdf, datatype, depths, depth_index=0, nb_quantiles=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplTempbydepth, self).__init__(self.fig)
        self.fig.tight_layout(h_pad=5, pad=5)
        self.pdf = pdf
        self.datatype = datatype
        self.depth_index = depth_index
        self.nb_quantiles = nb_quantiles
        self.depths = depths

        self.setTime()
        self.setCurves()

    def setTime(self):
        self.x = mdates.date2num(self.pdf[self.pdf.columns[0]])
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M")
        self.axes.xaxis.set_major_formatter(formatter)
        self.axes.xaxis.set_major_locator(MaxNLocator(4))
        plt.setp(self.axes.get_xticklabels(), rotation = 15)
        #self.axes.set_xlabel("Dates") Inutile
    
    def setCurves(self):
        if self.datatype == "direct":
            #Il n'y a pas de quantiles à prendre en compte
            data = self.pdf[self.pdf.columns[self.depth_index+1]].values.tolist()
            self.axes.plot(self.x, data)
            #print(len(data))
        elif self.datatype == "MCMC":
            #Il faut prendre en compte les quantiles
            index = 1 + (1+self.nb_quantiles)*self.depth_index
            for i in range(self.nb_quantiles+1):
                label = self.pdf.columns[index + i]
                data = self.pdf[label].values.tolist()
                self.axes.plot(self.x, data, label=label)
        self.axes.set_title(f"Température à la profondeur {self.depths.values[self.depth_index]}")
        self.axes.set_ylabel("Température (K)")
        self.axes.legend(loc='best', fontsize='xx-small')
    
    def update_(self, pdf, depths, nb_quantiles=None):
        self.pdf = pdf
        self.depths = depths
        self.nb_quantiles = nb_quantiles
        self.axes.clear()
        self.setTime()
        self.setCurves()
        self.draw()

    def refresh(self, depth_index):
        self.depth_index = depth_index
        self.axes.clear()
        self.setTime()
        self.setCurves()
        self.draw()




class MplCanvaHeatFluxes(FigureCanvasQTAgg):
    
    def __init__(self, df_advec, df_conduc, df_tot, df_depths, width=5, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(311), self.fig.add_subplot(312), self.fig.add_subplot(313)
        super(MplCanvaHeatFluxes, self).__init__(self.fig)
        self.fig.tight_layout(h_pad=2, pad=2)
        self.df_advec = df_advec
        self.df_conduc = df_conduc
        self.df_tot = df_tot
        self.depths = df_depths
        self.setTime()
        self.setFrises()

    def setTime(self):
        self.x = mdates.date2num(self.df_advec[self.df_advec.columns[0]])
        formatter = mdates.DateFormatter("%y/%m/%d %H:%M:%S")
        for i in range(3):
            self.ax[i].xaxis.set_major_formatter(formatter)
            self.ax[i].xaxis.set_major_locator(MaxNLocator(4))
            plt.setp(self.ax[i].get_xticklabels(), rotation = 0)

    def setFrises(self):

        depths = self.depths[self.depths.columns[0]].values.tolist()
        
        profils = self.df_advec.to_numpy()
        profils = profils[:,1:].astype(np.float)
        profils = np.transpose(profils)
        #profils = np.flipud(profils)
        image = self.ax[0].imshow(profils, cmap=cm.Spectral_r, aspect="auto", extent=[self.x[0], self.x[-1], float(depths[-1]), float(depths[0])], data="float")
        self.ax[0].xaxis_date()
        self.ax[0].set_title('Flux advectif (W/m2)')
        self.ax[0].set_ylabel("Profondeur (m)")
        self.colorbar_advec = plt.colorbar(image, ax=self.ax[0])

        profils = self.df_conduc.to_numpy()
        profils = profils[:,1:].astype(np.float)
        profils = np.transpose(profils)
        #profils = np.flipud(profils)
        image = self.ax[1].imshow(profils, cmap=cm.Spectral_r, aspect="auto", extent=[self.x[0], self.x[-1], float(depths[-1]), float(depths[0])], data="float")
        self.ax[1].xaxis_date()
        self.ax[1].set_title('Flux conductif (W/m2)')
        self.ax[1].set_ylabel("Profondeur (m)")
        self.colorbar_conduc = plt.colorbar(image, ax=self.ax[1])

        profils = self.df_tot.to_numpy()
        profils = profils[:,1:].astype(np.float)
        profils = np.transpose(profils)
        #profils = np.flipud(profils)
        image = self.ax[2].imshow(profils, cmap=cm.Spectral_r, aspect="auto", extent=[self.x[0], self.x[-1], float(depths[-1]), float(depths[0])], data="float")
        self.ax[2].xaxis_date()
        self.ax[2].set_title("Flux d'énergie total (W/m2)")
        self.ax[2].set_ylabel("Profondeur (m)")
        self.colorbar_tot = plt.colorbar(image, ax=self.ax[2])
    
    def update_(self, df_advec, df_conduc, df_tot, df_depths):
        for i in range(3):
            self.ax[i].clear()
        self.df_advec = df_advec
        self.df_conduc = df_conduc
        self.df_tot = df_tot
        self.depths = df_depths
        self.colorbar_advec.remove()
        self.colorbar_conduc.remove()
        self.colorbar_tot.remove()
        self.setTime()
        self.setFrises()
        self.draw()
        
