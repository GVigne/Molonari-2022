'''
Created on 15 mars 2021

@author: fors
'''

from numpy import NaN

class Sensor(object):
    '''
    classdocs
    '''

    def __init__(self, name="", intercept=NaN, dudh=NaN, dudt=NaN):
        self.name = name
        self.intercept = intercept
        self.dudh = dudh
        self.dudt = dudt
        
    def isValid(self):
        return True
    