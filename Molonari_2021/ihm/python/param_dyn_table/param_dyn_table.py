import sys, os
# Import PyQt sub-modules
from PyQt5 import QtWidgets, uic

From_param_dyn_table = uic.loadUiType(os.path.join(os.path.dirname(__file__),"param_dyn_table.ui")) 

class ParamDynTable(From_param_dyn_table[0], From_param_dyn_table[1]):
    """
    """
    def __init__(self, maxDepth):
        """
        Constructor
        """
        # Call the constructor of parent classes (super)
        super(ParamDynTable, self).__init__()
        # Configure the initial values of graphical controls 
        # See https://doc.qt.io/qt-5/designer-using-a-ui-file-python.html
        self.setupUi(self)
        
        # Start with 0 layers
        self.nblayers = 0
        self.maxDepth = maxDepth
        self.defaultParams = [0.5, 1.5, 405.0]
        
        # Connect buttons
        self.pushButtonPlus.clicked.connect(self.onPlus)
        self.pushButtonMinus.clicked.connect(self.onMinus)
        
        # Then add one layer
        self.addLayer()
        

    def addLayer(self):
        # Append a row
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        item = QtWidgets.QTableWidgetItem(f"Layer #{self.nblayers}")
        self.tableWidget.setVerticalHeaderItem(self.tableWidget.rowCount()-1, item)
        # Always use maximum depth for last layer
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, 
                                 QtWidgets.QTableWidgetItem(str(self.maxDepth)))
        
        # Update previous last layer depth
        if self.nblayers > 0:
            new_depth = self.maxDepth / 2
            if self.nblayers > 1:
                new_depth = float(self.tableWidget.item(self.tableWidget.rowCount()-3, 0).text())
                new_depth = new_depth + (self.maxDepth - new_depth) / 2
            self.tableWidget.setItem(self.tableWidget.rowCount()-2, 0, 
                                     QtWidgets.QTableWidgetItem(str(new_depth)))
            
        # Set new layer values (duplicate from previous layer)
        if self.nblayers == 0:
            values = self.defaultParams
        else:
            values = [float(self.tableWidget.item(self.tableWidget.rowCount()-2, 1).text()),
                      float(self.tableWidget.item(self.tableWidget.rowCount()-2, 2).text()),
                      float(self.tableWidget.item(self.tableWidget.rowCount()-2, 3).text())]
            
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 1,
                                 QtWidgets.QTableWidgetItem(str(values[0])))
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 2,
                                 QtWidgets.QTableWidgetItem(str(values[1])))
        self.tableWidget.setItem(self.tableWidget.rowCount()-1, 3,
                                 QtWidgets.QTableWidgetItem(str(values[2])))
        
        # Update layer number
        self.nblayers = self.nblayers + 1
        self.lineEditNLayers.setText(str(self.nblayers))

        
    def removeLayer(self):
        if (self.nblayers > 1) :
            # Remove last row
            self.tableWidget.removeRow(self.tableWidget.rowCount()-1)
            # Always use maximum depth for last layer
            self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0,
                                     QtWidgets.QTableWidgetItem(str(self.maxDepth)))
            # Update layer number
            self.nblayers = self.nblayers - 1
            self.lineEditNLayers.setText(str(self.nblayers))


    def onPlus(self):
        self.addLayer()
        
    def onMinus(self):
        self.removeLayer()
        
        
if __name__ == '__main__':
    """
    Main function of the script:
    - Create the QApplication object
    - Create the TemperatureViewer dialog and show it
    - Execute the infinite event loop and wait for interaction or exit
    """
    app = QtWidgets.QApplication(sys.argv)

    maxDepth = 46.0
    mainWin = ParamDynTable(maxDepth)
    mainWin.show()

    sys.exit(app.exec_())
    
