from mesh import TetrahedronMesh
from collections import Counter


class PolyllaEdge:
    def __init__(self, mesh):
        self.mesh = mesh
        self.calculate_edges_length()
        # use to check if the order of in which the edges are join is important or not
        # by defect the list of tetrahedros is of each edge is in counterclockwise order, this function do a random order
        #self.calculate_tetrahedrons_for_edge()  

        #Sort edges by length longest to shortest
        #Cambiar a futuro por algo que genere una lista de indice sin tener que primero crear una una lista de objetos
        self.edges_sorted_by_length = sorted(self.mesh.edge_list, key=lambda edge: edge.length, reverse=True)
        for e in range(0,len(self.edges_sorted_by_length)):
            self.edges_sorted_by_length[e] = self.edges_sorted_by_length[e].i
        
        for i in range(0,len(self.edges_sorted_by_length)):
            print("Edge:", self.edges_sorted_by_length[i], "length:", self.mesh.edge_list[self.edges_sorted_by_length[i]].length, self.mesh.edge_list[self.edges_sorted_by_length[i]].tetrahedrons)

        #Calculate longest edge of each tetrahedron
        self.longest_edges_each_tetra = self.calculate_longest_edges_of_tetra()
        
        #Create a list of visited tetrahedrons
        self.visited_tetra = [False] * mesh.n_tetrahedrons

        #generate a list of polyhedrons
        self.polyhedron_mesh_with_tetras = []
        for edge in self.edges_sorted_by_length:
            Polyhedron = []
            self.DepthFirstSearch(Polyhedron, edge)
            #Remove empty polyhedrons
            if len(Polyhedron) > 0:
                self.polyhedron_mesh_with_tetras.append(Polyhedron)
        
        #Polyhedron = []
        #self.DepthFirstSearch(Polyhedron, self.edges_sorted_by_length[0])
        ##Remove empty polyhedrons
        #if len(Polyhedron) > 0:
        #    self.polyhedron_mesh_with_tetras.append(Polyhedron)
        
        print("Polyhedrons with tetras: ", self.polyhedron_mesh_with_tetras)

        #Conseguir las caras de borde de las terminal-edge region
        self.polyhedron_mesh = []
        for poly in self.polyhedron_mesh_with_tetras:
            polyhedron = []
            #Generate a list of a the faces of each terminal-edge region
            for tetra in poly:
                polyhedron.extend(self.mesh.tetra_list[tetra].faces)
            #Remove repeat faces, those faces are interior faces
            polyhedron = [*set(polyhedron)]
            self.polyhedron_mesh.append(polyhedron)
    

    def DepthFirstSearch(self, polyhedron, edge):
        #print("Edge:", edge, "tetrahedrons", self.mesh.edge_list[edge].tetrahedrons)
        for tetra in self.mesh.edge_list[edge].tetrahedrons:
            if self.visited_tetra[tetra] == False:
                self.visited_tetra[tetra] = True
                polyhedron.append(tetra)
                e_max = self.longest_edges_each_tetra[tetra]
                if edge != e_max: #this line is not necesary, but it makes the code faster
                    self.DepthFirstSearch(polyhedron,e_max)   

    # Cambiar a otro que no sea fuerza bruta, este lo hizo github copilot
    # Hacer que la lista gire al rederedor de cada edge en counterclocwise
    def calculate_tetrahedrons_for_edge(self):
        #for edge in self.mesh.edge_list:
        #    for tetra in self.mesh.tetra_list:
        #        if edge.i in tetra.edges:
        #            edge.tetrahedrons.append(tetra.i)
        #    edge.tetrahedrons = [*set(edge.tetrahedrons)]
        for tetra in self.mesh.tetra_list:
            for edge in tetra.edges:
                self.mesh.edge_list[edge].tetrahedrons.append(tetra.i)
        #remove repeat tetrahedrons from edges
        for edge in self.mesh.edge_list:
            edge.tetrahedrons = [*set(edge.tetrahedrons)]    



    #Calculate longest edge of each tetrahedron
    #esta wea se puede hacer en una sola linea, la hizo github copilot, quedo de pana
    def calculate_longest_edges_of_tetra(self):
        longest_edges = []
        for tetra in self.mesh.tetra_list:
            edges = tetra.edges
            e0 = self.mesh.edge_list[edges[0]].length
            e1 = self.mesh.edge_list[edges[1]].length
            e2 = self.mesh.edge_list[edges[2]].length
            e3 = self.mesh.edge_list[edges[3]].length
            e4 = self.mesh.edge_list[edges[4]].length
            e5 = self.mesh.edge_list[edges[5]].length

            max_length = max(e0,e1,e2,e3,e4,e5)
            if max_length == e0:
                longest_edges.append(edges[0])
            elif max_length == e1:
                longest_edges.append(edges[1])
            elif max_length == e2:
                longest_edges.append(edges[2])
            elif max_length == e3:
                longest_edges.append(edges[3])
            elif max_length == e4:
                longest_edges.append(edges[4])
            elif max_length == e5:
                longest_edges.append(edges[5])
            else:
                print("Error")

        return longest_edges
 

    #Length of each edge
    def calculate_edges_length(self):
        for edge in self.mesh.edge_list:
            v1 = self.mesh.node_list[edge.v1]
            v2 = self.mesh.node_list[edge.v2]
            distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
            edge.length = distance

    def printOFF_faces(self, filename, faces):
            print("writing OFF file: "+ filename)
            with open(filename, 'w') as fh:
                fh.write("OFF\n")
                fh.write("%d %d 0\n" % (mesh.n_nodes, len(faces)))
                for v in self.mesh.node_list:
                    fh.write("%f %f %f\n" % (v.x, v.y, v.z))
                for f in faces:
                    v1 = self.mesh.face_list[f].v1
                    v2 = self.mesh.face_list[f].v2
                    v3 = self.mesh.face_list[f].v3
                    fh.write("3 %d %d %d\n" % (v1, v2, v3))

    def printOFF_polyhedralmesh(self, filename):
        print("writing OFF file: "+ filename)
        with open(filename, 'w') as fh:
            fh.write("OFF\n")
            fh.write("%d %d 0\n" % (self.mesh.n_nodes, len(self.polyhedron_mesh)))
            for v in self.mesh.node_list:
                fh.write("%f %f %f\n" % (v.x, v.y, v.z))
            for polyhedra in self.polyhedron_mesh:
                for f in polyhedra:
                    v1 = self.mesh.face_list[f].v1
                    v2 = self.mesh.face_list[f].v2
                    v3 = self.mesh.face_list[f].v3
                    fh.write("3 %d %d %d\n" % (v1, v2, v3))    

    def get_info(self):
        print("PolyllaEdge info:")
        print("Number of polyhedrons:", len(self.polyhedron_mesh))

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
    polylla_mesh = PolyllaEdge(mesh)


    for i in range(0, len(polylla_mesh.polyhedron_mesh)):
        print(polylla_mesh.polyhedron_mesh[i])
        polylla_mesh.printOFF_faces(file + "POLYLLAEDGE_polyhedron_" + str(i) + ".off", polylla_mesh.polyhedron_mesh[i])
    
    polylla_mesh.get_info()
    #polylla_mesh.printOFF_polyhedralmesh(filename + "_polyhedron_mesh.off")
    #polylla_mesh.printOFF_faces(filename + "_frontier_faces.off", sorted(set([num for sublist in polylla_mesh.polyhedron_mesh for num in sublist])))

    #print(polylla_mesh.polyhedron_mesh)
    ### detect repeated face in polyhgons from polyhedron_mesh
    #repeated_faces = []
    #for i in range(0, len(polylla_mesh.polyhedron_mesh)):
    #    print("polyhedron: " + str(i) + " " + str(polylla_mesh.polyhedron_mesh[i]))
    #    print([k for k,v in Counter(polylla_mesh.polyhedron_mesh[i]).items() if v>1])
