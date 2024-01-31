from newMesh import FaceTetrahedronMesh, EdgeTetrahedronMesh, saveLog
from mesh import TetrahedronMesh
from PolyllaEdge import PolyllaEdge
from PolyllaFace import PolyllaFace
import time
import os

numVertices = 1000

filename = "data/"+ str(numVertices) + "random.1"
outputname = "data/"+ str(numVertices) + "random"
node_file = filename + ".node"
ele_file = filename + ".ele"
face_file = filename + ".face"
edge_file = filename + ".edge"


tf2 = time.time()
mesh = TetrahedronMesh(node_file, face_file, ele_file,edge_file)
polyllaFace_mesh_original = PolyllaFace(mesh)
tf3 = time.time()

t0 = time.time()
mesh_f = FaceTetrahedronMesh(node_file, face_file, ele_file)
polyllaFace_mesh_prueba = PolyllaFace(mesh_f)
tf1 = time.time()


saveLog('logs/tetra_prueba_log.txt',mesh_f.tetra_list)
saveLog('logs/tetra_mesh_log.txt',mesh.tetra_list)


print('Tiempo Sergio`s version:',tf3-tf2,'segs')
print('Tiempo Magda`s version:',tf1-t0,'segs')

print('\n Stats polylla original')

polyllaFace_mesh_original.get_info()
print('\n Stats polylla Prueba:')
polyllaFace_mesh_prueba.get_info()

filename_face = "logs/face_orig"+str(numVertices)+".off"
filename_face_poly = "logs/face_orig"+str(numVertices)+".off"
# polyllaFace_mesh_original.printOFF_polyhedralmesh(filename_face)

# polyllaFace_mesh_original.printOFF_polyhedralmesh(filename_face_poly)
filename_prueba = "logs/face_prueba"+str(numVertices)+".off"
filename_prueba2 = "logs/face_prueba_ccw"+str(numVertices)
filename_face_polyall= "face_polys"+str(numVertices)
polyllaFace_mesh_prueba.writePolygonFile(filename_face_polyall)

# polyllaFace_mesh_prueba.printOFF_each_poly(filename_prueba2)
# polyllaFace_mesh_prueba.printOFF_polyhedralmesh(filename_prueba)
# for i in range(len(polyllaFace_mesh_prueba.polyhedral_mesh)):
#     os.system("./../polyhedron_kernel-main/kernel "+ "logs/face_prueba_ccw"+str(numVertices)+str(i)+".off")

os.system("./kernel "+ filename_face_polyall +".txt")

# saveLog('logs/logFaceOrg.txt',mesh.face_list)
# saveLog('logs/logTetraOrg.txt',mesh.tetra_list)
# saveLog('logs/logFacePrueba.txt',mesh_f.face_list)
# saveLog('logs/logTetraPrueba.txt',mesh_f.tetra_list)
# saveLog('logs/logEdgeOrg.txt',mesh.edge_list)
# saveLog('logs/logEdgePrueba.txt',mesh_f.edge_list)

# vtk_to_obj('obj/20random')
# polyllaFace_mesh_prueba.polyhedron_area()