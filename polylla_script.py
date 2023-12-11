from pruebaTetra import FaceTetrahedronMesh, EdgeTetrahedronMesh, saveLog
from mesh import TetrahedronMesh
from PolyllaEdge import PolyllaEdge
from PolyllaFace import PolyllaFace
import time
numVertices = 20

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


# polyllaEdge_mesh = PolyllaEdge(mesh)


saveLog('tetra_prueba_log.txt',mesh_f.tetra_list)
saveLog('tetra_mesh_log.txt',mesh.tetra_list)


print('Tiempo Sergio`s version:',tf3-tf2,'segs')
print('Tiempo Magda`s version:',tf1-t0,'segs')

print('\n Stats polylla original')

# polyllaEdge_mesh.get_info()

polyllaFace_mesh_original.get_info()
print('\n Stats polylla Prueba:')
polyllaFace_mesh_prueba.get_info()

filename_face = "logs/face_orig"+str(numVertices)
filename_face_poly = "logs/face_orig"+str(numVertices)
polyllaFace_mesh_original.printOFF_each_poly(filename_face)
# polyllaFace_mesh_original.printOFF_polyhedralmesh(filename_face_poly)
filename_prueba = "logs/face_prueba"+str(numVertices)
polyllaFace_mesh_prueba.printOFF_each_poly(filename_prueba)

saveLog('logFaceOrg.txt',mesh.face_list)
saveLog('logTetraOrg.txt',mesh.tetra_list)
saveLog('logFacePrueba.txt',mesh_f.face_list)
saveLog('logTetraPrueba.txt',mesh_f.tetra_list)
saveLog('logEdgeOrg.txt',mesh.edge_list)
saveLog('logEdgePrueba.txt',mesh_f.edge_list)