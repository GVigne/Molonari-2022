'''
Created on 14 janv. 2021

@author: fors
'''

# importing os and shutil module 
import os

class Preferences(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''self.sensorDir = ""'''
        self.valid = False
        self.load()
    
    def isValid(self):
        return self.valid
    
    def load(self):
        '''
        path = os.path.join(os.path.expanduser("~"),"molonaviz.txt")
        self.valid = False
        nbPref = 0 # Check total number of preferences below
        try:
            file = open(path,"r")
            lines = file.readlines()
            for line in lines:
                if line.split('=')[0].strip() == "SensorDir":
                    self.sensorDir = line.split('=')[1].strip()
                    nbPref = nbPref + 1
        except IOError:
            return False
        file.close()
        self.valid = (nbPref == 1) # Here
        '''
        self.valid = True
        return self.isValid()

    def save(self):
        '''
        path = os.path.join(os.path.expanduser("~"),"molonaviz.txt")
        file = open(path,"w")
        file.write("SensorDir = {}\n".format(self.sensorDir))
        file.close()
        '''
        return self.load()
    
    def update(self, newPref):
        '''self.sensorDir = newPref.sensorDir'''
        self.valid = newPref.valid
        return self.save()