import numpy as np

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
        self.was_repaired = False

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
        self.vertex = [v1,v2,v3]
        self.n1 = -1
        self.n2 = -1
        self.neighs = []
        self.is_boundary = False
        self.edges = [] #tetra case 3, poly case at least 3
        self.area = -1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Edges: " + str(self.edges) + " Neighs: " + str(self.n1) + ','+ str(self.n2) + ")\n"
class Edge:
    def __init__(self, i, end_point1, end_point2) -> None:
        self.i = i
        self.v1 = end_point1
        self.v2 = end_point2
        self.vertex = [end_point1,end_point2]
        self.faces = [] # boundary case 2, internal case at least 3
        self.length = -1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Edge " + str(self.i) + " Vertex i: " + str(self.v1) + " Vertex f: " + str(self.v2) + " Faces: " + str(self.faces) + ")\n"

class PolyllaEdge_Edge(Edge):
    def __init__(self, i, end_point1, end_point2) -> None:
        super().__init__(i, end_point1, end_point2)
        self.tetrahedrons = []

class Tetrahedron:
    def __init__(self, i, v1, v2, v3, v4):
        self.i = i
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3
        self.v4 = v4
        self.vertex = [v1,v2,v3,v4]
        self.neighs = [] #4 neighs not necessary, we can use faces neighs
        self.is_boundary = False #if len(neighs) > 4 True
        self.faces = []
        self.edges = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Tetra " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Vertex 4: " + str(self.v4) + " Faces: " + str(self.faces) + " Neighs: " + str(self.neighs) + ")\n"
    

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
        file = open(filev, "r")
        next(file)
        for line in file:
            l = line.split()
            if l[0] == '#':
                continue
            v = Vertex(int(l[0]), float(l[1]), float(l[2]), float(l[3]))
            vertex_list.append(v)
            matrix.append([[],[]]) # in c++ is not necessary
        return vertex_list,matrix
    
    def save_faces(self, filef, edges_matrix):
    
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

            savedE1 = False
            savedE2 = False
            savedE3 = False


            if v2 not in edges_matrix[v1][0] and v1 not in edges_matrix[v2][0]:
                edges_matrix[v1][0].append(v2)
                edges_matrix[v1][1].append([fi])
                savedE1 = True

            if v3 not in edges_matrix[v2][0] and v2 not in edges_matrix[v3][0]:
                edges_matrix[v2][0].append(v3)
                edges_matrix[v2][1].append([fi])
                savedE2 = True
            if v1 not in edges_matrix[v3][0] and v3 not in edges_matrix[v1][0]:
                edges_matrix[v3][0].append(v1)
                edges_matrix[v3][1].append([fi])
                savedE3 = True

            #if it isn't saved it already exist (only two options)
            if not savedE1:
                if v2 in edges_matrix[v1][0]:
                    index = edges_matrix[v1][0].index(v2)
                    edges_matrix[v1][1][index].append(fi)
                else:
                    index = edges_matrix[v2][0].index(v1)
                    edges_matrix[v2][1][index].append(fi)

            if not savedE2:
                if v3 in edges_matrix[v2][0]:
                    index = edges_matrix[v2][0].index(v3)
                    edges_matrix[v2][1][index].append(fi)
                else:
                    index = edges_matrix[v3][0].index(v2)
                    edges_matrix[v3][1][index].append(fi)
            if not savedE3:
                if v1 in edges_matrix[v3][0]:
                    index = edges_matrix[v3][0].index(v1)
                    edges_matrix[v3][1][index].append(fi)
                else:
                    index = edges_matrix[v1][0].index(v3)
                    edges_matrix[v1][1][index].append(fi)
        return face_list

    
    def save_edges(self, matrix, face_list):
        edge_list = []
        ei = 0
        for vi in range(len(matrix)):
            for i in range(len(matrix[vi][0])):
                vf = matrix[vi][0][i]
                faces = matrix[vi][1][i]
                edge = PolyllaEdge_Edge(ei,vi,vf)
                edge.faces = faces
                edge_list.append(edge)
                
                for f in faces:
                    face = face_list[f]
                    face.edges.append(ei)
                ei += 1
        return edge_list
    

    def save_tetra(self, filet):

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
            tetra_list.append(t)

        return tetra_list
    
    def asign_faces_and_edges_to_tetras(self,tetra_list, face_list, edge_list):
        for f in face_list:
            for t in tetra_list:
                if len(f.neighs) == 2:
                    break
                if set(t.vertex).intersection(set(f.vertex)) == set(f.vertex):
                    t.faces.append(f.i)
                    f.neighs.append(t.i)
                    for e in f.edges:
                        if e not in t.edges:
                            t.edges.append(e)
                        edge_list[e].tetrahedrons.append(t.i)


        return tetra_list, face_list

    def asign_neighs(self,tetra, face_list):
        neighs = []
        for face in tetra.faces:
            if len(face_list[face].neighs) < 2 :#and (not tetra.is_boundary):
                tetra.is_boundary = True
                face_list[face].is_boundary = True
                # tetra.edges+=face_list[face].edges
                # tetra.edges = list(set(tetra.edges))

            face_list[face].n1 = face_list[face].neighs[0]
            if face_list[face].n1 !=tetra.i: neighs.append(face_list[face].n1)

            if not face_list[face].is_boundary:
                face_list[face].n2 = face_list[face].neighs[1]
                if face_list[face].n2 !=tetra.i: neighs.append(face_list[face].n2)
            else:
                neighs.append(-1)

        # set_version = set(neighs)
        tetra.neighs = neighs


        
    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file):
        print("Reading vertex file")
        node_list, edges_matrix = self.save_vertex(node_file) #self.read_node_file(node_file)
        print("Reading face file")
        face_list = self.save_faces(face_file,edges_matrix) #self.read_face_file(face_file)
        print("Processing edges")
        edge_list = self.save_edges(edges_matrix, face_list)#self.read_edge_file(edge_file)
        print("Reading tetra file")
        tetra_list = self.save_tetra(ele_file) # self.read_ele_file(ele_file)
        

        # Calcula los tetrahedros vecinos
        # print(face_list)
        print("Processesing faces with tetrahedorns")
        tetra_list, face_list = self.asign_faces_and_edges_to_tetras(tetra_list,face_list, edge_list)
        # for tetra in tetra_list:
        #     for f in tetra.faces:
        #         face = face_list[f]
        #         neighs = [face.n1, face.n2]
        #         curr_tetra = tetra.i
        #         neigh_tetra = neighs[0] if neighs[0] != curr_tetra else neighs[1]
        #         tetra.neighs.append(neigh_tetra)
        
        #Find the edges of each tetrahedron
        # for tetra in tetra_list:
        #     for f in tetra.faces:
        #         face = face_list[f]
        #         ## add edges to tetrahedron
        #         tetra_edges_aux = []
        #         for edge_index in face.edges:
        #             tetra_edges_aux.append(edge_list[edge_index].i)
        #         tetra.edges.extend(tetra_edges_aux)
        #     tetra.edges = [*set(tetra.edges)]


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

        for tetra in range(len(tetra_list)):
            self.asign_neighs(tetra_list[tetra],face_list)

        # Calculate all the tetrahedrons adjacent to each edge in order
        #This do it using brute force
        #self.calculate_tetrahedrons_for_edge(edge_list, tetra_list)
        #This do it using the first tetrahedron, if the edge is boundary, then the first tetrahedron MUST BE boundary.
        # for edge in edge_list:
        #     self.tetrahedrons_adjcacents_to_edge(edge.i, tetra_list, face_list, edge_list)

        # Imprime los tetrahedros
        #for t in range(0, len(tetra_list)):
        #    print("tetrahedron ", t, ":", tetra_list[t].v1, tetra_list[t].v2, tetra_list[t].v3, tetra_list[t].v4, tetra_list[t].faces, tetra_list[t].neighs, tetra_list[t].is_boundary, tetra_list[t].edges)

        

        return node_list, face_list, tetra_list, edge_list

    # Circle around an edge e to find their adjacent tetrahedrons and faces and store them in order
    # If the edge es boundary, then the first_tetrahedron MUST BE boundary.
    # def tetrahedrons_adjcacents_to_edge(self, edge, tetra_list, face_list, edge_list):
    #     tetra_origin = edge_list[edge].first_tetra
    #     # Search face adjacent to tetra_origin that contains edge
    #     f = []
    #     for face in tetra_list[tetra_origin].faces:
    #         if edge in face_list[face].edges:
    #             f.append(face)
    #     #t_next = tetra adjcaent to f_origin that is not tetra_origin and is not boundary
    #     tetra_1 = face_list[f[0]].n1 if face_list[f[0]].n1 != tetra_origin else face_list[f[0]].n2
    #     tetra_2 = face_list[f[1]].n1 if face_list[f[1]].n1 != tetra_origin else face_list[f[1]].n2
    #     if tetra_1 == -1:
    #         tetra_next = tetra_2
    #         f_next = f[1]
    #     else:
    #         tetra_next = tetra_1
    #         f_next = f[0]
    #     faces = []
    #     tetras = [tetra_origin]
    #     #print("edge: ", edge, " border ", edge_list[edge].is_boundary ," tetra_origin: ", tetra_origin, " tetra_next: ", tetra_next, edge_list[edge].tetrahedrons)
    #     while tetra_next != tetra_origin:
    #         if tetra_next == -1:
    #             break
    #         tetras.append(tetra_next)
    #         faces.append(f_next)    
    #         #face that contains edge and is not f_origin
    #         for face in tetra_list[tetra_next].faces:
    #             if edge in face_list[face].edges and face != f_next:
    #                 f_next = face
    #                 break
    #         tetra_next = face_list[f_next].n1 if face_list[f_next].n1 != tetra_next else face_list[f_next].n2
    #     faces.append(f_next)
    #     edge_list[edge].tetrahedrons = tetras
    #     edge_list[edge].faces = faces


    # Calculate a list of tetrahedrons adjacent to each edge
    # only use this functions when you have edges adjacents to two tetrahedrons but no adjacent by any face
    # def calculate_tetrahedrons_for_edge(self, ea = self.node_list[v1]ahedrons)]    

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

    # def read_node_file(self, filename):
    #     print("reading node file: "+ filename)
    #     f = open(filename, "r")
    #     node_list = []
    #     next(f)
    #     for line in f:
    #         line = line.split()
    #         #v1, v2, v3, boundary_marker
    #         if line[0] != '#':
    #             node_temp = Vertex(int(line[0]), float(line[1]), float(line[2]), float(line[3]))
    #             node_list.append(node_temp)
    #     f.close()
    #     return node_list
    
    def save_faces(self, filef, edges_matrix,n_node,face_matrix):
    
        face_list = []
        file = open(filef, "r")
        next(file)
        # face_matrix = [[None]*n_node]*n_node# en c++ es un arreglo[nnode][nnode][nnode]

        
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
            
            # if face_matrix[v[0]][v[1]]:
            #     face_matrix[v[0]][v[1]][v[2]] = fi
            #     print(v[0],v[1],v[2],face_matrix[v[0]][v[1]])
            # # print(face_matrix)
            # else:
            #     face_matrix[v[0]][v[1]]={v[2]:fi}
            #     print(v[0],v[1],v[2],face_matrix[v[0]][v[1]])
                # print(face_matrix[v[0]][v[1]])
            # print(v[0],v[1],face_matrix[v[0]][v[1]])
            savedE1 = False
            savedE2 = False
            savedE3 = False

            v.sort()
            if v2 not in edges_matrix[v1][0] and v1 not in edges_matrix[v2][0]:
                edges_matrix[v1][0].append(v2)
                edges_matrix[v1][1].append([fi])
                savedE1 = True

            if v3 not in edges_matrix[v2][0] and v2 not in edges_matrix[v3][0]:
                edges_matrix[v2][0].append(v3)
                edges_matrix[v2][1].append([fi])
                savedE2 = True
            if v1 not in edges_matrix[v3][0] and v3 not in edges_matrix[v1][0]:
                edges_matrix[v3][0].append(v1)
                edges_matrix[v3][1].append([fi])
                savedE3 = True

            #if it isn't saved it already exist (only two options)
            if not savedE1:
                if v2 in edges_matrix[v1][0]:
                    index = edges_matrix[v1][0].index(v2)
                    edges_matrix[v1][1][index].append(fi)
                else:
                    index = edges_matrix[v2][0].index(v1)
                    edges_matrix[v2][1][index].append(fi)

            if not savedE2:
                if v3 in edges_matrix[v2][0]:
                    index = edges_matrix[v2][0].index(v3)
                    edges_matrix[v2][1][index].append(fi)
                else:
                    index = edges_matrix[v3][0].index(v2)
                    edges_matrix[v3][1][index].append(fi)
            if not savedE3:
                if v1 in edges_matrix[v3][0]:
                    index = edges_matrix[v3][0].index(v1)
                    edges_matrix[v3][1][index].append(fi)
                else:
                    index = edges_matrix[v1][0].index(v3)
                    edges_matrix[v1][1][index].append(fi)
        # print(face_matrix,'\n',len(face_matrix))
        file.close()
        return face_list, face_matrix

    # def read_face_file(self, filename):
    #     print("reading face file: "+ filename)
    #     f = open(filename, "r")
    #     face_list = []
    #     next(f)
    #     for line in f:
    #         line = line.split()
    #         ## v1, v2, v3, boundary_marker, n1, n2
    #         if line[0] != '#':
    #             v1 = int(line[1])
    #             v2 = int(line[2])
    #             v3 = int(line[3])
    #             boundary_marker = (int(line[4]) == 1 or int(line[4]) == -1)
    #             n1 = int(line[5])
    #             n2 = int(line[6])
    #             face_temp = Face(int(line[0]), v1, v2, v3, boundary_marker, n1, n2)
    #             face_list.append(face_temp)
    #     f.close()
    #     return face_list

    # def read_ele_file(self, filename):
    #     print("reading ele file: "+ filename)
    #     f = open(filename, "r")
    #     tetrahedron_list = []
    #     next(f)
    #     for line in f:
    #         line = line.split()
    #         #v1, v2, v3, v4
    #         if line[0] != '#':
    #             tetra_temp = Tetrahedron(int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]))
    #             tetrahedron_list.append(tetra_temp)
    #     f.close()
    #     return tetrahedron_list
    
    def save_edges(self, matrix, face_list):
        edge_list = []
        ei = 0
        for vi in range(len(matrix)):
            for i in range(len(matrix[vi][0])):
                vf = matrix[vi][0][i]
                faces = matrix[vi][1][i]
                edge = Edge(ei,vi,vf)
                edge.faces = faces
                edge_list.append(edge)
                # print(vi,',',vf)
                
                for f in faces:
                    face = face_list[f]
                    face.edges.append(ei)
                ei += 1
        return edge_list
    
    # def look_for_faces(self, v1, v2, v3, v4, tetra, face_list):
    #     faces = []
    #     edges = []
    #     c = 0
    #     for face in face_list:
    #             if c >= 4:
    #                 break
    #             if (v1 in face.vertex) and (v2 in face.vertex) and (v3 in face.vertex):
    #                 faces.append(face.i)
    #                 face.neighs.append(tetra.i)
    #                 edges += face.edges
    #                 c += 1
    #             if (v2 in face.vertex) and (v3 in face.vertex) and (v4 in face.vertex):
    #                 faces.append(face.i)
    #                 face.neighs.append(tetra.i)
    #                 edges += face.edges
    #                 c += 1
    #             if (v3 in face.vertex) and (v4 in face.vertex) and (v1 in face.vertex):
    #                 faces.append(face.i)
    #                 face.neighs.append(tetra.i)
    #                 edges += face.edges
    #                 c += 1
    #             if (v4 in face.vertex) and (v2 in face.vertex) and (v1 in face.vertex):
    #                 faces.append(face.i)
    #                 face.neighs.append(tetra.i)
    #                 edges += face.edges
    #                 c += 1
    #     tetra.edge = list(set(edges))
    #     return faces

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
            self.asign_faces(t,face_matrix,face_list)
            tetra_list.append(t)

        file.close()
        return tetra_list
    
    def asign_faces(self,tetra, face_matrix, face_list):
        faces = []
        v = [tetra.v1,tetra.v2,tetra.v3]
        v.sort()
        # print('tetra ',tetra.i)
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f1 = node.i
                        faces.append(f1)
                        face_list[f1].neighs.append(tetra.i)
                        # print(tetra.i,face_list[f1].neighs )
                        
        # print(found)
        v = [tetra.v2,tetra.v3,tetra.v4]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f2 = node.i
                        faces.append(f2)
                        face_list[f2].neighs.append(tetra.i)
                        # print(tetra.i,face_list[f2].neighs )
                        
        # print(found)
        v = [tetra.v3,tetra.v4,tetra.v1]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f3 = node.i
                        faces.append(f3)
                        face_list[f3].neighs.append(tetra.i)
                        
                        # print(tetra.i,face_list[f3].neighs )
        # print(found)
        v = [tetra.v4,tetra.v1,tetra.v2]
        v.sort()
        for tree in face_matrix[v[0]]:
            if tree.get_root() == v[1]:
                for node in tree.node_list:
                    if node.v3 == v[2]:
                        f4 = node.i
                        faces.append(f4)
                        face_list[f4].neighs.append(tetra.i)
                        
                        # print(tetra.i,face_list[f4].neighs )
        # print(found)
        
        tetra.faces = faces
        # print('faces to tetra',tetra.i,faces, tetra)
        return

    # def asign_tetras_to_faces(self,tetra_list, face_list):

    #     for f in face_list:
    #         for t in tetra_list:
    #             if len(f.neighs) == 2:
    #                 break
    #             if set(t.vertex).intersection(set(f.vertex)) == set(f.vertex):
    #                 t.faces.append(f.i)
    #                 f.neighs.append(t.i)
    #                 if len(t.faces) == 4:
    #                     print('tetra ', t.i)
    #                     print(t.faces)


        # return tetra_list, face_list

    def asign_neighs(self,tetra, face_list):
        neighs = []
        # print(tetra.faces)
        for face in tetra.faces:
            if len(face_list[face].neighs) < 2:
                tetra.is_boundary = True
                face_list[face].is_boundary = True
                # print('boundary')
                # tetra.edges+=face_list[face].edges
                # tetra.edges = list(set(tetra.edges))

            face_list[face].n1 = face_list[face].neighs[0]
            if face_list[face].n1 !=tetra.i: 
                neighs.append(face_list[face].n1)
                # print('agrega n1')
            if not face_list[face].is_boundary:
                face_list[face].n2 = face_list[face].neighs[1]
                if face_list[face].n2 !=tetra.i: 
                    neighs.append(face_list[face].n2)
                    # print('agrega n2')
            else:
                neighs.append(-1)
                # print('agrega -1')

        # set_version = set(neighs)
        tetra.neighs = neighs
        # print(tetra.i,tetra.neighs)


    # def read_edge_file(self, filename):
    #     print("reading edge file: "+ filename)
    #     edge_list = []
    #     with open(filename, 'r') as file:
    #         for i, line in enumerate(file):
    #             if i == 0 or "#" in line:
    #                 continue
    #             line = line.split()
    #             i = int(line[0])
    #             e1 = int(line[1])
    #             e2 = int(line[2])
    #             current_edge = Edge(i, e1, e2)
    #             current_edge.is_boundary = True if int(line[3]) == 1 else False
    #             current_edge.first_tetra = int(line[4])
    #             edge_list.append(current_edge)
    #     return edge_list


        
    def construct_tetrahedral_mesh(self, node_file, face_file, ele_file):
        print("Reading vertex file")
        node_list, edges_matrix,face_matrix = self.save_vertex(node_file) #self.read_node_file(node_file)
        print("Reading face file")
        face_list, face_matrix = self.save_faces(face_file,edges_matrix, len(node_list),face_matrix) #self.read_face_file(face_file)
        print("Processing edges")
        edge_list = self.save_edges(edges_matrix, face_list)#self.read_edge_file(edge_file)
        print("Reading tetra file")
        tetra_list = self.save_tetra(ele_file,face_matrix,face_list) # self.read_ele_file(ele_file)
        

        # asign to each face their edges
        #CAMBIAR POR ALGO MAS EFICIENTE, no O(n^2)
        # for face in face_list:
        #     e1 = (face.v1, face.v2)
        #     e2 = (face.v2, face.v3)
        #     e3 = (face.v3, face.v1)
        #     for edge in edge_list:
        #         if (edge.v1, edge.v2) == e1 or (edge.v2, edge.v1) == e1:
        #             face.edges.append(edge.i)
        #         if (edge.v1, edge.v2) == e2 or (edge.v2, edge.v1) == e2:
        #             face.edges.append(edge.i)
        #         if (edge.v1, edge.v2) == e3 or (edge.v2, edge.v1) == e3:
        #             face.edges.append(edge.i)
                #agregar que si len(face.edges == 3) se para esto
            #print("face " + str(face.i) + " has this edges " + str(face.edges))
        

        # add the faces of each tetrahedron
        # for f in range(0, len(face_list)):
        #     # Calcula neigh tetrahedras from faces
        #     neigh1 = face_list[f].neighs[0]
        #     neigh2 = face_list[f].neighs[1]
        #     if neigh1 != -1:
        #         tetra_list[neigh1].faces.append(f)
        #     if neigh2 != -1:
        #         tetra_list[neigh2].faces.append(f)
            #Se marca si un tetra es boundary
            # if neigh1 == -1:
            #     tetra_list[neigh2].is_boundary = True
            # if neigh2 == -1:
            #     tetra_list[neigh1].is_boundary = True

        # Calcula los tetrahedros vecinos
        # print(face_list)
        print("Processesing faces with tetrahedorns")
        # tetra_list, face_list = self.asign_tetras_to_faces(tetra_list,face_list)
        # for tetra in tetra_list:
        #     for f in tetra.faces:
        #         face = face_list[f]
        #         neighs = [face.n1, face.n2]
        #         curr_tetra = tetra.i
        #         neigh_tetra = neighs[0] if neighs[0] != curr_tetra else neighs[1]
        #         tetra.neighs.append(neigh_tetra)
        
        #Find the edges of each tetrahedron
        # for tetra in tetra_list:
        #     for f in tetra.faces:
        #         face = face_list[f]
        #         ## add edges to tetrahedron
        #         tetra_edges_aux = []
        #         for edge_index in face.edges:
        #             tetra_edges_aux.append(edge_list[edge_index].i)
        #         tetra.edges.extend(tetra_edges_aux)
        #     tetra.edges = [*set(tetra.edges)]


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

        for tetra in range(len(tetra_list)):
            self.asign_neighs(tetra_list[tetra],face_list)

        # Calculate all the tetrahedrons adjacent to each edge in order
        #This do it using brute force
        #self.calculate_tetrahedrons_for_edge(edge_list, tetra_list)
        #This do it using the first tetrahedron, if the edge is boundary, then the first tetrahedron MUST BE boundary.
        # for edge in edge_list:
        #     self.tetrahedrons_adjcacents_to_edge(edge.i, tetra_list, face_list, edge_list)

        # Imprime los tetrahedros
        #for t in range(0, len(tetra_list)):
        #    print("tetrahedron ", t, ":", tetra_list[t].v1, tetra_list[t].v2, tetra_list[t].v3, tetra_list[t].v4, tetra_list[t].faces, tetra_list[t].neighs, tetra_list[t].is_boundary, tetra_list[t].edges)

        

        return node_list, face_list, tetra_list, edge_list

    # Circle around an edge e to find their adjacent tetrahedrons and faces and store them in order
    # If the edge es boundary, then the first_tetrahedron MUST BE boundary.
    # def tetrahedrons_adjcacents_to_edge(self, edge, tetra_list, face_list, edge_list):
    #     tetra_origin = edge_list[edge].first_tetra
    #     # Search face adjacent to tetra_origin that contains edge
    #     f = []
    #     for face in tetra_list[tetra_origin].faces:
    #         if edge in face_list[face].edges:
    #             f.append(face)
    #     #t_next = tetra adjcaent to f_origin that is not tetra_origin and is not boundary
    #     tetra_1 = face_list[f[0]].n1 if face_list[f[0]].n1 != tetra_origin else face_list[f[0]].n2
    #     tetra_2 = face_list[f[1]].n1 if face_list[f[1]].n1 != tetra_origin else face_list[f[1]].n2
    #     if tetra_1 == -1:
    #         tetra_next = tetra_2
    #         f_next = f[1]
    #     else:
    #         tetra_next = tetra_1
    #         f_next = f[0]
    #     faces = []
    #     tetras = [tetra_origin]
    #     #print("edge: ", edge, " border ", edge_list[edge].is_boundary ," tetra_origin: ", tetra_origin, " tetra_next: ", tetra_next, edge_list[edge].tetrahedrons)
    #     while tetra_next != tetra_origin:
    #         if tetra_next == -1:
    #             break
    #         tetras.append(tetra_next)
    #         faces.append(f_next)    
    #         #face that contains edge and is not f_origin
    #         for face in tetra_list[tetra_next].faces:
    #             if edge in face_list[face].edges and face != f_next:
    #                 f_next = face
    #                 break
    #         tetra_next = face_list[f_next].n1 if face_list[f_next].n1 != tetra_next else face_list[f_next].n2
    #     faces.append(f_next)
    #     edge_list[edge].tetrahedrons = tetras
    #     edge_list[edge].faces = faces


    # Calculate a list of tetrahedrons adjacent to each edge
    # only use this functions when you have edges adjacents to two tetrahedrons but no adjacent by any face
    # def calculate_tetrahedrons_for_edge(self, edge_list, tetra_list):
    #     for tetra in tetra_list:
    #         for edge in tetra.edges:
    #             edge_list[edge].tetrahedrons.append(tetra.i)
    #             if tetra.is_boundary:
    #                 edge_list[edge].first_tetra = tetra.i
    #     #remove repeat tetrahedrons from edges
    #     for edge in edge_list:
    #         edge.tetrahedrons = [*set(edge.tetrahedrons)]    

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

        


