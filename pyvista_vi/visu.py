import numpy as np
import pyvista as pv
from pyvista import examples
import tetgen
import meshio

filename = "socket.1.mesh"
mesh = pv.read(filename)
#mesh.plot(cpos="xy",  style='wireframe')

print(len(mesh.cells))
print(mesh.cell_data)
print(mesh.cells_dict)