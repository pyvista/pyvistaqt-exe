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


DOGE_FILE = resource_path(os.path.join("assets", "doge.ply"))
ICON_FILE = resource_path(os.path.join(".", "icon.ico"))


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

        # allow adding a sphere
        meshMenu = mainMenu.addMenu("Mesh")
        self.add_sphere_action = QtWidgets.QAction("Add Sphere", self)
        self.add_sphere_action.triggered.connect(self.add_sphere)
        meshMenu.addAction(self.add_sphere_action)

        # demonstrate using a built-in asset
        self.plotter.add_mesh(pv.read(DOGE_FILE), color="tan")

        if show:
            self.show()

    def add_sphere(self):
        """add a sphere to the pyqt frame"""
        sphere = pv.Sphere()
        self.plotter.add_mesh(sphere, show_edges=True)
        self.plotter.reset_camera()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    sys.exit(app.exec_())