def save_vertex(file):
        matrix = []
        vertex_list = []
        for line in file:
            l = line.split()
            if l[0] == '#' or len(l) < 4:
                continue
            v = Vertex(int(l[0]), float(l[1]), float(l[2]), float(l[3]))
            vertex_list.append(v)
            matrix.append([[],[]]) # in c++ is not necessary
        return vertex_list,matrix

def save_vertex_tetra_version(file):
        edges_matrix = []
        faces_matrix = []
        vertex_list = []
        for line in file:
            l = line.split()
            v = Vertex(int(l[0]), float(l[1]), float(l[2]), float(l[3]))
            vertex_list.append(v)
            edges_matrix.append([[],[]]) # in c++ is not necessary
            faces_matrix.append([[],[]]) # in c++ is not necessary

        return vertex_list,edges_matrix, faces_matrix
def save_edges(matrix, face_list):
    edge_list = []
    ei = 0
    for vi in range(len(matrix)):
        for i in range(len(matrix[vi][0])):
            vf = matrix[vi][0][i]
            faces = matrix[vi][1][i]
            edge = Edge(ei,vi,vf)
            edge.faces = faces
            edge_list.append(edge)
            
            for f in faces:
                face = face_list[f]
                face.edges.append(ei)
            ei += 1
    return edge_list

