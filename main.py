from mesh import TetrahedronMesh
from PolyllaEdge import PolyllaEdge
from PolyllaFace import PolyllaFace
import sys
 

if __name__ == "__main__":
    #folder = "data\\"
    #file = "3D_100.1"
    #file = "socket.1"
    #file = "1000points07.1"

    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]

    filename = argument_list[0]
    outputname = argument_list[1]

    
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"

    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    
    polyllaEdge_mesh = PolyllaEdge(mesh)
    polyllaFace_mesh = PolyllaFace(mesh)
    
    #polyllaEdge_mesh.printOFF_polyhedralmesh(outputname + "POLYLLAEDGE.off")
    #polyllaFace_mesh.printOFF_polyhedralmesh(outputname + "POLYLLAFACE.off")

    mesh.get_info()
    polyllaEdge_mesh.get_info()
    polyllaFace_mesh.get_info()

