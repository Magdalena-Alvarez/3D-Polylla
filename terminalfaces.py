# TODO
#falta agregar el caso de que sea una cara de borde

# Se compila con
# ./tetgenex -fznn 3D_100.node && python3 terminalfaces.py      

import numpy as np
import sys

class vertex:
    def __init__(self, i, x, y, z):
        self.i = i
        self.x = x
        self.y = y
        self.z = z

class face:
    def __init__(self, i, v1, v2, v3, boundary, n1, n2 ):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.is_boundary = boundary
        self.n1 = n1
        self.n2 = n2
    

class Tetrahedron:
    def __init__(self, i, v1, v2, v3, v4):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.neighs = []
        self.is_boundary = False
        self.faces = []


class TetrahedronMesh:
    def __init__(self, node_file, face_file, tetra_file):
        self.node_list, self.face_list, self.tetra_list = self.construct_tetrahedral_mesh(node_file, face_file, tetra_file)
        self.n_tetrahedrons = len(self.tetra_list)
        self.n_faces = len(self.face_list)
        self.n_nodes = len(self.node_list)


    def read_node_file(self, filename):
        print("reading node file: "+ filename)
        f = open(filename, "r")
        node_list = []
        next(f)
        for line in f:
            line = line.split()
            #v1, v2, v3, boundary_marker
            if line[0] != '#':
                node_temp = vertex(int(line[0]), float(line[1]), float(line[2]), float(line[3]))
                node_list.append(node_temp)
        f.close()
        return node_list

    def read_face_file(self, filename):
        print("reading face file: "+ filename)
        f = open(filename, "r")
        face_list = []
        next(f)
        for line in f:
            line = line.split()
            ## v1, v2, v3, boundary_marker, n1, n2
            if line[0] != '#':
                v1 = int(line[1])
                v2 = int(line[2])
                v3 = int(line[3])
                boundary_marker = (int(line[4]) == 1 or int(line[4]) == -1)
                n1 = int(line[5])
                n2 = int(line[6])
                face_temp = face(int(line[0]), v1, v2, v3, boundary_marker, n1, n2)
                face_list.append(face_temp)
        f.close()
        return face_list

    def read_ele_file(self, filename):
        print("reading ele file: "+ filename)
        f = open(filename, "r")
        tetrahedron_list = []
        next(f)
        for line in f:
            line = line.split()
            #v1, v2, v3, v4
            if line[0] != '#':
                tetra_temp = Tetrahedron(int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]))
                tetrahedron_list.append(tetra_temp)
        f.close()
        return tetrahedron_list



    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file):
        node_list = self.read_node_file(node_file)
        face_list = self.read_face_file(face_file)
        tetra_list = self.read_ele_file(ele_file)

        # Calculas caras de cada tetrahedro
        for f in range(0, len(face_list)):
            # Calcula neigh tetrahedras from faces
            neigh1 = face_list[f].n1
            neigh2 = face_list[f].n2
            if neigh1 != -1:
                tetra_list[neigh1].faces.append(f)
                #tetra_list[neigh1].is_boundary = face_list[f].is_boundary
            if neigh2 != -1:
                tetra_list[neigh2].faces.append(f)
                #tetra_list[neigh2].is_boundary = face_list[f].is_boundary
            #falta agregar el caso de que sea una cara de borde

        # Calcula los tetrahedros vecinos
        for tetra in tetra_list:
            for f in tetra.faces:
                neighs = [face_list[f].n1, face_list[f].n2]
                curr_tetra = tetra.i
                neigh_tetra = neighs[0] if neighs[0] != curr_tetra else neighs[1]
                tetra.neighs.append(neigh_tetra)

        # Imprime los tetrahedros
        for t in range(0, len(tetra_list)):
            print("tetrahedron ", t, ":", tetra_list[t].v1, tetra_list[t].v2, tetra_list[t].v3, tetra_list[t].v4, tetra_list[t].faces, tetra_list[t].neighs, tetra_list[t].is_boundary)

        return node_list, face_list, tetra_list

def printOFF_faces(filename, vertices, faces):
    print("writing OFF file: "+ filename)
    with open(filename, 'w') as fh:
        fh.write("OFF\n")
        fh.write("%d %d 0\n" % (len(vertices), len(faces)))
        for v in vertices:
            fh.write("%f %f %f\n" % (v.x, v.y, v.z))
        for f in faces:
            fh.write("3 %d %d %d\n" % (f.v1, f.v2, f.v3))

def calculate_area_triangle_3d(v1, v2, v3):
    av1 = np.array([v1.x, v1.y, v1.z])
    av2 = np.array([v2.x, v2.y, v2.z])
    av3 = np.array([v3.x, v3.y, v3.z])
    a = np.linalg.norm(np.cross(av2-av1, av3-av1))
    return a/2

