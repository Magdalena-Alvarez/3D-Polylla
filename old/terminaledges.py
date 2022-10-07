# TODO
#falta agregar el caso de que sea una cara de borde

# Se compila con
# ./tetgenex -fnn 3D_100.node && python3 terminalfaces.py    
# para edges s  

# TODO
# Sacar de la funcion de hacer mesh tetrahedral los arcos mas largos y el arco mas largo de todo el conjunto
# Revisar si es mejor ponerlas como parametros de las clases o dejarlos como listas afuera

from collections import Counter
from operator import index
from typing import List, Dict
import numpy as np
import sys
import math

class Vertex:
    def __init__(self, i, x, y, z):
        self.i = i
        self.x = x
        self.y = y
        self.z = z

# class for edges and calculating the tetrahedron neighbours that
# share said edge
class Edge:
    def __init__(self, index, end_point1, end_point2) -> None:
        self.i = index
        self.e1 = end_point1
        self.e2 = end_point2
        self.tetrahedron_neighbours = set()
        self.tetrahedron = -1
        self.is_boundary = -1
        self.tetrahedron_list : List[Tetrahedron] = []
        # Length is saved for the polyhedralization process
        self.length = -1

    @staticmethod
    def read_edge_file(filename):
        edge_list = []
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                if i == 0 or "#" in line:
                    continue
                line = line.split()
                i = int(line[0])
                e1 = int(line[1])
                e2 = int(line[2])
                current_edge = Edge(i, e1, e2)
                current_edge.is_boundary = True if line[3] == 1 else False
                current_edge.tetrahedron = int(line[4])
                edge_list.append(current_edge)
        return edge_list

    @staticmethod
    def calculate_lengths(edges: List, nodes: List[Vertex]):
        for edge in edges:
            start_point = nodes[edge.e1]
            end_point = nodes[edge.e2]
            edge.length = math.dist([start_point.x, start_point.y, start_point.z], 
                            [end_point.x, end_point.y, end_point.z])

        # hay que calcular cual es el otro tetrahedro que comparte el edge.
        # hacer un dfs en los tetrahedros de borde
        #ordenar aristas de mayor a menor

        # imprimir las caras


class Face:
    def __init__(self, i, v1, v2, v3, boundary, n1, n2 ):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.is_boundary = boundary
        self.n1 = n1
        self.n2 = n2
        # Redundancia para recorrer tetrahedros
        self.e1 = -1
        self.e2 = -1
        self.e3 = -1
        self.edges = set()
    

class Tetrahedron:
    def __init__(self, i, v1, v2, v3, v4):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.neighs = []
        self.is_boundary = False
        self.faces : List[Face] = []
        self.edges = set()
        self.visited = False
        # self.flag_is_used = algo
    # TODO: set the edges for a specific tetrahedron
    # def set_edges

class TerminalEdge:
    def __init__(self):
        self.tetrahedrons : Dict[Tetrahedron] = {}

# Ver caras de los tetraedros en el TE, 
# y si están más de una vez, borrar hasta que quede 1 sola vez

class Polyhedron:
    def __init__(self) -> None:
        self.faces : List[Face] = []