def inFm(fm, v1,v2,v3):
    fm1 = set(fm[v1][0])
    fm2 = set(fm[v2][0])
    fm3 = set(fm[v3][0])
    return set([v2,v3]) in fm1 or set([v3,v1]) in fm2 or set([v1,v2]) in fm3

def save_tetra_faces(fm, t):
    if not inFm(fm, t.v1, t.v2, t.v3):
        fm[t.v1][0].append([t.v2,t.v3])
        fm[t.v1][1].append([t.i])
    # else:
    #     if 
    #     #que hacer si ya existe
    #     #buscar cual existe o generar forma de saber cual se guardó

    if not inFm(fm, t.v2, t.v3, t.v4):
        fm[t.v2][0].append([t.v3,t.v4])
        fm[t.v2][1].append([t.i])
    if not inFm(fm, t.v3, t.v4, t.v1):
        fm[t.v3][0].append([t.v4,t.v1])
        fm[t.v3][1].append([t.i])
    if not inFm(fm, t.v4, t.v1, t.v2):
        fm[t.v4][0].append([t.v1,t.v2])
        fm[t.v4][1].append([t.i])
    
    return fm


def save_tetra_bf(file, face_matrix):

    tetra_list = []

    for line in file:
        l = line.split()
        if l[0] == '#' or len(l) < 5:
            continue
        #print(l)
        v1 = int(l[1])
        v2 = int(l[2])
        v3 = int(l[3])
        v4 = int(l[4])
        ti = int(l[0])
        t = Tetrahedron(ti, v1,v2,v3,v4)
        tetra_list.append(t)
        face_matrix = save_tetra_faces(face_matrix,t)
    return tetra_list