def calculate_max_faces(mesh):
    longest = []
    for tetra in mesh.tetra_list:

        # Calcula el area de cada cara
        f1 = mesh.face_list[tetra.faces[0]]
        f2 = mesh.face_list[tetra.faces[1]]
        f3 = mesh.face_list[tetra.faces[2]]
        f4 = mesh.face_list[tetra.faces[3]]

        a0 = calculate_area_triangle_3d(mesh.node_list[f1.v1], mesh.node_list[f1.v2], mesh.node_list[f1.v3])
        a1 = calculate_area_triangle_3d(mesh.node_list[f2.v1], mesh.node_list[f2.v2], mesh.node_list[f2.v3])
        a2 = calculate_area_triangle_3d(mesh.node_list[f3.v1], mesh.node_list[f3.v2], mesh.node_list[f3.v3])
        a3 = calculate_area_triangle_3d(mesh.node_list[f4.v1], mesh.node_list[f4.v2], mesh.node_list[f4.v3])

        if a0 >= a1 and a0 >= a2 and a0 >= a3:
            longest.append(0)
        elif a1 >= a0 and a1 >= a2 and a1 >= a3:
            longest.append(1)
        elif a2 >= a0 and a2 >= a1 and a2 >= a3:
            longest.append(2)
        elif a3 >= a0 and a3 >= a1 and a3 >= a2:
            longest.append(3)
        else:
            print("Error")
            
    return longest    


# Retorna la cara maś larga como objeto cara
def calculate_terminal_faces(mesh, longest):
    terminal_faces = []
    for tetra in range(0, mesh.n_tetrahedrons):
        # Calcula la cara más larga del tetrahedro tetra
        longest_face_curr = mesh.face_list[mesh.tetra_list[tetra].faces[longest[tetra]]]
        #Calcula el vecino de lface1
        neigh = mesh.tetra_list[tetra].neighs[longest[tetra]]

        #Revisa cuál es la cara más larga del tetrahedro vecino con la cara más larga
        longest_face_neigh = mesh.face_list[mesh.tetra_list[neigh].faces[longest[neigh]]]

        #Si es terminal-border
        if longest_face_neigh == -1:
            terminal_faces.append(longest_face_curr)
        # Si ambas caras son la más larga, entonces es una cara cara terminal
        elif longest_face_curr == longest_face_neigh:
            terminal_faces.append(longest_face_curr)
    return terminal_faces

# Retorna un bitvector de largo n_faces que indica si la cara es frontier-face o no
def calculate_frontier_faces(mesh, longest):
    frontier_faces = []
    for f in range(0, len(mesh.face_list)):
        n1 = mesh.face_list[f].n1
        n2 = mesh.face_list[f].n2

        # Si la cara es de borde, es una frontier-edge
        if n1 == -1 or n2 == -1:
            frontier_faces.append(True) # True para imprimir caras de borde
        else: 
            longest_face_n1 = mesh.face_list[mesh.tetra_list[n1].faces[longest[n1]]]
            longest_face_n2 = mesh.face_list[mesh.tetra_list[n2].faces[longest[n2]]]

            # Si no es la cara más larga de ningún tetra de n1 o n2, es una frontier-edge
            if (mesh.face_list[f] != longest_face_n1 and mesh.face_list[f] != longest_face_n2): 
                frontier_faces.append(True)
            else:
                frontier_faces.append(False)

    return frontier_faces
    

def DepthFirstSearch(polyhedron, visited_tetra, tetra, frontier_faces, mesh):
    visited_tetra[tetra.i] = True
    for i in range(0, 4):
        face_id = tetra.faces[i]
        if face_id != -1:
            if frontier_faces[face_id] == True:
                fa = mesh.face_list[face_id]
                polyhedron.append(fa)
            else:
                next_tetra = mesh.tetra_list[tetra.neighs[i]]
                if(visited_tetra[next_tetra.i] == False):
                    DepthFirstSearch(polyhedron, visited_tetra, next_tetra, frontier_faces, mesh)
    
# Genera un polígono con las frontier-faces como caras y la terminal_face como generador de la cara
def generate_polyhedra_from_terminal_face(terminal_face, bitvector_frontier_edges, mesh):

    visited_tetra = [False] * mesh.n_tetrahedrons
    terminal_tetra = mesh.tetra_list[mesh.face_list[terminal_face.i].n1 if mesh.face_list[terminal_face.i].n1 != -1 else mesh.face_list[terminal_face.i].n2]
    #print(terminal_tetra.faces)
    polyhedron = []
    DepthFirstSearch(polyhedron, visited_tetra, terminal_tetra, bitvector_frontier_edges, mesh)
    
    #print("polyhedron: ", len(polyhedron))
    return polyhedron


if __name__ == "__main__":
    
    filename = sys.argv[1]
    #filename = "3D_100.1"
    #filename = "Models/dragon.1"
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    mesh = TetrahedronMesh(node_file, face_file, ele_file)
    #printOFF_faces(filename + ".off", mesh.node_list, mesh.face_list)

    # Calculate longest-faces
    longest_faces =  calculate_max_faces(mesh)
    terminal_faces = calculate_terminal_faces(mesh, longest_faces)

    printOFF_faces(filename + "_terminal.off", mesh.node_list, terminal_faces)

    bitvector_frontier_edges = calculate_frontier_faces(mesh, longest_faces)

    frontier_faces = []
    for i in range(0, len(mesh.face_list)):
        if bitvector_frontier_edges[i] == False:
            frontier_faces.append(mesh.face_list[i])


    printOFF_faces(filename + "_frontier.off", mesh.node_list, frontier_faces)
    #calculate terminal-faces
    for i in range(0,20):
	    polyhedron = generate_polyhedra_from_terminal_face(terminal_faces[i], bitvector_frontier_edges, mesh)
    #print("f1", terminal_faces[1].v1, terminal_faces[1].v2, terminal_faces[1].v3, "f2", terminal_faces[19].v1, terminal_faces[19].v2, terminal_faces[19].v3)
	    printOFF_faces(filename + "_" + str(i) + "_poly.off", mesh.node_list, polyhedron)

