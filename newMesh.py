import numpy as np
import statistics

class FaceNode:
    def __init__(self,v3,i):
        self.v3 = v3
        self.i = i
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face Node " + 'V3: ' +str(self.v3) + " i :" + str(self.i)+ "\n"

class FaceTree:
    def __init__(self, v2,v3, i):
        self.v2 = v2
        self.node_list = [FaceNode(v3,i)]
        
    def add_node(self, v3,i):
        new = FaceNode(v3,i)
        self.node_list.append(new)
    def get_root(self):
        return self.v2
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face Tree " + 'V2: ' +str(self.v2) + " V3's: ( " + str(self.node_list)+ ") " + ")\n"

class Polyhedron:
    def __init__(self):
        self.tetras = []
        self.faces = []
        self.nodes = []
        self.was_repaired = False
        self.is_convex = False
    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Polyhedron " + ": Tetra: " + str(self.tetras) + "Face n: " + str(len(self.faces)) +  ", Is convex: " + str(self.is_convex)  + ")n"


class Vertex:
    def __init__(self, i, x, y, z):
        self.i = i  
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Vertex " + str(self.i) + ": ( " + str(self.x) + ", " + str(self.y)  + ", " + str(self.z) + ") " + ")\n"

class Face:
    def __init__(self, i, v1, v2, v3 ):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.n1 = -1
        self.n2 = -1
        self.edges = [] #tetra case 3, poly case at least 3
        self.area = -1.0
        self.is_boundary = True

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Edges: " + str(self.edges) + " Neighs: " + str(self.n1) + ','+ str(self.n2) + ")\n"
class Edge:
    def __init__(self, i, end_point1, end_point2) -> None:
        self.i = i
        self.v1 = end_point1
        self.v2 = end_point2
        self.faces = [] # boundary case 2, internal case at least 3
        self.length = -1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Edge " + str(self.i) + " Vertex i: " + str(self.v1) + " Vertex f: " + str(self.v2) + " Faces: " + str(self.faces) + ")\n"

class PolyllaEdge_Edge(Edge):
    def __init__(self, i, end_point1, end_point2) -> None:
        super().__init__(i, end_point1, end_point2)
        self.first_tetra = -1
        self.tetrahedrons = []

class Tetrahedron:
    def __init__(self, i, v1, v2, v3, v4):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.neighs = [] #4 neighs not necessary, we can use faces neighs
        self.faces = []
        self.edges = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Tetra " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Vertex 4: " + str(self.v4) + " Faces: " + str(self.faces) + " Neighs: " + str(self.neighs) +  " Edges: " + ")\n"
    