def look_up_for_tetra(face, tetra_list):
    cont = 0
    for t in tetra_list:
        if set(t.vertex).intersection(set(face.vertex)) == set(face.vertex):
            face.neighs.append(t.i)
            t.faces.append(face.i)
        if cont >= 2:
            break
        

def save_faces_at(edges_matrix, face_matrix):
    
    face_list = []
    index = 0
    for i in range(len(face_matrix)):
        vertex_pairs = face_matrix[i][0]
        tetras = face_matrix[i][1][i]
        if len(vertex_pairs) > 0:
            for pairI in range(len(vertex_pairs)):
                f = Face(index, i,vertex_pairs[pairI][0],vertex_pairs[pairI][1])
                # f.neighs = [tetras[2*pairI],tetras[2*pairI+1]]
                # tetras[2*pairI].faces.append(index)
                # tetras[2*pairI+1].faces.append(index)
                index += 1

            continue
        #print(l)
        # v1 = int(l[1])
        # v2 = int(l[2])
        # v3 = int(l[3])
        # fi = int(l[0])
        # f = Face(fi, v1,v2,v3)
        # face_list.append(f)

        # savedE1 = False
        # savedE2 = False
        # savedE3 = False


        # if v2 not in edges_matrix[v1][0] and v1 not in edges_matrix[v2][0]:
        #     edges_matrix[v1][0].append(v2)
        #     edges_matrix[v1][1].append([fi])
        #     savedE1 = True

        # if v3 not in edges_matrix[v2][0] and v2 not in edges_matrix[v3][0]:
        #     edges_matrix[v2][0].append(v3)
        #     edges_matrix[v2][1].append([fi])
        #     savedE2 = True
        # if v1 not in edges_matrix[v3][0] and v3 not in edges_matrix[v1][0]:
        #     edges_matrix[v3][0].append(v1)
        #     edges_matrix[v3][1].append([fi])
        #     savedE3 = True

        # #if it isn't saved it already exist (only two options)
        # if not savedE1:
        #     if v2 in edges_matrix[v1][0]:
        #         index = edges_matrix[v1][0].index(v2)
        #         edges_matrix[v1][1][index].append(fi)
        #     else:
        #         index = edges_matrix[v2][0].index(v1)
        #         edges_matrix[v2][1][index].append(fi)

        # if not savedE2:
        #     if v3 in edges_matrix[v2][0]:
        #         index = edges_matrix[v2][0].index(v3)
        #         edges_matrix[v2][1][index].append(fi)
        #     else:
        #         index = edges_matrix[v3][0].index(v2)
        #         edges_matrix[v3][1][index].append(fi)
        # if not savedE3:
        #     if v1 in edges_matrix[v3][0]:
        #         index = edges_matrix[v3][0].index(v1)
        #         edges_matrix[v3][1][index].append(fi)
        #     else:
        #         index = edges_matrix[v1][0].index(v3)
        #         edges_matrix[v1][1][index].append(fi)
    return face_list




