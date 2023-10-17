# Setting the Qt bindings for QtPy
import os
import sys

os.environ["QT_API"] = "pyqt5"

import numpy as np
import pyvista as pv
from pyvistaqt import MainWindow, QtInteractor
from qtpy import QtGui, QtWidgets
from pyvistaqt.dialog import ScaleAxesDialog
from pyvistaqt.utils import _create_menu_bar


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

        self.plotter.app_window = self

        # simple menu to demo functions
        self.main_menu = _create_menu_bar(self)
        file_menu = self.main_menu.addMenu("File")
        exitButton = QtWidgets.QAction("Exit", self)
        exitButton.setShortcut("Ctrl+Q")
        exitButton.triggered.connect(self.close)
        file_menu.addAction(exitButton)

        view_menu = self.main_menu.addMenu("View")
        view_menu.addAction("Clear", self.plotter.clear_actors)
        view_menu.addAction("Scale Axes", self.scale_axes_dialog)

        # App specific
        self.plotter.main_menu = self.main_menu

        if show:
            self.show()

    def scale_axes_dialog(self, show: bool = True) -> ScaleAxesDialog:
        """Open scale axes dialog."""
        return ScaleAxesDialog(self, self.plotter, show=show)


if __name__ == "__main__":
    from script import bind_to_plotter
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    bind_to_plotter(window.plotter)
    sys.exit(app.exec_())
