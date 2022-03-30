'''
Created on 7 janv. 2021

@author: fors
'''

from PyQt5 import QtWidgets, QtCore

class Geometry(object):
    '''
    Depth in centimeters
    '''

    def __init__(self, sensor=None, riverDepth=0.0, hyporheicDepth=0.0, tempDepths=()):
        self.sensor = sensor
        self.riverDepth = riverDepth
        self.hyporheicDepth = hyporheicDepth
        self.tempDepths = tempDepths
        
    # https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
    @classmethod
    def load(cls, path, sensorModel):
        try:
            file = open(path,"r")
            lines = file.readlines()
            lst = sensorModel.findItems(lines[1].strip());
            if (len(lst) != 1):
                QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Unknown sensor in geometry file!')
                return Geometry()
            sensor = lst[0].data(QtCore.Qt.UserRole)
            riverDepth = float(lines[3].strip())
            hyporheicDepth = float(lines[5].strip())
            tempDepths = list(map(float, lines[7].strip().split(';')))
        except IOError:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Geometry file not valid!')
            return Geometry()
        except ValueError:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Geometry file not valid!')
            return Geometry()
        file.close()
        return cls(sensor, riverDepth, hyporheicDepth, tempDepths)
    
    def write(self, path):
        try:
            file = open(path,"w")
            file.write(self.toStringFile())
        except IOError:
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),'Error','Geometry file not witable!')
            return False
        file.close()
        return True

    def isValid(self):
        if (self.sensor == None):
            return False
        # TODO : Check that depths are consistents (increasing)
        return True
    
    def toStringFile(self):
        sf = "#pressure_sensor\n"
        sf += "{}\n".format(self.sensor.name)
        sf += "#depth river bed - river tube [cm]\n"
        sf += "{}\n".format(self.riverDepth)
        sf += "#depth river bed - hyporheic tube [cm]\n"
        sf += "{}\n".format(self.hyporheicDepth)
        sf += "#temperature_depths[cm]\n"
        sf += "{}\n".format(';'.join(str(d) for d in self.tempDepths))
        return sf
    
    def toString(self):
        return "[{}]".format(' | '.join(str(d) for d in self.tempDepths))
            
    def toStringList(self):
        return list(str(d)+'cm' for d in self.tempDepths)