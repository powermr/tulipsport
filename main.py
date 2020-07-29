import sys
import untitled
import main_window
from PyQt5.QtWidgets import  QApplication,QMainWindow,QDialog

if __name__ == '__main__':
    app=QApplication(sys.argv)
    # MainWindow=QMainWindow()

    qDialog=QDialog()
    ui=main_window.Ui_Dialog()
    ui.setupUi(qDialog)
    qDialog.show()
    sys.exit(app.exec_())