class EdgeTetrahedronMesh:
    def __init__(self, node_file, face_file, tetra_file):
        self.node_list, self.face_list, self.tetra_list, self.edge_list = self.construct_tetrahedral_mesh(node_file, face_file, tetra_file)
        self.n_tetrahedrons = len(self.tetra_list)
        self.n_faces = len(self.face_list)
        self.n_nodes = len(self.node_list)
        self.n_edges = len(self.edge_list)
    
    def save_vertex(self,filev):
        matrix = []
        vertex_list = []
        face_matrix = []
        file = open(filev, "r")
        next(file)
        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            v = Vertex(int(l[0]), float(l[1]), float(l[2]), float(l[3]))
            vertex_list.append(v)
            matrix.append([[],[]]) # in c++ is not necessary
            face_matrix.append([])
        file.close()
        return vertex_list,matrix,face_matrix

    def save_faces(self, filef, edges_matrix,node_list,face_matrix):
    
        face_list = []
        file = open(filef, "r")
        next(file)

        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            #print(l)
            v1 = int(l[1])
            v2 = int(l[2])
            v3 = int(l[3])
            fi = int(l[0])
            f = Face(fi, v1,v2,v3)

            face_list.append(f)

            v = [v1,v2,v3]
            v.sort()
            
            if not face_matrix[v[0]]:
                face_matrix[v[0]].append(FaceTree(v[1],v[2],fi))
            else:
                added = False
                for tree in face_matrix[v[0]]:
                    if tree.get_root() == v[1]:
                        tree.add_node(v[2],fi)
                        added = True
                        break
                if not added:
                    face_matrix[v[0]].append(FaceTree(v[1],v[2],fi))

            savedE1 = False
            savedE2 = False
            savedE3 = False
            
            v = [v1,v2]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

            v = [v2,v3]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

            v = [v3,v1]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

        file.close()
        return face_list, face_matrix
    
    def save_edges(self, matrix, face_list, node_list):
        edge_list = []
        ei = 0
        for vi in range(len(matrix)):
            for i in range(len(matrix[vi][0])):
                vf = matrix[vi][0][i]
                faces = matrix[vi][1][i]
                edge = PolyllaEdge_Edge(ei,vi,vf)
                edge.faces = faces
                v1 = node_list[edge.v1]
                v2 = node_list[edge.v2]
                distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
                edge.length = distance
                edge_list.append(edge)
                # print(vi,',',vf)
                
                for f in faces:
                    face = face_list[f]
                    face.edges.append(ei)
                ei += 1
        return edge_list
    
    def save_tetra(self, filet, face_matrix,face_list, edges_list):

        tetra_list = []
        file = open(filet, "r")
        next(file)

        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            #print(l)
            v1 = int(l[1])
            v2 = int(l[2])
            v3 = int(l[3])
            v4 = int(l[4])
            ti = int(l[0])
            t = Tetrahedron(ti, v1,v2,v3,v4)
            self.asign_faces(t,face_matrix,face_list, tetra_list,edges_list)
            tetra_list.append(t)

        file.close()
        return tetra_list
    
    def asign_faces(self,tetra, face_matrix, face_list, tetra_list,edges_list):

        faces = []
        edges = []
        v = [tetra.v1,tetra.v2,tetra.v3]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f1 = node.i
                        faces.append(f1)
                        edges+=face_list[f1].edges
                        if(face_list[f1].n1 == -1):
                            face_list[f1].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f1].n2 == -1):
                            face_list[f1].is_boundary = False
                            face_list[f1].n2 = tetra.i
                            tetra.neighs.append(face_list[f1].n1)
                            f_index = tetra_list[face_list[f1].n1].faces.index(f1)
                            tetra_list[face_list[f1].n1].neighs[f_index] = tetra.i
                            

                    
        v = [tetra.v2,tetra.v3,tetra.v4]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f2 = node.i
                        faces.append(f2)
                        edges+=face_list[f2].edges
                        if(face_list[f2].n1 == -1):
                            face_list[f2].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f2].n2 == -1):
                            face_list[f1].is_boundary = False
                            face_list[f2].n2 = tetra.i
                            tetra.neighs.append(face_list[f2].n1)
                            f_index = tetra_list[face_list[f2].n1].faces.index(f2)
                            tetra_list[face_list[f2].n1].neighs[f_index] = tetra.i
        v = [tetra.v3,tetra.v4,tetra.v1]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f3 = node.i
                        faces.append(f3)
                        edges+=face_list[f3].edges
                        if(face_list[f3].n1 == -1):
                            face_list[f3].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f3].n2 == -1):
                            face_list[f3].is_boundary = False
                            face_list[f3].n2 = tetra.i
                            tetra.neighs.append(face_list[f3].n1)
                            f_index = tetra_list[face_list[f3].n1].faces.index(f3)
                            tetra_list[face_list[f3].n1].neighs[f_index] = tetra.i
                        
        v = [tetra.v4,tetra.v1,tetra.v2]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f4 = node.i
                        faces.append(f4)
                        edges+=face_list[f4].edges
                        if(face_list[f4].n1 == -1):
                            face_list[f4].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f4].n2 == -1):
                            face_list[f4].is_boundary = False
                            face_list[f4].n2 = tetra.i
                            tetra.neighs.append(face_list[f4].n1)
                            f_index = tetra_list[face_list[f4].n1].faces.index(f4)
                            tetra_list[face_list[f4].n1].neighs[f_index] = tetra.i
        
        tetra.faces = faces
        tetra.edges = list(set(edges))
        for e in tetra.edges:
            if edges_list[e].first_tetra < 0:
                edges_list[e].first_tetra = tetra.i

        return

    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file):
        print("Reading vertex file")
        node_list, edges_matrix,face_matrix = self.save_vertex(node_file) #self.read_node_file(node_file)
        print("Reading face file")
        face_list, face_matrix = self.save_faces(face_file,edges_matrix, node_list,face_matrix) #self.read_face_file(face_file)
        print("Processing edges")
        edge_list = self.save_edges(edges_matrix, face_list,node_list)#self.read_edge_file(edge_file)
        print("Reading tetra file")
        tetra_list = self.save_tetra(ele_file,face_matrix,face_list,edge_list) # self.read_ele_file(ele_file)


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
            # print('found face', face_list[face].edges)
            if edge in face_list[face].edges:
                f.append(face)
        # print(f, edge, tetra_origin)
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

    # Calculate a list of tetrahedrons adjacent to each edge
    # only use this functions when you have edges adjacents to two tetrahedrons but no adjacent by any face
    # def calculate_tetrahedrons_for_edge(self, ea = self.node_list[v1]ahedrons)]    
    def calculate_edges_length(self):
        for edge in self.edge_list:
            v1 = self.node_list[edge.v1]
            v2 = self.node_list[edge.v2]
            distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
            edge.length = distance

    def get_edge_ratio(self):
        self.calculate_edges_length()
        ratios = []
        for tetra in self.tetra_list:
            edges = []
            for face in tetra.faces:
                for edge in self.face_list[face].edges:
                    edges.append(self.edge_list[edge].length)
            ratio = min(edges)/max(edges)
            ratios.append(ratio)
        mean_edge_ratio = statistics.mean(ratios)
        min_edge_ratio = min(ratios)
        max_edge_ratio = max(ratios)
        return [mean_edge_ratio, min_edge_ratio, max_edge_ratio]


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
    def return_info(self):
        #print("Tetrahedral mesh info:")
        #print("Number of nodes: ", len(self.node_list))
        #print("Number of faces: ", len(self.face_list))
        #print("Number of tetrahedrons: ", len(self.tetra_list))
        #print("Number of edges: ", len(self.edge_list))
        return len(self.node_list), len(self.face_list), len(self.tetra_list), len(self.edge_list)




