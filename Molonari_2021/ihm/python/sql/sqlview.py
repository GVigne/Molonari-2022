import sys

from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

class PointsAndMeasures(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Display Points Measures")

        self.resize(550, 250)

        # Set up the view and load the data
        self.view = QTableWidget()
        self.view.setColumnCount(7)
        self.view.setHorizontalHeaderLabels(["ID", "Date", "Pressure", "Temp0", "Temp1", "Temp2", "Temp3", "Temp4"])
        
        query = QSqlQuery("SELECT date, p, t0, t1, t2, t3, t4 FROM measures")
        date, p, t0, t1, t2, t3, t4 = range(7)
        while query.next() :
            print("  ", query.value(date), query.value(p), query.value(t0), query.value(t1), query.value(t2), query.value(t3), query.value(t4))
            rows = self.view.rowCount()
            self.view.setRowCount(rows + 1)
            self.view.setItem(rows, 0, QTableWidgetItem(str(query.value(date))))
            self.view.setItem(rows, 1, QTableWidgetItem(str(query.value(p))))
            self.view.setItem(rows, 2, QTableWidgetItem(str(query.value(t0))))
            self.view.setItem(rows, 3, QTableWidgetItem(str(query.value(t1))))
            self.view.setItem(rows, 4, QTableWidgetItem(str(query.value(t2))))
            self.view.setItem(rows, 5, QTableWidgetItem(str(query.value(t3))))
            self.view.setItem(rows, 6, QTableWidgetItem(str(query.value(t4))))

        query.finish()
        self.view.resizeColumnsToContents()
        self.setCentralWidget(self.view)


def createConnection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("molonari.sqlite")
    if not con.open():
        QMessageBox.critical(
            None,
            "Display Points Measures - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True

app = QApplication(sys.argv)
if not createConnection():
    sys.exit(1)

win = PointsAndMeasures()
win.show()

sys.exit(app.exec_())

