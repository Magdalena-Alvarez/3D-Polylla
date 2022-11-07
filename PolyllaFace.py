##Notice: Polyhedrons are representd a list of faces

from mesh import TetrahedronMesh
import numpy as np
import sys
from collections import Counter
from math import floor

class PolyllaFace:
    def __init__(self, mesh):
        self.mesh = mesh
        self.n_barrier_faces = 0
        self.polyhedra_with_barriers = 0
        
        #self.longest_faces = self.calculate_max_area_faces()
        self.longest_faces = self.calculate_max_incircle_faces()
        self.seed_tetra = self.calculate_seed_tetrahedrons()
        self.bitvector_frontier_edges = self.calculate_frontier_faces()

        self.visited_tetra = [False] * mesh.n_tetrahedrons
        self.bivector_seed_tetra_in_repair = [False] * mesh.n_tetrahedrons
        self.polyhedron_mesh = []
        for terminal_tetra in self.seed_tetra:
            polyhedron = []
            polyhedron_tetras = []
            self.DepthFirstSearch(polyhedron, polyhedron_tetras, terminal_tetra)
            #check if the polyhedron has barriers faces
            barrierFaces = self.count_barrierFaces(polyhedron)
            if barrierFaces > 0:
                #we need to repair the polyhedron, so we mark all the tetrahedrons in the polyhedron as not visited yet
                for tetra in polyhedron_tetras:
                    self.visited_tetra[tetra] = False
                self.polyhedron_mesh.append(polyhedron)
                print("Polyhedron ", len(self.polyhedron_mesh) - 1 ," with ", barrierFaces, " barriers faces")
                ##generate a list with all the  barrier-face tips 
                barrierFacesTips = self.detectBarrierFaceTips(polyhedron)       
                ## Sent the polyhedron to repair
                self.repairPhase(polyhedron, barrierFacesTips)
            #else:
                #self.polyhedron_mesh.append(polyhedron)

