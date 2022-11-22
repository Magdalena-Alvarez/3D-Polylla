#Reglas
# - Cualquier cualquer calculo geometrico no debe en la clase mesh, deben estar en PolyllaEdge y PolyllaFace

from collections import Counter
from operator import index
from typing import List, Dict
import numpy as np
import sys
import math

class Polyhedron:
    def __init__(self):
        self.tetras = []
        self.faces = []
        self.was_repaired = False

class Vertex:
    def __init__(self, i, x, y, z):
        self.i = i  
        self.x = x
        self.y = y
        self.z = z

class Face:
    def __init__(self, i, v1, v2, v3, boundary, n1, n2 ):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.is_boundary = boundary
        self.n1 = n1
        self.n2 = n2
        self.edges = []
        self.area = -1

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
        self.edges = []

class Edge:
    def __init__(self, i, end_point1, end_point2) -> None:
        self.i = i
        self.v1 = end_point1
        self.v2 = end_point2
        self.first_tetra = -1
        self.is_boundary = -1
        self.tetrahedrons = []
        self.faces = []
        # Length is saved for the polyhedralization process
        self.length = -1

class TetrahedronMesh:
    def __init__(self, node_file, face_file, tetra_file, edge_file):
        self.node_list, self.face_list, self.tetra_list, self.edge_list = self.construct_tetrahedral_mesh(node_file, face_file, tetra_file, edge_file)
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

    def read_edge_file(self, filename):
        print("reading edge file: "+ filename)
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
                current_edge.is_boundary = True if int(line[3]) == 1 else False
                current_edge.first_tetra = int(line[4])
                edge_list.append(current_edge)
        return edge_list


        
    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file, edge_file):
        node_list = self.read_node_file(node_file)
        face_list = self.read_face_file(face_file)
        tetra_list = self.read_ele_file(ele_file)
        edge_list = self.read_edge_file(edge_file)

        # asign to each face their edges
        #CAMBIAR POR ALGO MAS EFICIENTE, no O(n^2)
        for face in face_list:
            e1 = (face.v1, face.v2)
            e2 = (face.v2, face.v3)
            e3 = (face.v3, face.v1)
            for edge in edge_list:
                if (edge.v1, edge.v2) == e1 or (edge.v2, edge.v1) == e1:
                    face.edges.append(edge.i)
                if (edge.v1, edge.v2) == e2 or (edge.v2, edge.v1) == e2:
                    face.edges.append(edge.i)
                if (edge.v1, edge.v2) == e3 or (edge.v2, edge.v1) == e3:
                    face.edges.append(edge.i)
                #agregar que si len(face.edges == 3) se para esto
            #print("face " + str(face.i) + " has this edges " + str(face.edges))
        

        # add the faces of each tetrahedron
        for f in range(0, len(face_list)):
            # Calcula neigh tetrahedras from faces
            neigh1 = face_list[f].n1
            neigh2 = face_list[f].n2
            if neigh1 != -1:
                tetra_list[neigh1].faces.append(f)
            if neigh2 != -1:
                tetra_list[neigh2].faces.append(f)
            #Se marca si un tetra es boundary
            if neigh1 == -1:
                tetra_list[neigh2].is_boundary = True
            if neigh2 == -1:
                tetra_list[neigh1].is_boundary = True

        # Calcula los tetrahedros vecinos
        for tetra in tetra_list:
            for f in tetra.faces:
                face = face_list[f]
                neighs = [face.n1, face.n2]
                curr_tetra = tetra.i
                neigh_tetra = neighs[0] if neighs[0] != curr_tetra else neighs[1]
                tetra.neighs.append(neigh_tetra)
        
        #Find the edges of each tetrahedron
        for tetra in tetra_list:
            for f in tetra.faces:
                face = face_list[f]
                ## add edges to tetrahedron
                tetra_edges_aux = []
                for edge_index in face.edges:
                    tetra_edges_aux.append(edge_list[edge_index].i)
                tetra.edges.extend(tetra_edges_aux)
            tetra.edges = [*set(tetra.edges)]


        # Calculate border tetrahedron adjacent to each edge
