import pyvista as pv

mesh = pv.Wavelet()

pl = pv.Plotter()
pl.add_mesh(mesh)
pl.show()