#############################################################################################   
# LABEL PHASE
#############################################################################################


    #Calculate length of each edge
    def calculate_edges_length(self):
        for edge in self.mesh.edge_list:
            v1 = self.mesh.node_list[edge.v1]
            v2 = self.mesh.node_list[edge.v2]
            distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
            edge.length = distance

    ## Create a list with the index of the face of each treehedral that have the longest incircle radius
    def calculate_max_incircle_faces(self):
        #Caclulate the length of each edge
        self.calculate_edges_length()

        # Calculate the incircle radius of each face
        face_radious = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length
            semiperimeter = (length_edge_a + length_edge_b + length_edge_c) / 2
            #we avoid calculate the square root to opt the code
            radious = (semiperimeter - length_edge_a) * (semiperimeter - length_edge_b) * (semiperimeter - length_edge_c) / semiperimeter
            face_radious.append(radious)

        #compare the radious of each face of all tetrahedros and return the index of the face with the longest radious
        longest_faces = []
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = face_radious[self.mesh.tetra_list[i].faces[0]]
            a1 = face_radious[self.mesh.tetra_list[i].faces[1]]
            a2 = face_radious[self.mesh.tetra_list[i].faces[2]]
            a3 = face_radious[self.mesh.tetra_list[i].faces[3]]
            maxFace = max(a0, a1, a2, a3)
            if maxFace == a0:
                longest_faces.append(0)
            elif maxFace == a1:
                longest_faces.append(1)
            elif maxFace == a2:
                longest_faces.append(2)
            elif maxFace == a3:
                longest_faces.append(3)
            else:
                print("Error en la funcion calculate_max_incircle_faces")
        return longest_faces


    def calculate_area_triangle_3d(self):
        for face in self.mesh.face_list:
            v1 = self.mesh.node_list[face.v1]
            v2 = self.mesh.node_list[face.v2]
            v3 = self.mesh.node_list[face.v3]
            av1 = np.array([v1.x, v1.y, v1.z])
            av2 = np.array([v2.x, v2.y, v2.z])
            av3 = np.array([v3.x, v3.y, v3.z])
            area = np.linalg.norm(np.cross(av2-av1, av3-av1))
            face.area = area

    # Esto puede ser un escrito en dos lineas
    def calculate_max_area_faces(self):
        self.calculate_area_triangle_3d()
        longest = []
        for tetra in self.mesh.tetra_list:
            # Calcula el area de cada cara
            a0 = self.mesh.face_list[tetra.faces[0]].area
            a1 = self.mesh.face_list[tetra.faces[1]].area
            a2 = self.mesh.face_list[tetra.faces[2]].area
            a3 = self.mesh.face_list[tetra.faces[3]].area

            maxFace = max(a0, a1, a2, a3)
            if maxFace == a0:
                longest.append(0)
            elif maxFace == a1:
                longest.append(1)
            elif maxFace == a2:
                longest.append(2)
            elif maxFace == a3:
                longest.append(3)
            else:
                print("Error en la funcion calculate_max_area_faces")
        return longest   

    # Retorna la cara maś larga como objeto cara
    def calculate_terminal_faces(self):
        terminal_faces = []
        for tetra in range(0, self.mesh.n_tetrahedrons):
                    
            # Get the longest face of tetrahedron tetra 
            longest_face_curr = self.mesh.tetra_list[tetra].faces[self.longest_faces[tetra]]

            #Calculate the tetrahedron neigh by their longest face
            neigh_index = self.mesh.tetra_list[tetra].neighs[self.longest_faces[tetra]]

            #Check which is the longest face of the neigh tetrahedron
            longest_face_neigh = self.mesh.tetra_list[neigh_index].faces[self.longest_faces[neigh_index]]

            #if the base is border or If both faces are equal, then their are the terminal face.
            if longest_face_neigh == -1 or longest_face_curr == longest_face_neigh:
                terminal_faces.append(longest_face_curr)

        #remove duplicates to avoid repeated faces
        terminal_faces = list(dict.fromkeys(terminal_faces))

        return terminal_faces



    def calculate_seed_tetrahedrons(self):
        seed_tetra = []
        for f in range(0, self.mesh.n_faces):
            #Get two tetrahedrons adjacens to the face
            n1 = self.mesh.face_list[f].n1
            n2 = self.mesh.face_list[f].n2

            #if n1 is -1, check if n2 is the longest face of its tetrahedron
            if n1 == -1 and self.mesh.tetra_list[n2].faces[self.longest_faces[n2]] == f:
                seed_tetra.append(n2)
            #if n2 is -1, check if n1 is the longest face of its tetrahedron
            elif n2 == -1 and self.mesh.tetra_list[n1].faces[self.longest_faces[n1]] == f:
                seed_tetra.append(n1)
            #if both are not -1, check if n1 and n2 are the longest face of its tetrahedron
            else:
                longest_face_n1 = self.mesh.tetra_list[n1].faces[self.longest_faces[n1]]
                longest_face_n2 = self.mesh.tetra_list[n2].faces[self.longest_faces[n2]]
                # Si no es la cara más larga de ningún tetra de n1 o n2, es una frontier-edge
                if f == longest_face_n1 and f == longest_face_n2:
                    seed_tetra.append(n1)

        return seed_tetra


    # Retorna un bitvector de largo n_faces que indica si la cara es frontier-face o no
    def calculate_frontier_faces(self):
        frontier_faces = []
        for f in range(0, self.mesh.n_faces):
            n1 = self.mesh.face_list[f].n1
            n2 = self.mesh.face_list[f].n2

            # Si la cara es de borde, es una frontier-edge
            if n1 == -1 or n2 == -1:
                frontier_faces.append(True) # True para imprimir caras de borde
            else: 
                longest_face_n1 = self.mesh.tetra_list[n1].faces[self.longest_faces[n1]]
                longest_face_n2 = self.mesh.tetra_list[n2].faces[self.longest_faces[n2]]

                # Si no es la cara más larga de ningún tetra de n1 o n2, es una frontier-edge
                frontier_faces.append(f != longest_face_n1 and f != longest_face_n2)
            
        return frontier_faces

