a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    hiddenimports=[
        "vtkmodules",
        "vtkmodules.all",
        "vtkmodules.qt.QVTKRenderWindowInteractor",
        "vtkmodules.util",
        "vtkmodules.util.numpy_support",
        "vtkmodules.numpy_interface.dataset_adapter",
        "vtkmodules.vtkFiltersGeneral",
    ],
)
