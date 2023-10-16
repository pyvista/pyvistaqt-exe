
dir_name = 'main'

added_files = []

a = Analysis(
    ["main.py", "script.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        "vtkmodules",
        "vtkmodules.all",
        "vtkmodules.qt.QVTKRenderWindowInteractor",
        "vtkmodules.util",
        "vtkmodules.util.numpy_support",
        "vtkmodules.numpy_interface.dataset_adapter",
        "vtkmodules.vtkFiltersGeneral",
        "scipy.stats"
        "pandas",
    ],
)
block_cipher = None
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name="GIVAViewer",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=dir_name)