#        for tetra in tetra_list:
#            for edge in tetra.edges:
#                if tetra.is_boundary:
#                    edge_list[edge].first_tetra = tetra.i

        # Calculate border tetrahedron adjacent to each edge
        for face in face_list:
            for edge in face.edges:
                if face.is_boundary:
                    n1 = face.n1
                    n2 = face.n2
                    if n1 != -1:
                        edge_list[edge].first_tetra = n1
                    else:
                        edge_list[edge].first_tetra = n2

        # Calculate all the tetrahedrons adjacent to each edge in order
        #This do it using brute force
        #self.calculate_tetrahedrons_for_edge(edge_list, tetra_list)
        #This do it using the first tetrahedron, if the edge is boundary, then the first tetrahedron MUST BE boundary.
        for edge in edge_list:
            self.tetrahedrons_adjcacents_to_edge(edge.i, tetra_list, face_list, edge_list)

        # Imprime los tetrahedros
        #for t in range(0, len(tetra_list)):
        #    print("tetrahedron ", t, ":", tetra_list[t].v1, tetra_list[t].v2, tetra_list[t].v3, tetra_list[t].v4, tetra_list[t].faces, tetra_list[t].neighs, tetra_list[t].is_boundary, tetra_list[t].edges)

        

        return node_list, face_list, tetra_list, edge_list

    # Circle around an edge e to find their adjacent tetrahedrons and faces and store them in order
    # If the edge es boundary, then the first_tetrahedron MUST BE boundary.
    def tetrahedrons_adjcacents_to_edge(self, edge, tetra_list, face_list, edge_list):
        tetra_origin = edge_list[edge].first_tetra
        # Search face adjacent to tetra_origin that contains edge
        f = []
        for face in tetra_list[tetra_origin].faces:
            if edge in face_list[face].edges:
                f.append(face)
        #t_next = tetra adjcaent to f_origin that is not tetra_origin and is not boundary
        tetra_1 = face_list[f[0]].n1 if face_list[f[0]].n1 != tetra_origin else face_list[f[0]].n2
        tetra_2 = face_list[f[1]].n1 if face_list[f[1]].n1 != tetra_origin else face_list[f[1]].n2
        if tetra_1 == -1:
            tetra_next = tetra_2
            f_next = f[1]
        else:
            tetra_next = tetra_1
            f_next = f[0]
        faces = []
        tetras = [tetra_origin]
        #print("edge: ", edge, " border ", edge_list[edge].is_boundary ," tetra_origin: ", tetra_origin, " tetra_next: ", tetra_next, edge_list[edge].tetrahedrons)
        while tetra_next != tetra_origin:
            if tetra_next == -1:
                break
            tetras.append(tetra_next)
            faces.append(f_next)    
            #face that contains edge and is not f_origin
            for face in tetra_list[tetra_next].faces:
                if edge in face_list[face].edges and face != f_next:
                    f_next = face
                    break
            tetra_next = face_list[f_next].n1 if face_list[f_next].n1 != tetra_next else face_list[f_next].n2
        faces.append(f_next)
        edge_list[edge].tetrahedrons = tetras
        edge_list[edge].faces = faces


    # Calculate a list of tetrahedrons adjacent to each edge
    # only use this functions when you have edges adjacents to two tetrahedrons but no adjacent by any face
    def calculate_tetrahedrons_for_edge(self, edge_list, tetra_list):
        for tetra in tetra_list:
            for edge in tetra.edges:
                edge_list[edge].tetrahedrons.append(tetra.i)
                if tetra.is_boundary:
                    edge_list[edge].first_tetra = tetra.i
        #remove repeat tetrahedrons from edges
        for edge in edge_list:
            edge.tetrahedrons = [*set(edge.tetrahedrons)]    

    def get_face(self, f):
        return self.face_list[f]
    
    def get_edge(self, e):
        return self.edge_list[e]

    def get_tetrahedron(self,t):
        return self.tetra_list[t]
    
    def get_vertex(self, v):
        return self.node_list[v]

    def get_info(self):
        print("Tetrahedral mesh info:")
        print("Number of nodes: ", len(self.node_list))
        print("Number of faces: ", len(self.face_list))
        print("Number of tetrahedrons: ", len(self.tetra_list))
        print("Number of edges: ", len(self.edge_list))

if __name__ == "__main__":
    #filename = "data\\3D_100.1"
    filename = "data\\socket.1"
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"
    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    for edge in mesh.edge_list:
        print(edge.i, edge.v1, edge.v2, edge.tetrahedrons, edge.faces, edge.first_tetra)
        