class TetrahedronMesh:
    def __init__(self, node_file, face_file, tetra_file, edge_file):
        self.node_list, self.face_list, self.tetra_list, self.edge_list, self.longest_edges = self.construct_tetrahedral_mesh(node_file, face_file, tetra_file, edge_file)
        self.n_tetrahedrons = len(self.tetra_list)
        self.n_faces = len(self.face_list)
        self.n_nodes = len(self.node_list)
        self.n_edges = len(self.edge_list)


    def read_node_file(self, filename):
        print("reading node file: "+ filename)
        f = open(filename, "r")
        node_list = []
        next(f)
        for line in f:
            line = line.split()
            #v1, v2, v3, boundary_marker
            if line[0] != '#':
                node_temp = Vertex(int(line[0]), float(line[1]), float(line[2]), float(line[3]))
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
                face_temp = Face(int(line[0]), v1, v2, v3, boundary_marker, n1, n2)
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



    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file, edge_file):
        node_list = self.read_node_file(node_file)
        face_list = self.read_face_file(face_file)
        tetra_list: List[Tetrahedron] = self.read_ele_file(ele_file)
        edge_list: List[Edge] = Edge.read_edge_file(edge_file)
        store_edges_in_faces(face_list, edge_list)
        Edge.calculate_lengths(edge_list, node_list)
        
        # Calculas caras de cada tetrahedro
        # Andres: Cambiando el indice por la cara en si
        for face in face_list:
            # Calcula neigh tetrahedras from faces
            neigh1 = face.n1
            neigh2 = face.n2
            if neigh1 != -1:
                tetra_list[neigh1].faces.append(face)
                #tetra_list[neigh1].is_boundary = face_list[f].is_boundary
            if neigh2 != -1:
                tetra_list[neigh2].faces.append(face)
                #tetra_list[neigh2].is_boundary = face_list[f].is_boundary
            #falta agregar el caso de que sea una cara de borde
        longest_edges = {}
        # Calcula lwos tetrahedros vecinos
        for tetra in tetra_list:
            for face in tetra.faces:
                neighs = [face.n1, face.n2]
                curr_tetra = tetra.i
                neigh_tetra = neighs[0] if neighs[0] != curr_tetra else neighs[1]
                tetra.neighs.append(neigh_tetra)

                # Add edges to tetrahedron
                for edge_index in face.edges:
                    tetra.edges.add(edge_index)
            # Aca se supone que ya agregamos todos los edges al tetrahedro
            # por eso podemos calcular su arista mas larga
            current_tetra_edge_lengths = []
            current_tetra_edge_indexes = []
            for edge in tetra.edges:
                current_tetra_edge_lengths.append(edge_list[edge].length)
                edge_list[edge].tetrahedron_list.append(tetra)
            tetra_edges = list(tetra.edges)
            longest_edges[tetra.i] = tetra_edges[current_tetra_edge_lengths.index(max(current_tetra_edge_lengths))]
        #print(longest_edges)  [node_list[tetra.v1], node_list[tetra.v2], node_list[tetra.v3], node_list[tetra.v4]]
            #printOFF_faces("test1.OFF", node_list, [face_list[i] for i in tetra.faces])
            #input() 

        # Imprime los tetrahedros
        # for t in range(0, len(tetra_list)):
        #     print("tetrahedron ", t, ":", tetra_list[t].v1, tetra_list[t].v2, tetra_list[t].v3, tetra_list[t].v4,
        #      tetra_list[t].faces, tetra_list[t].neighs, tetra_list[t].is_boundary, tetra_list[t].edges)

        return node_list, face_list, tetra_list, edge_list, longest_edges

def printOFF_faces(filename, vertices, faces):
    print("writing OFF file: "+ filename)
    with open(filename, 'w') as fh:
        fh.write("OFF\n")
        fh.write("%d %d 0\n" % (len(vertices), len(faces)))
        for v in vertices:
            fh.write("%f %f %f\n" % (v.x, v.y, v.z))
        for f in faces:
            fh.write("3 %d %d %d\n" % (f.v1, f.v2, f.v3))

# Function for giving each face it's corresponding edges
def store_edges_in_faces(list_faces : List[Face], list_edges : List[Edge]):
    edge_list_new = [(edge.e1, edge.e2) for edge in list_edges]
    for face in list_faces:
        e1 = (face.v1, face.v2)
        e2 = (face.v2, face.v3)
        e3 = (face.v3, face.v1)
        try:
            index_to_add = edge_list_new.index(e1)
            face.edges.add(index_to_add)
        except ValueError:
            try:
                index_to_add = edge_list_new.index(e1[::-1])
                face.edges.add(index_to_add)
            except ValueError:
                print("this ain't workin chief")
        try:
            index_to_add = edge_list_new.index(e2)
            face.edges.add(index_to_add)
        except ValueError:
            try:
                index_to_add =edge_list_new.index(e2[::-1])
                face.edges.add(index_to_add)
            except ValueError:
                print("this ain't workin chief")
        try:
            index_to_add = edge_list_new.index(e3)
            face.edges.add(index_to_add)
        except ValueError:
            try:
                index_to_add = edge_list_new.index(e3[::-1])
                face.edges.add(index_to_add)
            except ValueError:
                print("this ain't workin chief")
        #print(face.edges)