##########################################################################################
#   TRAVEL PHASE
##########################################################################################


    # return list of faces 
    def DepthFirstSearch(self, polyhedron, polyhedron_tetras, tetra):
        self.visited_tetra[tetra] = True
        polyhedron_tetras.append(tetra)
        ## for each face of tetra
        for i in range(0, 4):
            face_id = self.mesh.tetra_list[tetra].faces[i]
            tetra_neighs = self.mesh.tetra_list[tetra].neighs
            if face_id != -1:
                #si la cara es un frontier-face, entonces no se sigue la recursión
                if self.bitvector_frontier_edges[face_id] == True:
                    polyhedron.append(face_id)
                else: #si es internal-face, se sigue la recursión por su tetra vecino
                    next_tetra = tetra_neighs[i]
                    if(self.visited_tetra[next_tetra] == False):
                        self.DepthFirstSearch(polyhedron, polyhedron_tetras, next_tetra)
        
############################################################################################################
# REPAIR PHASE
############################################################################################################


    def count_barrierFaces(self, polyhedron):
        repeated = [k for k, v in Counter(polyhedron).items() if v > 1]
        if(len(repeated) > 0):
            self.n_barrier_faces += len(repeated)
            self.polyhedra_with_barriers += 1
        return len(repeated)

    def detectBarrierFaceTips(self, terminalFace):
        barrierFacesTips = []
        #print("Detecting barrier faces of terminalFace: ", terminalFace)    
        #list of all reapeted faces
        barrierFaces = [k for k, v in Counter(terminalFace).items() if v > 1]
        #print("terminalFace: ", terminalFace)
        #for face in barrierFaces:
        #    print("face: ", face, "vertices", self.mesh.face_list[face].v1, self.mesh.face_list[face].v2, self.mesh.face_list[face].v3)
        #print("barrierFaces: ", barrierFaces)
        #List of all edges of the barrier faces
        possibleTips = set()
        for face in barrierFaces:
            possibleTips.update(self.mesh.face_list[face].edges)
        possibleTips = list(possibleTips)
        for e in possibleTips:
            #List of all faces incident to e
            face_of_edge = self.mesh.edge_list[e].faces
            # #(F_e in terminalFace)
            #if(e == 1608 or e == 2009):
                #print("face_of_edge: ", face_of_edge, "tetrahedrons incidentes: ", self.mesh.edge_list[e].tetrahedrons)
                #print("L1", list(set(face_of_edge) & set(terminalFace)))
                #print("L2", terminalFace)
            L1 = len(list(set(face_of_edge) & set(terminalFace)))
            L2 = len(terminalFace)
            if L2 - L1 == L2 - 1:
                #print(e, "is a barrier-face tip")
                barrierFacesTips.append(e)
        return barrierFacesTips


    def repairPhase(self, polyhedron, barrierFaceTips):
        tetra_list = []
        barrierFace = -1
        for e in barrierFaceTips:
            #search polyhedron that contains the edge e
            for face in polyhedron:
                if e in self.mesh.face_list[face].edges:
                    barrierFace = face
                    break
            # select the middle face indicent to e
            faces_of_barrierFaceTip = self.mesh.edge_list[e].faces
            
            n_internalFaces = len(faces_of_barrierFaceTip) - 1 
            #int adv = (internal_edges%2 == 0) ? internal_edges/2 - 1 : internal_edges/2 ;
            adv = floor(n_internalFaces/2) - 1 if n_internalFaces%2 == 0 else floor(n_internalFaces/2) 
            #because the first face is the barrierFace, advance to the next internal-face
            pos = faces_of_barrierFaceTip.index(barrierFace) + 1    
            middle_Face = faces_of_barrierFaceTip[((pos + adv)%n_internalFaces) ]
            #print("faces_of_barrierFaceTip: ", faces_of_barrierFaceTip, "barrierFace", barrierFace, "n_internalFaces", n_internalFaces,   "adv: ", adv, "pos: ", pos, "middle_Face: ", middle_Face)
            #if there no advance, the middle face is the barrierFace and there is not repair
            if(middle_Face == barrierFace):
                sys.exit("middle_Face == faces_of_barrierFaceTip")
            # convert the middle internalface into a frontier-face
            self.bitvector_frontier_edges[middle_Face] = True

            #store adjacent tetrahedrons to the sub seed list
            tetra1 = self.mesh.face_list[barrierFace].n1
            tetra2 = self.mesh.face_list[barrierFace].n2
            tetra_list.append(tetra1)
            tetra_list.append(tetra2)

            #mark to be use in the bitvector_seed_tetra
            self.bivector_seed_tetra_in_repair[tetra1] = True
            self.bivector_seed_tetra_in_repair[tetra2] = True
        
        #while tetra_list is not empty
        #print("Tetra list: ", tetra_list)
        while len(tetra_list) > 0:
            tetra_curr = tetra_list.pop()
            if self.bivector_seed_tetra_in_repair[tetra_curr] == True:
                self.bivector_seed_tetra_in_repair[tetra_curr] = False
                new_polyhedron = []
                self.DepthFirstSearch_in_repair(new_polyhedron, tetra_curr)
                self.polyhedron_mesh.append(new_polyhedron)
                #barrierFaces = self.count_barrierFaces(new_polyhedron)
                #print("NEW ", len(self.polyhedron_mesh) -1, "has barrierFaces: ", barrierFaces)

    # return list of faces 
    def DepthFirstSearch_in_repair(self, polyhedron, tetra):
        self.visited_tetra[tetra] = True
        # tetra es remove as candidate for generation of poliedron
        self.bivector_seed_tetra_in_repair[tetra] = False 
        ## for each face of tetra
        for i in range(0, 4):
            face_id = self.mesh.tetra_list[tetra].faces[i]
            tetra_neighs = self.mesh.tetra_list[tetra].neighs
            if face_id != -1:
                #si la cara es un frontier-face, entonces no se sigue la recursión
                if self.bitvector_frontier_edges[face_id] == True:
                    polyhedron.append(face_id)
                else: #si es internal-face, se sigue la recursión por su tetra vecino
                    next_tetra = tetra_neighs[i]
                    if(self.visited_tetra[next_tetra] == False):
                        self.DepthFirstSearch_in_repair(polyhedron,  next_tetra)

