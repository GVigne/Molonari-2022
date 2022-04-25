from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
import os

from .bestParametersDb import BestParametersDb
from .cleanedMeasuresDb import CleanedMeasuresDb
from .newDateDb import NewDateDb
from .depthDb import DepthDb
from .directParametersDb import DirectParametersDb
from .laboDb import LaboDb
from .layerDb import LayerDb
from .parametersDistributionDb import ParametersDistributionDb
from .pointDb import PointDb
from .pressureSensorDb import PressureSensorDb
from .quantileDb import QuantileDb
from .rawMeasuresPressDb import RawMeasuresPressDb
from .rawMeasuresTempDb import RawMeasuresTempDb
from .rmseDb import RMSEDb
from .samplingPointDb import SamplingPointDb
from .shaftDb import ShaftDb
from .studyDb import StudyDb
from .temperatureAndHeatFlowsDb import TemperatureAndHeatFlowsDb
from .thermometerDb import ThermometerDb
from .waterFlowDb import WaterFlowDb


class MainDb():
    def __init__(self, con) -> None:
        self.con = con
        
        
        self.bestParametersDb = BestParametersDb(self.con)
        self.cleanedMeasuresDb = CleanedMeasuresDb(self.con)
        self.dateDb = NewDateDb(self.con)
        self.depthDb = DepthDb(self.con)
        self.directParametersDb = DirectParametersDb(self.con)
        self.laboDb = LaboDb(self.con)
        self.layerDb = LayerDb(self.con)
        self.parametersDistribution = ParametersDistributionDb(self.con)
        self.pointDb = PointDb(self.con)
        self.pressureSensorDb = PressureSensorDb(self.con)
        self.quantileDb = QuantileDb(self.con)
        self.rawMeasuresPressDb = RawMeasuresPressDb(self.con)
        self.rawMeasuresTempDb = RawMeasuresTempDb(self.con)
        self.rmseDb = RMSEDb(self.con)
        self.samplingPointDb = SamplingPointDb(self.con)
        self.shaftDb = ShaftDb(self.con)
        self.studyDb = StudyDb(self.con)
        self.temperatureAndHeatFlowsDb = TemperatureAndHeatFlowsDb(self.con)
        self.thermometerDb = ThermometerDb(self.con)
        self.waterFlowDb = WaterFlowDb(self.con)
        
        
    def createTables(self):
        self.thermometerDb.create()
        self.laboDb.create()
        self.studyDb.create()
        self.shaftDb.create()
        self.pressureSensorDb.create()
        self.samplingPointDb.create()
        self.rawMeasuresPressDb.create()
        self.rawMeasuresTempDb.create()
        self.cleanedMeasuresDb.create()
        self.pointDb.create()
        self.dateDb.create()
        self.quantileDb.create()
        self.layerDb.create()
        self.bestParametersDb.create()
        self.depthDb.create()
        self.directParametersDb.create()
        self.parametersDistribution.create()
        self.temperatureAndHeatFlowsDb.create()
        self.waterFlowDb.create()
        self.rmseDb.create()
