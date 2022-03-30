import sys
from PyQt5 import QtWidgets, uic, QtCore
import pandas as pd
Qt = QtCore.Qt

class PandasModel(QtCore.QAbstractTableModel):

    def __init__(self, df=pd.DataFrame(), parent=None): #idée : initialiser le modèle avec un dataframe plutôt qu'un csv
        # permet de mieux gérer les formats de csv différents
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.df = df

    def headerData(self, section, orientation = QtCore.Qt.Horizontal, role=QtCore.Qt.DisplayRole):
        
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return self.df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def columnCount(self, parent=None):
        return self.df.columns.size

    def rowCount(self, parent=None):
        return len(self.df.values)
    
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return QtCore.QVariant(str(self.df.iloc[index.row()][index.column()]))
        return QtCore.QVariant()
    
    def setData(self, df):
        self.beginResetModel()
        self.df = df.copy()
        self.endResetModel()
    
    def getpdData(self):
        return(self.df)