############################################################################################################
# EXTRA
############################################################################################################

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
        print("PolyllaFace info:")
        print("Number of polyhedrons: " + str(len(self.polyhedron_mesh)))
        print("Number of barrier faces: " + str(self.n_barrier_faces))
        print("Number of polyhedra with barrier faces: " + str(self.polyhedra_with_barriers))
        num_of_tetra = 0
        for i in range(0, len(self.polyhedron_mesh)):
            if len(self.polyhedron_mesh[i]) == 4:
                num_of_tetra += 1
        print("Number of polyhedrons that are tetrahedrons: " + str(num_of_tetra))

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
    polylla_mesh = PolyllaFace(mesh)
    for i in range(0, len(polylla_mesh.polyhedron_mesh)):
        #print(polylla_mesh.polyhedron_mesh[i])
        polylla_mesh.printOFF_faces(folder + file + "_PolyllaFACE_polyhedron_" + str(i) + ".off", polylla_mesh.polyhedron_mesh[i])
    
    polylla_mesh.get_info()
    #polylla_mesh.printOFF_polyhedralmesh(filename + "_polyhedron_mesh.off")
    #polylla_mesh.printOFF_faces(filename + "_frontier_faces.off", sorted(set([num for sublist in polylla_mesh.polyhedron_mesh for num in sublist])))

    #print(polylla_mesh.polyhedron_mesh)
    ## detect repeated face in polyhgons from polyhedron_mesh
    #repeated_faces = []
    #for i in range(0, len(polylla_mesh.polyhedron_mesh)):
    #        print("polyhedron: " + str(i) + " " + str(polylla_mesh.polyhedron_mesh[i]))
    #        print([k for k,v in Counter(polylla_mesh.polyhedron_mesh[i]).items() if v>1])

    #polylla_mesh.detect_barrierFaces() 