#dfs recursivo original
def dfs_on_tetrahedral_mesh_recursive(tetra_mesh : TetrahedronMesh, e : Edge, terminal_edge : TerminalEdge): #, index_seed: int):
    for i, tetrahedron in enumerate(tetra_mesh.edge_list[e.i].tetrahedron_list):
        if not tetrahedron.visited:
            terminal_edge.tetrahedrons[tetrahedron.i] = tetrahedron
            tetrahedron.visited = True
            #terminal_edge
            longest_edge_for_current_tetrahedron = tetra_mesh.longest_edges[tetrahedron.i]
            #for edge in tetrahedron.edges:
            dfs_on_tetrahedral_mesh_recursive(tetra_mesh, tetra_mesh.edge_list[longest_edge_for_current_tetrahedron], terminal_edge) # this will make one giant polyhedron, we want multiple polyhedra

# One flaw of this approach is that if there's a non convex polyhedron with v-e+f=2, e.g a 
# great stellated dodecahdron, this won't catch it.
# Function to check the Euler Characteristic of a polyhedron (if its convex returns true, false otherwise):
def check_euler_characteristic(poly : Polyhedron) -> bool:
    vertices_counter : int = 0
    edges_counter :int = 0
    faces_counter : int = 0
    vertices = []
    edges = []
    #print(poly.faces)
    for face in poly.faces:
        faces_counter += 1
        for vertex in (face.v1, face.v2, face.v3):
            if vertex not in vertices:
                vertices.append(vertex)
                vertices_counter += 1
        for edge in face.edges:
            if edge not in edges:
                edges.append(edge)
                edges_counter += 1
    #print(f"V = {vertices_counter}, E = {edges_counter}, F = {faces_counter}")
    if vertices_counter - edges_counter + faces_counter == 2:
        return True
    return False

def make_polyhedra_from_terminal_edges(terminal_edge_list : List[TerminalEdge]) -> List[Polyhedron]:
    poly_list : List[Polyhedron] = []
    counter_removed : int = 0
    counter_faces : int = 0
    for i, terminal_edge in enumerate(terminal_edge_list):
        #print(f"terminal edge number {i}")
        comparator = [t.i for t in terminal_edge.tetrahedrons.values()]
        faces : Dict[Face] = {}
        for tetrahedron in terminal_edge.tetrahedrons.values():
            for face in tetrahedron.faces:
                try:
                    faces[face.i] += 1
                except KeyError:
                    faces[face.i] = 1
        poly_list.append(Polyhedron())
        for tetrahedron in terminal_edge.tetrahedrons.values():
            for face in tetrahedron.faces:
                # remove faces that are counted twice
                if faces[face.i] > 1:
                    counter_removed += 1
                    continue
                else:
                    poly_list[i].faces.append(face)
                    counter_faces += 1
    # print(f"Total removed faces = {counter_removed}")
    # print(f"Total added faces = {counter_faces}")
    # print(f"total polyhedra b4 removing = {len(poly_list)}")
    # if polyhedron is empty, remove it:
    # for i, poly in enumerate(poly_list):
    #     if not poly.faces:
    #         poly_list.pop(i)    
    #     print(f"polyhedron{i} : faces = {poly.faces}")
    # print(f"total polyhedra after removing = {len(poly_list)}")
    return poly_list

# TODO: HACER DFS con lista de aristas de mayor a menor

