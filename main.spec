
dir_name = 'main'

added_files = []

# key goes (file to copy, path to move it to (relative to exe))
added_files.append(('assets/doge.ply', 'assets'))
added_files.append(('icon.ico', '.'))

a = Analysis(
    ["main.py"],
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
          name="DogeViewer",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='icon.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=dir_name)
