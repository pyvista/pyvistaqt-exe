# Setting the Qt bindings for QtPy
import os
import sys

os.environ["QT_API"] = "pyqt5"

import numpy as np
import pyvista as pv
from pyvistaqt import MainWindow, QtInteractor
from pyvistaqt.dialog import ScaleAxesDialog
from pyvistaqt.utils import _create_menu_bar
from qtpy import QtGui, QtWidgets


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
        view_menu.addAction("Clear", self.plotter.clear)
        view_menu.addAction("Scale Axes", self.scale_axes_dialog)

        view_menu.addSeparator()
        # Orientation marker
        orien_menu = view_menu.addMenu("Orientation Marker")
        orien_menu.addAction("Show All", self.plotter.show_axes_all)
        orien_menu.addAction("Hide All", self.plotter.hide_axes_all)
        # Bounds axes
        axes_menu = view_menu.addMenu("Bounds Axes")
        axes_menu.addAction("Add Bounds Axes (front)", self.plotter.show_bounds)
        axes_menu.addAction("Add Bounds Grid (back)", self.plotter.show_grid)
        axes_menu.addAction("Add Bounding Box", self.plotter.add_bounding_box)
        axes_menu.addSeparator()
        axes_menu.addAction("Remove Bounding Box", self.plotter.remove_bounding_box)
        axes_menu.addAction("Remove Bounds", self.plotter.remove_bounds_axes)

        cam_menu = view_menu.addMenu("Camera")
        self._parallel_projection_action = cam_menu.addAction(
            "Toggle Parallel Projection", self._toggle_parallel_projection
        )

        # App specific
        self.plotter.main_menu = self.main_menu

        if show:
            self.show()

    def scale_axes_dialog(self, show: bool = True) -> ScaleAxesDialog:
        """Open scale axes dialog."""
        return ScaleAxesDialog(self, self.plotter, show=show)

    def _toggle_parallel_projection(self) -> None:
        if self.plotter.camera.GetParallelProjection():
            return self.plotter.disable_parallel_projection()
        return self.plotter.enable_parallel_projection()


if __name__ == "__main__":
    from script import bind_to_plotter

    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()
    bind_to_plotter(window.plotter)
    sys.exit(app.exec_())