class FaceTetrahedronMesh:
    def __init__(self, node_file, face_file, tetra_file):
        self.node_list, self.face_list, self.tetra_list, self.edge_list = self.construct_tetrahedral_mesh(node_file, face_file, tetra_file)
        self.n_tetrahedrons = len(self.tetra_list)
        self.n_faces = len(self.face_list)
        self.n_nodes = len(self.node_list)
        self.n_edges = len(self.edge_list)
    
    def save_vertex(self,filev):
        matrix = []
        vertex_list = []
        face_matrix = []
        file = open(filev, "r")
        next(file)
        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            v = Vertex(int(l[0]), float(l[1]), float(l[2]), float(l[3]))
            vertex_list.append(v)
            matrix.append([[],[]]) # in c++ is not necessary
            face_matrix.append([])
        file.close()
        return vertex_list,matrix,face_matrix
    
    def save_faces(self, filef, edges_matrix,node_list,face_matrix):
    
        face_list = []
        file = open(filef, "r")
        next(file)

        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            #print(l)
            v1 = int(l[1])
            v2 = int(l[2])
            v3 = int(l[3])
            fi = int(l[0])
            f = Face(fi, v1,v2,v3)

            face_list.append(f)

            v = [v1,v2,v3]
            v.sort()
            
            if not face_matrix[v[0]]:
                face_matrix[v[0]].append(FaceTree(v[1],v[2],fi))
            else:
                added = False
                for tree in face_matrix[v[0]]:
                    if tree.get_root() == v[1]:
                        tree.add_node(v[2],fi)
                        added = True
                        break
                if not added:
                    face_matrix[v[0]].append(FaceTree(v[1],v[2],fi))

            savedE1 = False
            savedE2 = False
            savedE3 = False
            
            v = [v1,v2]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

            v = [v2,v3]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

            v = [v3,v1]
            v.sort()
            if v[1] not in edges_matrix[v[0]][0]:# and v1 not in edges_matrix[v2][0]:
                edges_matrix[v[0]][0].append(v[1])
                edges_matrix[v[0]][1].append([fi])
                savedE1 = True
            else:
                index = edges_matrix[v[0]][0].index(v[1])
                edges_matrix[v[0]][1][index].append(fi)

        file.close()
        return face_list, face_matrix
    
    def save_edges(self, matrix, face_list, node_list):
        edge_list = []
        ei = 0
        for vi in range(len(matrix)):
            for i in range(len(matrix[vi][0])):
                vf = matrix[vi][0][i]
                faces = matrix[vi][1][i]
                edge = Edge(ei,vi,vf)
                edge.faces = faces
                v1 = node_list[edge.v1]
                v2 = node_list[edge.v2]
                distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
                edge.length = distance
                edge_list.append(edge)
                # print(vi,',',vf)
                
                for f in faces:
                    face = face_list[f]
                    face.edges.append(ei)
                ei += 1
        return edge_list
    
    def save_tetra(self, filet, face_matrix,face_list):

        tetra_list = []
        file = open(filet, "r")
        next(file)

        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            #print(l)
            v1 = int(l[1])
            v2 = int(l[2])
            v3 = int(l[3])
            v4 = int(l[4])
            ti = int(l[0])
            t = Tetrahedron(ti, v1,v2,v3,v4)
            self.asign_faces(t,face_matrix,face_list, tetra_list)
            tetra_list.append(t)

        file.close()
        return tetra_list
    
    def asign_faces(self,tetra, face_matrix, face_list, tetra_list):

        faces = []
        v = [tetra.v1,tetra.v2,tetra.v3]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f1 = node.i
                        faces.append(f1)
                        if(face_list[f1].n1 == -1):
                            face_list[f1].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f1].n2 == -1):
                            face_list[f1].n2 = tetra.i
                            tetra.neighs.append(face_list[f1].n1)
                            f_index = tetra_list[face_list[f1].n1].faces.index(f1)
                            tetra_list[face_list[f1].n1].neighs[f_index] = tetra.i
                            

                    
        v = [tetra.v2,tetra.v3,tetra.v4]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f2 = node.i
                        faces.append(f2)
                        if(face_list[f2].n1 == -1):
                            face_list[f2].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f2].n2 == -1):
                            face_list[f2].n2 = tetra.i
                            tetra.neighs.append(face_list[f2].n1)
                            f_index = tetra_list[face_list[f2].n1].faces.index(f2)
                            tetra_list[face_list[f2].n1].neighs[f_index] = tetra.i
        v = [tetra.v3,tetra.v4,tetra.v1]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f3 = node.i
                        faces.append(f3)
                        if(face_list[f3].n1 == -1):
                            face_list[f3].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f3].n2 == -1):
                            face_list[f3].n2 = tetra.i
                            tetra.neighs.append(face_list[f3].n1)
                            f_index = tetra_list[face_list[f3].n1].faces.index(f3)
                            tetra_list[face_list[f3].n1].neighs[f_index] = tetra.i
                        
        v = [tetra.v4,tetra.v1,tetra.v2]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f4 = node.i
                        faces.append(f4)
                        if(face_list[f4].n1 == -1):
                            face_list[f4].n1 = tetra.i
                            tetra.neighs.append(-1)
                        elif(face_list[f4].n2 == -1):
                            face_list[f4].n2 = tetra.i
                            tetra.neighs.append(face_list[f4].n1)
                            f_index = tetra_list[face_list[f4].n1].faces.index(f4)
                            tetra_list[face_list[f4].n1].neighs[f_index] = tetra.i
        
        tetra.faces = faces
        return

    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file):
        print("Reading vertex file")
        node_list, edges_matrix,face_matrix = self.save_vertex(node_file) #self.read_node_file(node_file)
        print("Reading face file")
        face_list, face_matrix = self.save_faces(face_file,edges_matrix, node_list,face_matrix) #self.read_face_file(face_file)
        print("Processing edges")
        edge_list = self.save_edges(edges_matrix, face_list,node_list)#self.read_edge_file(edge_file)
        print("Reading tetra file")
        tetra_list = self.save_tetra(ele_file,face_matrix,face_list) # self.read_ele_file(ele_file)
        
        print("Tetraedralization ready")
        

        return node_list, face_list, tetra_list, edge_list


    def calculate_edge_length(self,edge):

        v1 = self.node_list[edge.v1]
        v2 = self.node_list[edge.v2]
        distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
        return distance

    def get_edge_ratio(self):
        ratios = []
        for tetra in self.tetra_list:
            edges = []
            for face in tetra.faces:
                for edge in self.face_list[face].edges:
                    self.edge_list[edge].length = self.calculate_edge_length(self.edge_list[edge])
                    edges.append(self.edge_list[edge].length)
            ratio = min(edges)/max(edges)
            ratios.append(ratio)
        mean_edge_ratio = statistics.mean(ratios)
        min_edge_ratio = min(ratios)
        max_edge_ratio = max(ratios)
        return [mean_edge_ratio, min_edge_ratio, max_edge_ratio]
    
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

    def return_info(self):
        #print("Tetrahedral mesh info:")
        #print("Number of nodes: ", len(self.node_list))
        #print("Number of faces: ", len(self.face_list))
        #print("Number of tetrahedrons: ", len(self.tetra_list))
        #print("Number of edges: ", len(self.edge_list))
        return len(self.node_list), len(self.face_list), len(self.tetra_list), len(self.edge_list)

def saveLog(filename, info_list):
      f = open(filename,'w')
      for i in info_list:
            f.write(str(i))
