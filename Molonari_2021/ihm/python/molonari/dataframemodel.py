import pandas as pd

from PyQt5 import QtCore, QtWidgets

# https://stackoverflow.com/questions/31475965/fastest-way-to-populate-qtableview-from-pandas-data-frame
# https://stackoverflow.com/questions/58234343/display-pandas-dataframe-in-tableview-in-pyqt5-where-column-is-set-as-index
class DataFrameModel(QtCore.QAbstractTableModel):
    '''
    classdocs
    '''
    def __init__(self, df=pd.DataFrame(), parent=None):
        # This is equivalent to
        #QtCore.QAbstractTableModel.__init__(self, parent)
        super(DataFrameModel, self).__init__(parent)
        self.dataFrame = df

    @classmethod
    def fromCSV(cls, fileName, skiprows=0, header=1, index_col=None, parent=None):
        df = None
        file = QtCore.QFile(fileName)
        if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtWidgets.QMessageBox.critical(QtWidgets.qApp.activeWindow(),"Error while loading:{}".format(fileName))
            return DataFrameModel()
        with open(fileName, "r") as fileInput:
            df = pd.read_csv(fileInput, skiprows=skiprows, header=header, index_col=index_col) # Header is first line
        return cls(df, parent)
        
    def setDataFrame(self, df):
        self.beginResetModel()
        self.dataFrame = df.copy()
        self.endResetModel()

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.dataFrame.columns[section]
            else:
                return str(self.dataFrame.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.dataFrame.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self.dataFrame.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(self.dataFrame.values[index.row()][index.column()]))
            # other roles (i.e. : editing) look at stackoverflow
        return QtCore.QVariant()
