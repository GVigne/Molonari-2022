'''
Created on 16 mars 2021

@author: fors
'''

class OutputMesh(object):
    '''
    Depth in centimeters
    '''

    def __init__(self, depthmin=0.0, depthmax=0.0, depthstep=1.0):
        self.min = depthmin
        self.max = depthmax
        self.step = depthstep
        
    def isValid(self):
        # TODO : check that depths are consistents
        return True
    
    def toString(self):
        return "Min={} - Max={} - Step={}".format(self.min, self.max, self.step)