# ta malo este, está imprimiendo poliedros con 0 caras, pero ninguno tiene 0 caras
def print_polyhedra_visf(vertices : List[Vertex], poly_list : List[Polyhedron], filename : str):
    print(f"Writing VisF file {filename}")
    i = 0
    face_indices = {}
    faces : List[Face] = []
    for j, p in enumerate(poly_list):
        face_indices[j] = []
        for face in p.faces:
            face_indices[j].append(i)
            i += 1
            faces.append(face)
    for p in poly_list:
        for face in p.faces:
            faces.append(face)
    with open(filename, 'w') as f:
        f.write("2 2\n")
        f.write(f"{len(vertices)}\n")
        for v in vertices:
            f.write(f"{v.x} {v.y} {v.z}\n")
        f.write(f"{len(faces)}\n")
        for face in faces:
            f.write(f"3 {face.v1} {face.v2} {face.v3}\n")

        f.write("0\n")
        f.write(f"{(len(poly_list))}\n")
        for v in face_indices.values():
            f.write(f"{len(v)} ")
            for x in v:
                f.write(f"{x} ")
            f.write("\n")
            
def delete_repeated_faces_from_terminal_edge(terminal_edge : TerminalEdge):
    for k, tetrahedron in terminal_edge.tetrahedrons.items():
        counter = Counter(tetrahedron.faces)
        terminal_edge.tetrahedrons[k].faces = [f for f in tetrahedron.faces if counter[f] < 2]
                

if __name__ == "__main__":
    
    filename = sys.argv[1]
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    terminal_edges : List[TerminalEdge] = []
    #print(f"The longest edges for each tetrahedron are: {mesh.longest_edges}")
    long_edges_objects = [mesh.edge_list[e] for e in mesh.longest_edges.values()]
    long_edges_objects = reversed(sorted(long_edges_objects, key=lambda x: x.length))
    #print(f"{[e.length for e in long_edges_objects]}")
    for i, e in enumerate(long_edges_objects):
        terminal_edges.append(TerminalEdge())
        dfs_on_tetrahedral_mesh_recursive(mesh, e, terminal_edges[-1])
        if not terminal_edges[-1].tetrahedrons: # if the terminal edge is empty, this fixes polyhedra with no faces
            terminal_edges.pop(-1) # remove it from the list
        delete_repeated_faces_from_terminal_edge(terminal_edges[-1])

    # print(terminal_edges)
    polyhedra = make_polyhedra_from_terminal_edges(terminal_edges)
    faces = []
    vertices = []
    for p in terminal_edges:
        for i, tetra in p.tetrahedrons.items():
            faces += [f for f in tetra.faces if f not in faces]
    #print(f"Faces: {faces}")
    printOFF_faces("terminal_edges_full_socket.OFF", mesh.node_list, faces)

    # Printing the OFF and the VisF of the polyhedra
    # OFF:
    poly_faces : List[Face] = []
    for i, p in enumerate(polyhedra):
        if not p.faces:
            polyhedra.remove(p)
            continue
        for face in p.faces:
            poly_faces.append(face)
        if not check_euler_characteristic(p):
            print(f"El poliedro {i} no es convexo")
    printOFF_faces("polyhedra_full_socket.OFF", mesh.node_list, poly_faces)

    # VisF:
    print_polyhedra_visf(mesh.node_list, polyhedra, "socket_polyhedra.visf")
    
    
    
    
    #print_polyhedra_visf(mesh.node_list, [polyhedra[0], polyhedra[1]], "polyhedron0and1.visf")
    #printOFF_faces("polyhedron0anbd1.OFF", mesh.node_list, polyhedra[0].faces + polyhedra[1].faces)
    #print(poly_faces)










    # vertices = []
    # faces = []
    # #print(p.tetrahedrons for p in poly)
    # #print([p.tetrahedrons.items() for p in poly])
    # for p in poly:
    #     for i, tetra in p.tetrahedrons.items():
    #         if mesh.node_list[tetra.v1] not in vertices:
    #             vertices.append(mesh.node_list[tetra.v1])
    #         if mesh.node_list[tetra.v2] not in vertices:
    #             vertices.append(mesh.node_list[tetra.v2])
    #         if mesh.node_list[tetra.v3] not in vertices:
    #             vertices.append(mesh.node_list[tetra.v3])
    #         if mesh.node_list[tetra.v4] not in vertices:
    #             vertices.append(mesh.node_list[tetra.v4])
    #         faces += [f for f in tetra.faces if f not in faces]
    # #print(f"Faces: {faces}")
    # printOFF_faces("polyhedron2.OFF", mesh.node_list, faces)
    # polyhedron_list = make_polyhedra_from_terminal_edges(poly)
    # #print(polyhedron_list)
    # ec = [check_euler_characteristic(p) for p in polyhedron_list]
    # poly_vertices = []
    # poly_faces = []
    # for po in polyhedron_list:
    #     for face in po.faces:
    #         if mesh.node_list[face.v1] not in poly_vertices:
    #             poly_vertices.append(mesh.node_list[face.v1])
    #         if mesh.node_list[face.v2] not in poly_vertices:
    #             poly_vertices.append(mesh.node_list[face.v2])
    #         if mesh.node_list[face.v3] not in poly_vertices:
    #             poly_vertices.append(mesh.node_list[face.v3])
    #         if face not in poly_faces:
    #             poly_faces.append(face)
    # #printOFF_faces("noneuler2.OFF", mesh.node_list, polyhedron_list[1].faces)
    # #print(ec)
    # print(f"nº poliedros: {len(polyhedron_list)}")
    # print_polyhedra_visf(mesh.node_list, [polyhedron_list[10]], "poliedro11.visf")
    # print_polyhedra_visf(mesh.node_list, [polyhedron_list[9]], "poliedro10.visf")
    # printOFF_faces("poliedro10.OFF", mesh.node_list, polyhedron_list[9].faces)
    # printOFF_faces("poliedro11.OFF", mesh.node_list, polyhedron_list[10].faces)
    # poly9faces = []
    # for t in poly[9].tetrahedrons.values():
    #     for f in t.faces:
    #         poly9faces.append(f)
    # printOFF_faces("terminaledge10.OFF", mesh.node_list, poly9faces)
    # printOFF_faces("3dcubevisf.OFF", mesh.node_list, poly_faces)
    # print_polyhedra_visf(mesh.node_list, polyhedron_list, "3DCUBE.visf")
    # for i, p in enumerate(polyhedron_list):
    #     if not check_euler_characteristic(p):
    #         print(f"El poliedro {i} es no convexo")


  # TODO: Aplicar formula de euler para cada poliedro, los que nos den distinto a 2, son no simples, buscarlos.V - E + F = 2



  # def DepthFirstSearch(polyhedron, visited_tetra, tetra, frontier_faces, mesh):
