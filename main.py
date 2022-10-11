from mesh import TetrahedronMesh
from PolyllaEdge import PolyllaEdge
from PolyllaFace import PolyllaFace

if __name__ == "__main__":
    folder = "data\\"
    #file = "3D_100.1"
    file = "socket.1"
    filename = folder + file
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"

    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    
    polyllaEdge_mesh = PolyllaEdge(mesh)
    polyllaFace_mesh = PolyllaFace(mesh)
    
    mesh.get_info()
    polyllaEdge_mesh.get_info()
    polyllaFace_mesh.get_info()

