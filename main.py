# Setting the Qt bindings for QtPy
import os
import sys

os.environ["QT_API"] = "pyqt5"

import numpy as np
import pyvista as pv
from pyvistaqt import MainWindow, QtInteractor
from qtpy import QtGui, QtWidgets

import PVGeo
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from matplotlib.colors import ListedColormap
from scipy.stats import entropy


def resource_path(relative_path=""):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)


class MyMainWindow(MainWindow):
    def __init__(self, parent=None, show=True):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.setWindowIcon(QtGui.QIcon("icon.ico"))

        # create the frame
        self.frame = QtWidgets.QFrame()
        vlayout = QtWidgets.QVBoxLayout()

        # add the pyvista interactor object
        self.plotter = QtInteractor(self.frame)
        vlayout.addWidget(self.plotter.interactor)
        self.signal_close.connect(self.plotter.close)

        self.frame.setLayout(vlayout)
        self.setCentralWidget(self.frame)

        # simple menu to demo functions
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        exitButton = QtWidgets.QAction("Exit", self)
        exitButton.setShortcut("Ctrl+Q")
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        clr_menu = mainMenu.addMenu("Clear")
        clr_menu.addAction("Clear", self.plotter.clear_actors)

        self.plotter.main_menu = mainMenu

        if show:
            self.show()


if __name__ == "__main__":
    from script import bind_to_plotter
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    bind_to_plotter(window.plotter)
    sys.exit(app.exec_())
