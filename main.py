#-*- coding: utf-8 -*-
import sys
import os
import mainWindow
from PyQt5.QtWidgets import *

if __name__ == "__main__":
    if os.path.exists("C:\OpenAPI")==False:
        os.startfile("OpenAPISetup.exe")
        app = QApplication(sys.argv)
        window = mainWindow.InstallAPIWindow()
        window.show()
        app.exec_()

    else:
        app = QApplication(sys.argv)
        window = mainWindow.MainWindow()
        window.show()
        app.exec_()
