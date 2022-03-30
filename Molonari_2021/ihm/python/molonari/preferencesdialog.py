'''
Created on 14 janv. 2021

@author: fors
'''
import os

from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic

import preferences as pre

From_PreferencesDialog,_= uic.loadUiType(os.path.join(os.path.dirname(__file__),"preferencesdialog.ui"))
class PreferencesDialog(QtWidgets.QDialog,From_PreferencesDialog):
    '''
    classdocs
    '''
    def __init__(self, parent):
        super(PreferencesDialog, self).__init__()
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)               

    def getPreferences(self):
        pref = pre.Preferences()
        return pref
        