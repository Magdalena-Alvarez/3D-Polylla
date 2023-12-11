# Los polihedros se represen como un conjunto de tetrahedros
# se deben transformar a un conjunto de caras


from mesh import TetrahedronMesh, Polyhedron
from collections import Counter


class PolyllaEdge:
    def __init__(self, mesh):
        self.mesh = mesh
        self.calculate_edges_length()
        self.barrier_edges = 0
        self.hanging_polyhedrons = 0
        #Sort edges by length longest to shortest
        #Cambiar a futuro por algo que genere una lista de indice sin tener que primero crear una una lista de objetos
        self.edges_sorted_by_length = sorted(self.mesh.edge_list, key=lambda edge: edge.length, reverse=True)
        for e in range(0,len(self.edges_sorted_by_length)):
            self.edges_sorted_by_length[e] = self.edges_sorted_by_length[e].i
        
        #for i in range(0,len(self.edges_sorted_by_length)):
        #    print("Edge:", self.edges_sorted_by_length[i], "length:", self.mesh.edge_list[self.edges_sorted_by_length[i]].length, self.mesh.edge_list[self.edges_sorted_by_length[i]].tetrahedrons)

        #Calculate longest edge of each tetrahedron
        self.longest_edges_each_tetra = self.calculate_longest_edges_of_tetra()
        
        #Create a list of visited tetrahedrons
        self.visited_tetra = [False] * mesh.n_tetrahedrons

        #generate a list of polyhedrons
        self.polyhedral_mesh = []
        
        for edge in self.edges_sorted_by_length:
            terminalEdgeRegion = []
            self.DepthFirstSearch(terminalEdgeRegion, edge)
            #Remove empty terminal edge regions
            if len(terminalEdgeRegion) > 0:
                # check if a polyhedron needs to be repair
                terminalEdgeRegion = self.repair_polyhedron(terminalEdgeRegion)
                has_hanging_tetra = True if len(terminalEdgeRegion) > 1 else False
                for element in terminalEdgeRegion:
                    poly = Polyhedron()
                    poly.tetras.extend(element)
                    poly.was_repaired = has_hanging_tetra
                    self.polyhedral_mesh.append(poly)
                    

        #Conseguir las caras de borde de las terminal-edge region
        for poly in self.polyhedral_mesh:
            polyhedron_faces = []
            #Generate a list of a the faces of each terminal-edge region
            for tetra in poly.tetras:
                polyhedron_faces.extend(self.mesh.tetra_list[tetra].faces)
            #Remove repeat faces, those faces are interior faces
            polyhedron = [el for el, cnt in Counter(polyhedron_faces).items() if cnt==1]
            poly.faces.extend(polyhedron)
    
    ## Function to detect and polyhedrons with hanging tetrahedrons
    ## Return a list of lists of polyhedrons
    def repair_polyhedron(self, polyhedron):
        edge_list = []
        for tetra in polyhedron:
            edge_list.extend(self.mesh.tetra_list[tetra].edges)
        #Only repeated edges are revised
        edge_list = [k for k, v in Counter(edge_list).items() if v > 1]
        # For each repead edge
        new_polyhedrons = []
        flag = False
        for edge in edge_list:
            if self.detec_barrier_edge(edge, polyhedron):
                flag = True
                self.barrier_edges += 1
                new_polyhedrons.extend(self.separate_polyhedron(edge, polyhedron))
        # if a barrier_edge was detected
        if flag:           
            return new_polyhedrons     
        return [polyhedron]

    ## Function separate polyhedron with hanging tetrahedrons
    ## Input: polyhedron and a barrier-edge
    ## Output: a list of polyhedrons
    def separate_polyhedron(self, edge, polyhedron):
        Te = self.mesh.edge_list[edge].tetrahedrons.copy() 
        #mark all tetrahedrons that are not in polyhedron as -1
        for t in range(0,len(Te)):
            if Te[t] not in polyhedron:
                Te[t] = -1
        #position of the first element -1 in Te
        pos_origin = -1
        for i in range(0,len(Te)):
            if Te[i] == -1:
                pos_origin = i
                break 
        curr = (pos_origin + 1) % len(Te)
        new_polyhedrons = []
        while curr != pos_origin:
            # If there is a hanging tetrahedron
            if Te[curr] != -1:
                polyhedron = []
                ## add all tetrahedrons until reach a void
                while Te[curr] != -1:
                    polyhedron.append(Te[curr])
                    curr = (curr + 1) % len(Te)
                new_polyhedrons.append(polyhedron)
            else:
                #Advance until reach an haing tetrahedron
                curr = (curr + 1) % len(Te)
        return new_polyhedrons

    ## Function to detect if a edge has hanging tetrahedrons
    def detec_barrier_edge(self, e, polyhedron):
        ## list of tetrahedros adjacent to edge e
        #to avoid change the original list que uses copy
        Te = self.mesh.edge_list[e].tetrahedrons.copy() 
        for t in range(0,len(Te)):
            if Te[t] not in polyhedron:
                Te[t] = -1
        count = 0
        for i in range(0,len(Te)):
            first = Te[i]
            nxt = Te[(i+1)%len(Te)]
            #change from tetra and void
            if first != -1 and nxt == -1:
                count += 1
            #change from void and tetra
            if first == -1 and nxt != -1:
                count += 1
        self.hanging_polyhedrons += count
        if count > 2:
            return True
        return False



    def DepthFirstSearch(self, polyhedron, edge):
        for tetra in self.mesh.edge_list[edge].tetrahedrons:
            if self.visited_tetra[tetra] == False:
                self.visited_tetra[tetra] = True
                polyhedron.append(tetra)
                e_max = self.longest_edges_each_tetra[tetra]
                if edge != e_max: #this line is not necesary, but it makes the code faster
                    self.DepthFirstSearch(polyhedron,e_max)   



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
           # print("writing OFF file: "+ filename)
            with open(filename, 'w') as fh:
                fh.write("OFF\n")
                fh.write("%d %d 0\n" % (self.mesh.n_nodes, len(faces)))
                for v in self.mesh.node_list:
                    fh.write("%f %f %f\n" % (v.x, v.y, v.z))
                for f in faces:
                    v1 = self.mesh.face_list[f.i].v1
                    v2 = self.mesh.face_list[f.i].v2
                    v3 = self.mesh.face_list[f.i].v3
                    fh.write("3 %d %d %d\n" % (v1, v2, v3))

    #def printOFF_polyhedralmesh(self, filename):
    #    print("writing OFF file: "+ filename)
    #    list_face = []
    #    for polyhedron in self.polyhedron_mesh:
    #        list_face.extend(polyhedron)
    #    list_face =  list(dict.fromkeys(list_face))
    #    with open(filename, 'w') as fh:
    #        fh.write("OFF\n")
    #        fh.write("%d %d 0\n" % (self.mesh.n_nodes, len(list_face)))
    #        for v in self.mesh.node_list:
    #            fh.write("%f %f %f\n" % (v.x, v.y, v.z))
    #        for f in list_face:
    #            v1 = self.mesh.face_list[f].v1
    #            v2 = self.mesh.face_list[f].v2
    #            v3 = self.mesh.face_list[f].v3
    #            fh.write("3 %d %d %d\n" % (v1, v2, v3))

    def get_info(self):
        print("PolyllaEdge info:")
        print("Number of polyhedrons:", len(self.polyhedral_mesh))
        print("Number of barrier-edges:", self.barrier_edges)
        print("Number of hanging polyhedrons:", self.hanging_polyhedrons/2)
        #calcaulte the number of polyhedrons that containts only one tetrahedron
        count = 0
        for polyhedron in self.polyhedral_mesh:
            if len(polyhedron.tetras) == 1:
                count += 1
        print("Number of polyhedrons that are tetrahedrons: " + str(count))

if __name__ == "__main__":
    folder = "data\\"
    #file = "3D_100.1"
    file = "socket.1"
    #file = "1000points.1"
    filename = folder + file
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"
    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    polylla_mesh = PolyllaEdge(mesh)


#    for i in range(0, len(polylla_mesh.polyhedron_mesh)):
#        #print(polylla_mesh.polyhedron_mesh[i])
#        polylla_mesh.printOFF_faces(folder + file + "POLYLLAEDGE_polyhedron_" + str(i) + ".off", polylla_mesh.polyhedron_mesh[i])
#    print(polylla_mesh.polyhedron_mesh[0])
    #polylla_mesh.printOFF_polyhedralmesh(folder + file + "POLYLLAEDGE.off")
    polylla_mesh.get_info()