#     visited_tetra[tetra.i] = True
#     for i in range(0, 4):
#         face_id = tetra.faces[i]
#         if face_id != -1:
#             if frontier_faces[face_id] == True:
#                 fa = mesh.face_list[face_id]
#                 polyhedron.append(fa)
#             else:
#                 next_tetra = mesh.tetra_list[tetra.neighs[i]]
#                 if(visited_tetra[next_tetra.i] == False):
#                     DepthFirstSearch(polyhedron, visited_tetra, next_tetra, frontier_faces, mesh)
    
# # Genera un polígono con las frontier-faces como caras y la terminal_face como generador de la cara
# def generate_polyhedra_from_terminal_face(terminal_face, bitvector_frontier_edges, mesh):

#     visited_tetra = [False] * mesh.n_tetrahedrons
#     terminal_tetra = mesh.tetra_list[mesh.face_list[terminal_face.i].n1 if mesh.face_list[terminal_face.i].n1 != -1 else mesh.face_list[terminal_face.i].n2]
#     #print(terminal_tetra.faces)
#     polyhedron = []
#     DepthFirstSearch(polyhedron, visited_tetra, terminal_tetra, bitvector_frontier_edges, mesh)
    
#     #print("polyhedron: ", len(polyhedron))
#     return polyhedron