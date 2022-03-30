'''
Created on 16 march 2021

@author: fors
'''
import os
import sys

from PyQt5 import QtWidgets
from PyQt5 import uic

import pandas as pd
import numpy as np

import outputmesh as om
from outputmeshdialog import OutputMeshDialog

from fileutil import RoundTo1, ConvertDates

sys.path.append("../../../pyHeat")
import codepyheat as ph
from codepyheat.units import NSECINDAY
from codepyheat.geometry import Column
from codepyheat.porousMedia import PropPorousMedia
from codepyheat.heat import BoundaryConditionHeat
from codepyheat.hydrogeol import BoundaryConditionHyd 
from codepyheat.heat import BoundConditionSinus
from codepyheat.heat import BoundConditionMultiSinus

From_ComputeDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"computedialog.ui"))
class ComputeDialog(QtWidgets.QDialog,From_ComputeDialog):
    '''
    classdocs
    '''
    def __init__(self, parent, startDate, endDate, study, point):
        super(ComputeDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.setWindowTitle("{} Compute Dialog".format(point.name))

        # https://stackoverflow.com/questions/14582591/border-of-qgroupbox
        ss = """QGroupBox { 
                   border: 1px solid lightgray;
                   border-radius: 3px;
                   margin-top: 0.5em;
                }
                QGroupBox::title {
                   subcontrol-origin: margin;
                   left: 10px;
                   padding: 0 3px 0 3px;
                }"""
        self.boxDates.setStyleSheet(ss)
        self.boxModel.setStyleSheet(ss)
        self.boxInversion.setStyleSheet(ss)
        
        self.butOutputMesh.clicked.connect(self.editOutputMesh)
        self.butModel.clicked.connect(self.runModel)
        self.butInversion.clicked.connect(self.runInversion)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.restoreDefault) 
        
        self.study = study
        self.point = point
        self.defaultStartDate = startDate
        self.defaultEndDate = endDate
        
        self.restoreDefault()
        
    def restoreDefault(self):
        self.editStartDate.setDateTime(self.defaultStartDate)
        self.editEndDate.setDateTime(self.defaultEndDate)

        self.outputmesh = om.OutputMesh(self.point.geometry.riverDepth,
                                        self.point.geometry.tempDepths[-1],
                                        1.0)
        
        perm = ph.PERMEABILITY # TODO : to be confirmed (mail 17/03/2021)
        poro = ph.POROSITY
        cond = ph.LAMBDAS
        capa = ph.HEATCAPAS
        dens = ph.RHOW
        
        deltaPerm = RoundTo1(perm/10)
        deltaPoro = RoundTo1(poro/10)
        deltaCond = RoundTo1(cond/10)
        deltaCapa = RoundTo1(capa/10)
        deltaDens = RoundTo1(dens/10)
        
        self.editPermeability.setValue(perm)
        self.editPorosity.setValue(poro)
        self.editSedThCond.setValue(cond)
        self.editSedThCap.setValue(capa)
        self.editDensity.setValue(dens)
        
        self.editPermeability.setSingleStep(deltaPerm)
        self.editPorosity.setSingleStep(deltaPoro)
        self.editSedThCond.setSingleStep(deltaCond)
        self.editSedThCap.setSingleStep(deltaCapa)
        self.editDensity.setSingleStep(deltaDens)
           
        self.editPermStep.setValue(deltaPerm)
        self.editPoroStep.setValue(deltaPoro)
        self.editCondStep.setValue(deltaCond)
        self.editCapStep.setValue(deltaCapa)
        self.editDenStep.setValue(deltaDens)
        
        self.editPermStep.setSingleStep(deltaPerm/10)
        self.editPoroStep.setSingleStep(deltaPoro/10)
        self.editCondStep.setSingleStep(deltaCond/10)
        self.editCapStep.setSingleStep(deltaCapa/10)
        self.editDenStep.setSingleStep(deltaDens/10)
        
        self.editPermMin.setValue(RoundTo1(perm - 5*deltaPerm))
        self.editPoroMin.setValue(RoundTo1(poro - 5*deltaPoro))
        self.editCondMin.setValue(cond - 5*deltaCond)
        self.editCapMin.setValue(capa - 5*deltaCapa)
        self.editDenMin.setValue(dens - 5*deltaDens)
        
        self.editPermMin.setSingleStep(deltaPerm)
        self.editPoroMin.setSingleStep(deltaPoro)
        self.editCondMin.setSingleStep(deltaCond)
        self.editCapMin.setSingleStep(deltaCapa)
        self.editDenMin.setSingleStep(deltaDens)
        
        self.editPermMax.setValue(RoundTo1(perm + 5*deltaPerm))
        self.editPoroMax.setValue(RoundTo1(poro + 5*deltaPoro))
        self.editCondMax.setValue(cond + 5*deltaCond)
        self.editCapMax.setValue(capa + 5*deltaCapa)
        self.editDenMax.setValue(dens + 5*deltaDens)
        
        self.editPermMax.setSingleStep(deltaPerm)
        self.editPoroMax.setSingleStep(deltaPoro)
        self.editCondMax.setSingleStep(deltaCond)
        self.editCapMax.setSingleStep(deltaCapa)
        self.editDenMax.setSingleStep(deltaDens)
        
        self.editOutMesh.setText(self.outputmesh.toString())
    
    
    def editOutputMesh(self):
        diag = OutputMeshDialog(self, self.point, self.outputmesh)
        if diag.exec() == QtWidgets.QDialog.Accepted:
            self.outputmesh = diag.getOutputMesh()
            self.editOutMesh.setText(self.outputmesh.toString())

    def runModel(self):
        #self.runModelPerm()
        self.runModelTrans()

    def runModelPerm(self):
        thickness = self.outputmesh.max - self.outputmesh.min
        ncells = int(thickness / self.outputmesh.step) 
        dico = {
                    'depth': {
                        'val': thickness,
                         'unit': 'cm'
                    },
                    'ncells': ncells
               }
        rivBed = Column(dico)
        rivBed.printProps()
        
        perm = self.editPermeability.value()
        poro = self.editPorosity.value()
        cond = self.editSedThCond.value()
        capa = self.editSedThCap.value()
        dens = self.editDensity.value()
        dico = {
                    "name": "Soil Column",
                    "hydroParam": {
                        "hydro": {
                            "permeability" : {
                                "val" : perm,
                                "unit" : "m/s"
                            },
                            "porosity" : {
                                "val" : poro
                            }
                        }
                    },
                    "sedParam": {
                        "sediment": {
                            "specificHeatCapacity" : {
                                "val" : capa,
                                "unit" : "m2 s-2 K-1"
                            },
                            "lambda" : {
                                "val" : cond,
                                "unit": "W m-1 K-1"
                            },
                            "rho" : {
                                "val" : dens,
                                "unit" : "kg/m3"
                            }
                        }
                    }
                }
        physProp = PropPorousMedia.fromDict(dico)
        rivBed.setHomogeneousPorMedObj(physProp)
        rivBed.physProp.printProps()

        dico =  {
                    "dH" : {
                        "val": 5,
                        "unit": "cm"
                    }
                }
        bchyd = BoundaryConditionHyd.fromDict(dico)
        rivBed.setBcHydObj(bchyd)
        
        dico =  {
                    "Triv" : {
                        "val" : 29,
                        "unit" : "°C"
                    },
                    "Taq" : {
                        "val" : 12,
                        "unit" : "°C"
                    }
                }
        bcT = BoundaryConditionHeat.fromDict(dico)
        rivBed.setBcTObj(bcT)
                
        start = self.editStartDate.dateTime()
        end = self.editEndDate.dateTime()
        jf = start.daysTo(end)
        dj = 0.25 # TODO : use data time resolution ?
        dt = dj * NSECINDAY
        ndt = int( jf / dj )
        
        dico =  {
                    "Taverage": {
                        "val": 0,
                        "unit": "K"
                    },
                    "sinus": {
                        "Tampli": {
                            "val": 1,
                            "unit": "K"
                        },
                        "Period": {
                            "val": 30,
                            "unit": "j"
                        }
                    }
                }
        # https://stackoverflow.com/questions/8468756/converting-qdatetime-to-normal-python-datetime
        dates = ConvertDates(pd.date_range(start.toPyDateTime(), end.toPyDateTime(), ndt))
        z = rivBed.generateZAxis()
        bcts = BoundConditionSinus.fromDict(dico)
        allT = rivBed.calcTFromBcTSinusObj(bcts,ndt,dt)
        df = pd.DataFrame(allT,columns=z,index=dates).transpose()
        df.to_csv(self.study.resultPath(self.point,3))
        
        # Reload new points results
        self.parentWidget().loadResults()
        
    def runModelTrans(self):
        thickness = self.outputmesh.max - self.outputmesh.min
        ncells = int(thickness / self.outputmesh.step) 
        dico = {
                    'depth': {
                        'val': thickness,
                         'unit': 'cm'
                    },
                    'ncells': ncells
               }
        rivBed = Column(dico)
        rivBed.printProps()
        
        perm = self.editPermeability.value()
        poro = self.editPorosity.value()
        cond = self.editSedThCond.value()
        capa = self.editSedThCap.value()
        dens = self.editDensity.value()
        dico =  {
                    "name": "Soil Column",
                    "hydroParam": {
                        "hydro": {
                            "permeability" : {
                                "val" : perm,
                                "unit" : "m/s"
                            },
                            "porosity" : {
                                "val" : poro
                            }
                        }
                    },
                    "sedParam": {
                        "sediment": {
                            "specificHeatCapacity" : {
                                "val" : capa,
                                "unit" : "m2 s-2 K-1"
                            },
                            "lambda" : {
                                "val" : cond,
                                "unit": "W m-1 K-1"
                            },
                            "rho" : {
                                "val" : dens,
                                "unit" : "kg/m3"
                            }
                        }
                    }
                }
        physProp = PropPorousMedia.fromDict(dico)
        rivBed.setHomogeneousPorMedObj(physProp)
        rivBed.physProp.printProps()

        # TODO : Correct value of valQ ?
        #valQ = [1e-6, 0, -1e-6]  # m/s
        valQ = 0
        upperK = rivBed.physProp.propH.upperK
        grad = -valQ / upperK
        dh = -grad * rivBed.depth
        dico =  {
                    "dH" : {
                        "val": dh,
                        "unit": "cm"
                    }
                }
        bchyd = BoundaryConditionHyd.fromDict(dico)
        rivBed.setBcHydObj(bchyd)
        rivBed.printBcHydSteady()
        
        start = self.editStartDate.dateTime()
        end = self.editEndDate.dateTime()
        jf = start.daysTo(end)
        dj = 0.25 # TODO : Use data time resolution ?
        dt = dj * NSECINDAY
        ndt = int( jf / dj )
        
        dico =  {
                    "Taverage": {
                        "val": 12,
                        "unit": "°C"
                    },
                    "sinus": [ {
                        "Tampli": {
                            "val": 1,
                            "unit": "K"
                        },
                        "Period": {
                            "val": 30,
                            "unit": "j"
                        }
                    } ]
                }
        bcts = BoundConditionMultiSinus.fromDict(dico)
        rivBed.tempRiv = ph.CODE_HEAT
        rivBed.tempAq = ph.CODE_HEAT
        rivBed.tempAv = ph.CODE_HEAT
        allT = rivBed.calcTFromBcTSinusObj(bcts, ndt, dt)
        tempRiv = rivBed.calcBcTSinusObj(bcts, ndt, dt)
 
        dates = ConvertDates(pd.date_range(start.toPyDateTime(), end.toPyDateTime(), ndt))
        df = pd.DataFrame()
        df["DateTime"] = dates
        df["RiverTemp"] = tempRiv
        df.to_csv(self.study.resultPath(self.point,1))
        
        z = rivBed.generateZAxis()
        df = pd.DataFrame(allT,columns=z,index=dates).transpose()
        df.to_csv(self.study.resultPath(self.point,2))
        
        #Calculating fluxes
        #ncells = rivBed.ncells
        #adv = np.zeros(ndt,ncells)
        #cond = np.zeros(ndt,ncells)
        #deltaT = np.zeros(ndt,ncells)
        #deltaBil = np.zeros(ndt,ncells)
        #[adv,cond,deltaT, deltaBil] = rivBed.calcFluxFromBcTSinus(allT,tempRiv,valQ,ndt,dt,id)
        
        # TODO : Other results ?
        
        # Reload new points results
        self.parentWidget().loadResults()
        
    def runInversion(self):
        # TODO : Call the inversion
        QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Waraning','Not yet implemented!')
        