def saveLog(filename, info_list):
      f = open(filename,'w')
      for i in info_list:
            f.write(str(i))



# arguments = sys.argv
# filename = arguments[1]
# # vertexs = arguments[1]
# # faces = arguments[2]
# # tetras = arguments[3]
# vertexs = filename + ".node"
# faces = filename + ".face"
# tetras = filename + ".ele"
# t0= time.time()
# mesh = TetrahedronMesh(vertexs, faces, tetras)
# print("vecinos")
# for tetra in range(len(mesh.tetra_list)):
#     mesh.asign_neighs(mesh.tetra_list[tetra],mesh.face_list)
# saveLog("face_log.txt",mesh.face_list)
# saveLog("tetra_log.txt",mesh.tetra_list)
# tf = time.time()
# print("Processing the data:", (tf-t0), "segundos")
# print(mesh.tetra_list)
# mesh.get_info()
# print("Reading vertex file")
# filev = open(vertexs, 'r')

# vertex_list, edges_matrix = save_vertex(filev)

# print("Reading face file")
# filef = open(faces, 'r')
# face_list = save_faces(filef, edges_matrix)

# print("Processing edges")
# edge_list = save_edges(edges_matrix, face_list)

# print("Reading tetrahedron file")
# filet = open(tetras, 'r')
# tetra_list = save_tetra(filet,face_list)

# print("Processesing faces with tetrahedorns")
# tetra_list,face_list = asign_faces_to_tetras(tetra_list,face_list)
# tf = time.time()
# print("Processing the data:", (tf-t0), "segundos")
# saveLog("logTetra.txt", tetra_list)
# saveLog("logFace.txt", face_list)+")\n"self.n1