'''
Created on 3 mars 2021

@author: fors
'''

from datetime import date
from fileutil import FileExists
import geometry as geom

class Point(object):
    '''
    classdocs
    '''

    def __init__(self, name="", lastDate = date.today(), geometry = geom.Geometry()):
        self.name = name
        self.lastDate = lastDate
        self.geometry = geometry
        
    def isValid(self):
        return True
    
    def tempFileName(self):
        return "t_{}_{}_{}.csv".format(self.name, self.geometry.sensor.name, self.lastDate.toString("yyyy-MM-dd"))
    
    def pressFileName(self):
        return "p_{}_{}_{}.csv".format(self.name, self.geometry.sensor.name, self.lastDate.toString("yyyy-MM-dd"))
    
    def riverTempFileName(self):
        return "river_temp.csv"
    
    def tempProFileName(self):
        return "all_temp.csv"

    def waterVelFileName(self):
        return "water_vel.csv"
    
    def heatFlxFileName(self):
        return "heat_flx.csv"
        
class SourceFiles(object):
    '''
    classdocs
    '''
    def __init__(self, rawTempFile, rawPressFile, noticeFile, installFile, auxFiles=()):
        self.rawTempFile = rawTempFile
        self.rawPressFile = rawPressFile
        self.noticeFile = noticeFile
        self.installFile = installFile
        self.auxFiles = auxFiles
        
    def isValid(self):
        # TODO : check that files have the good format (extension ?)
        path = self.rawTempFile # CSV
        if not FileExists(path):
            return False
        path = self.rawPressFile # CSV
        if not FileExists(path):
            return False
        path = self.noticeFile # TXT
        if not FileExists(path):
            return False
        path = self.installFile # PNG
        if not FileExists(path):
            return False
        for path in self.auxFiles: # Whatever
            if not FileExists(path):
                return False
        return True
