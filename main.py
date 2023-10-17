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


DOGE_FILE = resource_path(os.path.join("assets", "doge.ply"))
ICON_FILE = resource_path(os.path.join(".", "icon.ico"))


class MyMainWindow(MainWindow):
    """Extandable MainWindow for PyVistaQt standalone applications."""
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
        self.main_menu = _create_menu_bar(self)
        self.add_menus()

        if show:
            self.show()

    def add_menus(self):
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

    def scale_axes_dialog(self, show: bool = True) -> ScaleAxesDialog:
        """Open scale axes dialog."""
        self.plotter.app_window = self  # HACK
        return ScaleAxesDialog(self, self.plotter, show=show)

    def _toggle_parallel_projection(self) -> None:
        if self.plotter.camera.GetParallelProjection():
            return self.plotter.disable_parallel_projection()
        return self.plotter.enable_parallel_projection()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow()

    # Custom application logic
    def add_doge():
        window.plotter.add_mesh(pv.read(DOGE_FILE), color="tan", name="doge")
        window.plotter.camera_position = [
            (45.3316, -15.7107, 95.7495),
            (-0.2799, -0.1400, 0.6100),
            (-0.1308, 0.9665, 0.2209),
        ]

    mesh_menu = window.main_menu.addMenu("Mesh")
    add_doge_action = QtWidgets.QAction("Add Doge", window)
    add_doge_action.triggered.connect(add_doge)
    mesh_menu.addAction(add_doge_action)

    sys.exit(app.exec_())
