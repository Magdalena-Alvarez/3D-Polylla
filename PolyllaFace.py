##Notice: Polyhedrons are representd a list of faces

import statistics
from newMesh import FaceTetrahedronMesh, Polyhedron
import numpy as np
import sys
from collections import Counter
from math import floor, sqrt
import random
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import numpy as np
from utils import ccw_check
import tetgen


class PolyllaFace:
    def __init__(self, mesh, flag = 'r'):
        self.mesh = mesh
        self.flag = flag
        self.n_barrier_faces = 0
        self.polyhedra_with_barriers = 0
        self.FLAGS = {
            'r' : self.calculate_max_incircle_faces,
            'R' : self.calculate_max_circumcircle_faces,
            'tra' : self.calculate_max_triangle_aspect_faces,
            'are1' : self.calculate_max_aspect_ratio_e1_faces,
            'are2' : self.calculate_max_aspect_ratio_e2_faces,
            # 'are3' : self.calculate_max_aspect_ratio_e3_faces,
            'a' : self.calculate_max_area_faces
        }
        #self.longest_faces = self.calculate_max_area_faces()
        self.longest_faces = self.FLAGS[flag]()
        self.seed_tetra = self.calculate_seed_tetrahedrons()
        self.bitvector_frontier_faces = self.calculate_frontier_faces()

        self.visited_tetra = [False] * mesh.n_tetrahedrons
        self.bivector_seed_tetra_in_repair = [False] * mesh.n_tetrahedrons
        self.polyhedral_mesh = []
        for terminal_tetra in self.seed_tetra:
            polyhedron = []
            polyhedron_tetras = []
            self.DepthFirstSearch(polyhedron, polyhedron_tetras, terminal_tetra)
            #self.polyhedral_mesh.append(polyhedron)
            #check if the polyhedron has barriers faces
            barrierFaces = self.count_barrierFaces(polyhedron)
            if barrierFaces > 0:
                #we need to repair the polyhedron, so we mark all the tetrahedrons in the polyhedron as not visited yet
                for tetra in polyhedron_tetras:
                    self.visited_tetra[tetra] = False
                ##generate a list with all the  barrier-face tips 
                barrierFacesTips = self.detectBarrierFaceTips(polyhedron)       
                ## Sent the polyhedron to repair
                # print('pre repair',polyhedron)
                # poly = Polyhedron()
                # poly.tetras = polyhedron_tetras.copy()
                # poly.faces = polyhedron.copy()
                # self.polyhedral_mesh.append(poly)
                self.repairPhase(polyhedron, barrierFacesTips) #--> al comentarla quedan iguales
            else:
                poly = Polyhedron()
                poly.tetras = polyhedron_tetras.copy()
                poly.faces = polyhedron.copy()
                self.polyhedral_mesh.append(poly)

#############################################################################################
# FACE METRICS
#############################################################################################   
    def area(self,face):
        v1 = self.mesh.node_list[face.v1]
        v2 = self.mesh.node_list[face.v2]
        v3 = self.mesh.node_list[face.v3]
        
        #calculate the area of the triangle
        av1 = np.array([v1.x, v1.y, v1.z])
        av2 = np.array([v2.x, v2.y, v2.z])
        av3 = np.array([v3.x, v3.y, v3.z])
        area = np.linalg.norm(np.cross(av2-av1, av3-av1))
        if(area < 0):
            print('-1')
        return area

    def calculate_max_triangle_aspect_faces(self):
        self.calculate_edges_length()
        self.calculate_area_triangle_3d()
        aspects = []
        longest_faces = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length
            area = self.area(self.mesh.face_list[i])

            L_max = max(length_edge_a,length_edge_b,length_edge_c)

            q = L_max*(length_edge_a + length_edge_b + length_edge_c) / (4 * sqrt(3) * area) # type: ignore
            aspects.append(area / q)
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = aspects[self.mesh.tetra_list[i].faces[0]]
            a1 = aspects[self.mesh.tetra_list[i].faces[1]]
            a2 = aspects[self.mesh.tetra_list[i].faces[2]]
            a3 = aspects[self.mesh.tetra_list[i].faces[3]]
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
                print("Error en la función calculate_max_triangle_aspect_faces")
            # index_max_face = longest_faces[len(longest_faces)-1]
            # coordsmaxface = [self.mesh.face_list[longest_faces[len(longest_faces)-1]]]
        # print(longest_faces)
        return longest_faces
    # aspect ratio for triangles from paper A Survey of Indicators for Mesh Quality Assessment
    def calculate_max_aspect_ratio_e1_faces(self):
        self.calculate_edges_length()
        self.calculate_area_triangle_3d()
        aspects = []
        longest_faces = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length

            ar = .5 * (length_edge_a * length_edge_b * length_edge_c) / (length_edge_a + length_edge_b + length_edge_c)
            aspects.append(self.mesh.face_list[i].area * ar)
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = aspects[self.mesh.tetra_list[i].faces[0]]
            a1 = aspects[self.mesh.tetra_list[i].faces[1]]
            a2 = aspects[self.mesh.tetra_list[i].faces[2]]
            a3 = aspects[self.mesh.tetra_list[i].faces[3]]
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
                print("Error en la función calculate_max_aspect_ratio_e1_faces")

        return longest_faces
        
    def calculate_max_aspect_ratio_e2_faces(self):
        self.calculate_edges_length()
        self.calculate_area_triangle_3d()
        aspects = []
        longest_faces = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length
            semiperimeter = (length_edge_a + length_edge_b + length_edge_c) / 2
            L_max = max(length_edge_a,length_edge_b,length_edge_c)

            radious = (semiperimeter - length_edge_a) * (semiperimeter - length_edge_b) * (semiperimeter - length_edge_c) / semiperimeter
            ar = radious / L_max
            
            aspects.append(self.mesh.face_list[i].area * ar)
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = aspects[self.mesh.tetra_list[i].faces[0]]
            a1 = aspects[self.mesh.tetra_list[i].faces[1]]
            a2 = aspects[self.mesh.tetra_list[i].faces[2]]
            a3 = aspects[self.mesh.tetra_list[i].faces[3]]
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
                print("Error en la función calculate_max__aspect_ratio_e2_faces")
        return longest_faces
    
    def calculate_max_aspect_ratio_e3_faces(self):
        self.calculate_edges_length()
        self.calculate_area_triangle_3d()
        aspects = []
        longest_faces = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length
            L_max = max(length_edge_a,length_edge_b,length_edge_c)

            Radious = (length_edge_a * length_edge_b * length_edge_c) / (4 * self.area(self.mesh.face_list[i])) # type: ignore
            ar =  L_max / Radious
            
            aspects.append(ar * self.mesh.face_list[i].area)
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = aspects[self.mesh.tetra_list[i].faces[0]]
            a1 = aspects[self.mesh.tetra_list[i].faces[1]]
            a2 = aspects[self.mesh.tetra_list[i].faces[2]]
            a3 = aspects[self.mesh.tetra_list[i].faces[3]]
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
                print("Error en la función calculate_max__aspect_ratio_e3_faces")
        return longest_faces
    
    def calculate_max_circumcircle_faces(self):
        self.calculate_edges_length()
        aspects = []
        longest_faces = []
        for i in range(0, self.mesh.n_faces):
            length_edge_a = self.mesh.edge_list[self.mesh.face_list[i].edges[0]].length
            length_edge_b = self.mesh.edge_list[self.mesh.face_list[i].edges[1]].length
            length_edge_c = self.mesh.edge_list[self.mesh.face_list[i].edges[2]].length

            Radious = (length_edge_a * length_edge_b * length_edge_c) / (4 * self.area(self.mesh.face_list[i])) # type: ignore
            
            aspects.append(Radious)
        for i in range(0, self.mesh.n_tetrahedrons):
            a0 = aspects[self.mesh.tetra_list[i].faces[0]]
            a1 = aspects[self.mesh.tetra_list[i].faces[1]]
            a2 = aspects[self.mesh.tetra_list[i].faces[2]]
            a3 = aspects[self.mesh.tetra_list[i].faces[3]]
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
                print("Error en la función calculate_max__aspect_ratio_e3_faces")
        return longest_faces


#############################################################################################   
# LABEL PHASE
#############################################################################################

    #Calculate length of each edge
    def calculate_edges_length(self):
        for edge in self.mesh.edge_list:
            v1 = self.mesh.node_list[edge.v1]
            v2 = self.mesh.node_list[edge.v2]
            distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
            if(distance < 0):
                print('-1')
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
            # index_max_face = longest_faces[len(longest_faces)-1]
            # coordsmaxface = [self.mesh.face_list[longest_faces[len(longest_faces)-1]]]
        # print(longest_faces)
        return longest_faces


    def calculate_area_triangle_3d(self):
        for face in self.mesh.face_list:
            v1 = self.mesh.node_list[face.v1]
            v2 = self.mesh.node_list[face.v2]
            v3 = self.mesh.node_list[face.v3]
            
            #calculate the area of the triangle
            av1 = np.array([v1.x, v1.y, v1.z])
            av2 = np.array([v2.x, v2.y, v2.z])
            av3 = np.array([v3.x, v3.y, v3.z])
            area = np.linalg.norm(np.cross(av2-av1, av3-av1))
            # print(face.i, area)
            if(area < 0):
                print('-1')
            face.area = area*0.5

    # Esto puede ser un escrito en dos lineas
    def calculate_max_area_faces(self):
        self.calculate_area_triangle_3d()
        longest = []
        for tetra in self.mesh.tetra_list:            
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
        # print(seed_tetra)
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
        # not_fronteir_index = 0
        ## for each face of tetra
        for i in range(0, 4):
            face_id = self.mesh.tetra_list[tetra].faces[i]
            tetra_neighs = self.mesh.tetra_list[tetra].neighs
            if face_id != -1:
                #si la cara es un frontier-face, entonces no se sigue la recursión
                if self.bitvector_frontier_faces[face_id] == True:
                    # print(i,tetra_neighs,self.mesh.tetra_list[tetra],'\n','fronteir', self.mesh.face_list[face_id])
                    
                    # if(face_id not in polyhedron and not((self.mesh.face_list[face_id].n1 in polyhedron_tetras) and (self.mesh.face_list[face_id].n2 in polyhedron_tetras))):
                    
                    # if(face_id in polyhedron):
                    #     polyhedron.remove(face_id)
                    #     # print('no saving', face_id)
                    # else:
                    polyhedron.append(face_id)
                    #     print('saving', face_id)
                    # print(self.mesh.face_list[face_id])
                    # print(polyhedron_tetras)
                else: #si es internal-face, se sigue la recursión por su tetra vecino
                    # print(i,tetra_neighs,self.mesh.tetra_list[tetra],'\n', self.mesh.face_list[face_id])
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
        #list of all reapeted faces
        barrierFaces = [k for k, v in Counter(terminalFace).items() if v > 1]
        #List of all edges of the barrier faces
        possibleTips = set()
        for face in barrierFaces:
            possibleTips.update(self.mesh.face_list[face].edges)
        possibleTips = list(possibleTips)
        for e in possibleTips:
            #List of all faces incident to e
            face_of_edge = self.mesh.edge_list[e].faces
            L1 = len(list(set(face_of_edge) & set(terminalFace)))
            L2 = len(terminalFace)
            if L2 - L1 == L2 - 1:
                barrierFacesTips.append(e)
        return barrierFacesTips


    def repairPhase(self, polyhedron, barrierFaceTips):
        # print('Repair Phase')
        tetra_list = []
        barrierFace = -1
        # print('repair phase:')
        for e in barrierFaceTips:
            #search polyhedron that contains the edge e
            for face in polyhedron:
                if e in self.mesh.face_list[face].edges:
                    barrierFace = face
                    # print('edge: ', self.mesh.edge_list[e], 'face: ', face)
                    break
            # select the middle face indicent to e
            faces_of_barrierFaceTip = self.mesh.edge_list[e].faces
            faces_of_barrierFaceTip.sort()
            # print('edge',self.mesh.edge_list[e].i, ':', faces_of_barrierFaceTip)
            
            n_internalFaces = len(faces_of_barrierFaceTip) - 1 
            #int adv = (internal_edges%2 == 0) ? internal_edges/2 - 1 : internal_edges/2 ;
            adv = floor(n_internalFaces/2) - 1 if n_internalFaces%2 == 0 else floor(n_internalFaces/2) 
            #because the first face is the barrierFace, advance to the next internal-face
            pos = faces_of_barrierFaceTip.index(barrierFace) + 1    
            middle_Face = faces_of_barrierFaceTip[((pos + adv)%n_internalFaces) ]
            #if there no advance, the middle face is the barrierFace and there is not repair
            if(middle_Face == barrierFace):
                sys.exit("middle_Face == faces_of_barrierFaceTip")
            # convert the middle internalface into a frontier-face
            self.bitvector_frontier_faces[middle_Face] = True

            #store adjacent tetrahedrons to the sub seed list
            tetra1 = self.mesh.face_list[barrierFace].n1
            tetra2 = self.mesh.face_list[barrierFace].n2
            tetra_list.append(tetra1)
            tetra_list.append(tetra2)

            #mark to be use in the bitvector_seed_tetra
            self.bivector_seed_tetra_in_repair[tetra1] = True
            self.bivector_seed_tetra_in_repair[tetra2] = True
        
        #while tetra_list is not empty
        while len(tetra_list) > 0:
            tetra_curr = tetra_list.pop()
            if self.bivector_seed_tetra_in_repair[tetra_curr] == True:
                self.bivector_seed_tetra_in_repair[tetra_curr] = False
                new_polyhedron = []
                new_polyhedron_tetras = []
                self.DepthFirstSearch_in_repair(new_polyhedron, new_polyhedron_tetras, tetra_curr)
                barrierFaces_new = self.count_barrierFaces(new_polyhedron)
                if barrierFaces_new > 0:
                    # print('re-repair')
                    for tetra in new_polyhedron_tetras:
                        self.visited_tetra[tetra] = False
                    ##generate a list with all the  barrier-face tips 
                    barrierFacesTips_new = self.detectBarrierFaceTips(new_polyhedron)       
                    ## Sent the polyhedron to repair
                    self.repairPhase(new_polyhedron, barrierFacesTips_new)
                else:
                    poly = Polyhedron()
                    poly.faces = new_polyhedron.copy()
                    # print(poly.faces)
                    poly.tetras = new_polyhedron_tetras.copy()
                    poly.was_repaired = True
                    self.polyhedral_mesh.append(poly)

    # return list of faces 
    def DepthFirstSearch_in_repair(self, polyhedron, polyhedron_tetras, tetra):
        self.visited_tetra[tetra] = True
        polyhedron_tetras.append(tetra)
        # tetra es remove as candidate for generation of poliedron
        self.bivector_seed_tetra_in_repair[tetra] = False 
        # not_fronteir_index = 0
        ## for each face of tetra
        for i in range(0, 4):
            face_id = self.mesh.tetra_list[tetra].faces[i]
            tetra_neighs = self.mesh.tetra_list[tetra].neighs
            if face_id != -1:
                #si la cara es un frontier-face, entonces no se sigue la recursión
                if self.bitvector_frontier_faces[face_id] == True:
                    polyhedron.append(face_id)
                else: #si es internal-face, se sigue la recursión por su tetra vecino
                    next_tetra = tetra_neighs[i]
                    # not_fronteir_index += 1
                    if(self.visited_tetra[next_tetra] == False):
                        self.DepthFirstSearch_in_repair(polyhedron, polyhedron_tetras, next_tetra)

############################################################################################################
# EXTRA
############################################################################################################

    def printOFF_faces(self, filename, faces):
            print("writing OFF file: "+ filename)
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

    def printOFF_polyhedralmesh_colors(self, filename):
        print("writing OFF file: "+ filename)
        list_face = []
        nodes = []
        colors = []
        for polyhedron in self.polyhedral_mesh:
            color = [random.random(),random.random(),random.random()]
            if(len(polyhedron.faces) == 4):
                for face in polyhedron.faces: 
                    list_face.append(face)
                    colors.append(color)
                # else:
                #     colors.append([0.8,0.8,0.8,0.5])
        #list_face =  list(dict.fromkeys(list_face))
        with open(filename, 'w') as fh:
            fh.write("OFF\n")
            fh.write("%d %d 0\n" % (self.mesh.n_nodes, len(list_face)))
            for v in self.mesh.node_list:
                fh.write("%f %f %f\n" % (v.x, v.y, v.z))
            # print(len(colors[0]), len(list_face))
            for f in list_face:
                v1 = self.mesh.face_list[f].v1
                v2 = self.mesh.face_list[f].v2
                v3 = self.mesh.face_list[f].v3
                fh.write("3 %d %d %d 3 .4 .5 .1\n" % (v1, v2, v3))#, colors[f][0],colors[f][1],colors[f][2]))

    def printOFF_polyhedralmesh(self, filename):
        print("writing OFF file: "+ filename)
        list_face = []
        for polyhedron in self.polyhedral_mesh:
            for face in polyhedron.faces:
                t = self.mesh.face_list[face].n1 if (self.mesh.face_list[face].n1 in polyhedron.tetras) else self.mesh.face_list[face].n2
                if not ccw_check(self.mesh.face_list[face], self.mesh.tetra_list[t],self.mesh.node_list):
                    # print('check face', face)
                    v2 = self.mesh.face_list[face].v2
                    v3 = self.mesh.face_list[face].v3
                    self.mesh.face_list[face].v2 = v3
                    self.mesh.face_list[face].v3 = v2
                list_face.append(face)
        list_face =  list(dict.fromkeys(list_face))
        with open(filename, 'w') as fh:
            fh.write("OFF\n")
            fh.write("%d %d 0\n" % (self.mesh.n_nodes, len(list_face)))
            for v in self.mesh.node_list:
                fh.write("%f %f %f\n" % (v.x, v.y, v.z))
            for f in list_face:

                v1 = self.mesh.face_list[f].v1
                v2 = self.mesh.face_list[f].v2
                v3 = self.mesh.face_list[f].v3

                fh.write("3 %d %d %d\n" % (v1, v2, v3))


    def printOFF_each_poly(self,filename):
        # print("writing OFF files: "+ filename)
        i = 0
        for polyhedron in self.polyhedral_mesh:
            list_face = polyhedron.faces
            nodes = []
            with open(filename+str(i)+'.off', 'w') as fh:
                fh.write("OFF\n")
                for tetra in polyhedron.tetras:
                    vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
                    for v in vertex:
                        if v not in nodes :
                            nodes.append(v) 
                fh.write("%d %d 0\n" % (len(nodes), len(list_face)))
                for node in nodes:
                    v = self.mesh.node_list[node]
                    fh.write("%f %f %f\n" % (v.x, v.y, v.z))
                for f in list_face:
                    t = self.mesh.face_list[f].n1 if (self.mesh.face_list[f].n1 in polyhedron.tetras) else self.mesh.face_list[f].n2
                    if ccw_check(self.mesh.face_list[f], self.mesh.tetra_list[t],self.mesh.node_list):
                        v1 = nodes.index(self.mesh.face_list[f].v1)
                        v2 = nodes.index(self.mesh.face_list[f].v2)
                        v3 = nodes.index(self.mesh.face_list[f].v3)
                    else:
                        v1 = nodes.index(self.mesh.face_list[f].v1)
                        v2 = nodes.index(self.mesh.face_list[f].v3)
                        v3 = nodes.index(self.mesh.face_list[f].v2)
                    fh.write("3 %d %d %d # %d\n" % (v1, v2, v3,f))
            i+=1

    def printOFF_one_poly(self,index,filename):
        # print("writing OFF files: "+ filename)
        polyhedron = self.polyhedral_mesh[index]
        list_face = polyhedron.faces
        nodes = []
        with open(filename+'.off', 'w') as fh:
            fh.write("OFF\n")
            for tetra in polyhedron.tetras:
                vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
                for v in vertex:
                    if v not in nodes :
                        nodes.append(v) 
            fh.write("%d %d 0\n" % (len(nodes), len(list_face)))
            for node in nodes:
                v = self.mesh.node_list[node]
                fh.write("%f %f %f\n" % (v.x, v.y, v.z))
            for f in list_face:
                t = self.mesh.face_list[f].n1 if (self.mesh.face_list[f].n1 in polyhedron.tetras) else self.mesh.face_list[f].n2
                if ccw_check(self.mesh.face_list[f], self.mesh.tetra_list[t],self.mesh.node_list):
                    v1 = nodes.index(self.mesh.face_list[f].v1)
                    v2 = nodes.index(self.mesh.face_list[f].v2)
                    v3 = nodes.index(self.mesh.face_list[f].v3)
                else:
                    v1 = nodes.index(self.mesh.face_list[f].v1)
                    v2 = nodes.index(self.mesh.face_list[f].v3)
                    v3 = nodes.index(self.mesh.face_list[f].v2)
                fh.write("3 %d %d %d # %d\n" % (v1, v2, v3,f))


    def writePolygonFile(self,filename):
        # print("writing OFF files: "+ filename)
        with open(filename+'.txt', 'w') as fh:
            polys = self.polyhedral_mesh
            
            c = 0
            not_convex_poly = []
            for poly in polys:
                if not poly.is_convex:
                    not_convex_poly.append(poly)
            p = len(not_convex_poly)
            fh.write(str(p)+'\n')
            for polyhedron in not_convex_poly:
                # print(str(polyhedron))
                list_face = polyhedron.faces
                nodes = []
                for tetra in polyhedron.tetras:
                    vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
                    for v in vertex:
                        if v not in nodes :
                            nodes.append(v) 
                # if not polyhedron.is_convex:
                fh.write("%d %d\n" % (len(nodes), len(list_face)))
                for node in nodes:
                    v = self.mesh.node_list[node]
                    fh.write("%f %f %f\n" % (v.x, v.y, v.z))
                
                for f in list_face:
                    # print(list_face)
                    t = self.mesh.face_list[f].n1 if (self.mesh.face_list[f].n1 in polyhedron.tetras) else self.mesh.face_list[f].n2
                    if ccw_check(self.mesh.face_list[f], self.mesh.tetra_list[t],self.mesh.node_list):
                        v1 = nodes.index(self.mesh.face_list[f].v1)
                        v2 = nodes.index(self.mesh.face_list[f].v2)
                        v3 = nodes.index(self.mesh.face_list[f].v3)
                    else:
                        v1 = nodes.index(self.mesh.face_list[f].v1)
                        v2 = nodes.index(self.mesh.face_list[f].v3)
                        v3 = nodes.index(self.mesh.face_list[f].v2)
                    fh.write("3 %d %d %d \n" % (v1, v2, v3))# %d %d
                # else:
                #     print('si convex')
                c+=1


    def get_info(self):
        print("PolyllaFace info:")
        print("Number of polyhedrons: " + str(len(self.polyhedral_mesh)))
        print("Number of barrier faces: " + str(self.n_barrier_faces))
        print("Number of polyhedra with barrier faces: " + str(self.polyhedra_with_barriers))
        count = 0
        for polyhedron in self.polyhedral_mesh:
            if len(polyhedron.tetras) == 1:
                count += 1
        print("Number of polyhedrons that are tetrahedrons: " + str(count))
        return len(self.polyhedral_mesh), self.n_barrier_faces, self.polyhedra_with_barriers, count

#############################################################################################
#POLYHEDRA METRICS
#############################################################################################
    def edge_length(self, edge):
        v1 = self.mesh.node_list[edge.v1]
        v2 = self.mesh.node_list[edge.v2]
        distance = (v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2 #without sqrt for performance
        edge.length = distance
    
    def edge_ratio(self):
        polyhedrons = self.polyhedral_mesh
        ratios = []
        # if self.mesh.edge_list[0].length < 0:
        #     self.calculate_edges_length()
        for poly in polyhedrons:
            # print(poly)
            faces = poly.faces
            # face_mins = []
            # face_maxs = []
            edges = []
            for face in faces:
                # edges = []
                for edge in self.mesh.face_list[face].edges:
                    self.edge_length(self.mesh.edge_list[edge])
                    edges.append(self.mesh.edge_list[edge].length)
                # edge_min = min(edges)
                # edge_max = max(edges)
                # face_mins.append(edge_min)
                # face_maxs.append(edge_max)
            poly_min = min(edges)
            poly_max = max(edges)
            ratio = poly_min/poly_max
            ratios.append(ratio)
            # print(poly_min,poly_max)
        mean_ratio = statistics.mean(ratios)
        median_ratio = statistics.median(ratios)
        variance_ratio = statistics.variance(ratios)
        min_ratio = min(ratios)
        max_ratio = max(ratios)

        return [mean_ratio, min_ratio, max_ratio,median_ratio,variance_ratio]
    
    def tetra_per_poly(self):
        polyhedrons = self.polyhedral_mesh
        tetras = []
        for poly in polyhedrons:
            tetra_num = len(poly.tetras)
            tetras.append(tetra_num)
        
        mean_tetra_num = statistics.mean(tetras)
        median_tetra_num = statistics.median(tetras)
        variance_tetra_num = statistics.variance(tetras)
        min_tetra_num = min(tetras)
        max_tetra_num = max(tetras)
        i = tetras.index(max_tetra_num)
        self.printOFF_one_poly(i,'BiggestPoly/'+str(self.mesh.n_nodes)+self.flag+'.off')

        return [mean_tetra_num, min_tetra_num, max_tetra_num,median_tetra_num,variance_tetra_num]
    
    def faces_per_poly(self):
        polyhedrons = self.polyhedral_mesh
        faces_num = []
        for poly in polyhedrons:
            face_num = len(poly.faces)
            faces_num.append(face_num)
        
        mean_face_num = statistics.mean(faces_num)
        median_face_num = statistics.median(faces_num)
        variance_face_num = statistics.variance(faces_num)
        min_face_num = min(faces_num)
        max_face_num = max(faces_num)

        return [mean_face_num, min_face_num, max_face_num,median_face_num,variance_face_num]
    
    def convex_polyhedrons(self):
        conv_polys = 0
        for polyhedron in self.polyhedral_mesh:
            nodes = []
            for tetra in polyhedron.tetras:
                    vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
                    for v in vertex:
                        if v not in nodes :
                            nodes.append(v)
            for i in range(len(nodes)):
                v = np.array([self.mesh.node_list[nodes[i]].x,self.mesh.node_list[nodes[i]].y,self.mesh.node_list[nodes[i]].z])
                nodes[i] = v
            nodes = np.array(nodes)
            cvhull = ConvexHull(nodes)
            if set(cvhull.vertices) == set(range(len(nodes))):
                conv_polys+=1
                polyhedron.is_convex = True

        return conv_polys/len(self.polyhedral_mesh)
    
    def polyhedron_area(self):
        ratios = []
        if self.mesh.face_list[0].area < 0:
            self.calculate_area_triangle_3d()
        for polyhedron in self.polyhedral_mesh:
            suma_area = 0
            nodes = []
            for face in polyhedron.faces:
                # print(self.mesh.face_list[face].i, self.mesh.face_list[face].area)
                suma_area+= self.mesh.face_list[face].area
            for tetra in polyhedron.tetras:
                    vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
                    for v in vertex:
                        if v not in nodes :
                            nodes.append(v)
            for i in range(len(nodes)):
                v = np.array([self.mesh.node_list[nodes[i]].x,self.mesh.node_list[nodes[i]].y,self.mesh.node_list[nodes[i]].z])
                nodes[i] = v
            nodes = np.array(nodes)
            cvhull = ConvexHull(nodes)
            cvHull_area = cvhull.area
            ratio = suma_area / cvHull_area
            ratios.append(ratio)
        mean_ratio_area = statistics.mean(ratios)
        median_ratio_area = statistics.median(ratios)
        variance_ratio_area = statistics.variance(ratios)
        min_ratio_area = min(ratios)
        max_ratio_area = max(ratios)

        return [mean_ratio_area, min_ratio_area, max_ratio_area,median_ratio_area,variance_ratio_area]
    
    def tetra_volume(self, tetra):
        t = self.mesh.tetra_list[tetra]
        v1 = self.mesh.node_list[t.v1]
        v2 = self.mesh.node_list[t.v2]
        v3 = self.mesh.node_list[t.v3]
        v4 = self.mesh.node_list[t.v4]
        A = np.array([v2.x - v1.x,v2.y - v1.y,v2.z - v1.z])
        B = np.array([v3.x - v1.x,v3.y - v1.y,v3.z - v1.z])
        C = np.array([v4.x - v1.x,v4.y - v1.y,v4.z - v1.z])

        # vec3d L0 = p1 - p0;
        # vec3d L2 = p0 - p2;
        # vec3d L3 = p3 - p0;

        # return (L2.cross(L0)).dot(L3) / 6.0;
        return np.dot(A,np.cross(B,C))/6.0
        

    def polyhedron_volume(self):
        volumes = []
        for poly in self.polyhedral_mesh:
            volume = 0
            for tetra in poly.tetras:
                volume += self.tetra_volume(tetra)
            volumes.append(volume)
        mean_volume = statistics.mean(volumes)
        min_volume = min(volumes)
        max_volume = max(volumes)

        return [mean_volume, min_volume, max_volume]
    
    def volume_ratio(self, kernelfile):
        kfile = open(kernelfile+'.txt','r')
        filelines = kfile.readlines()
        polys_w_kernel = int(filelines.pop().split(' ')[0])
        kernel_volumes = list(map(float, filelines))
        # for line in filelines:
        #     kernel_volumes.append(float(line))
        ratios = []
        convex_poly = []
        # for poly in self.polyhedral_mesh:
        #     if poly.is_convex:
        #         convex_poly.append(poly)
        not_convexs = 0
        for i in range(len(self.polyhedral_mesh)):
            poly = self.polyhedral_mesh[i]
            volume = 0
            for tetra in poly.tetras:
                volume += self.tetra_volume(tetra)
            if not poly.is_convex:
                if kernel_volumes[not_convexs] > 0:
                    ratio = kernel_volumes[not_convexs] / volume
                    ratios.append(ratio)
                not_convexs+=1
            else:
                ratio = 1
                ratios.append(ratio)
                # print(volume,kernel_volumes[i],ratio)
        mean_volume = statistics.mean(ratios)
        median_volume= statistics.median(ratios)
        variance_volume = statistics.variance(ratios)
        min_volume = min(ratios)
        max_volume = max(ratios)
        convex_num = len(self.polyhedral_mesh) - not_convexs
        kernel_rate = ((polys_w_kernel+convex_num)/len(self.polyhedral_mesh))*100
        
        return [mean_volume, min_volume, max_volume, kernel_rate,median_volume,variance_volume]
    
    def original_mesh_edge_ratio(self):
        self.calculate_edges_length()
        ratios = []
        for tetra in self.mesh.tetra_list:
            edges = []
            for face in tetra.faces:
                for edge in self.mesh.face_list[face].edges:
                    edges.append(self.mesh.edge_list[edge].length)
            ratio = min(edges)/max(edges)
            ratios.append(ratio)
        mean_edge_ratio = statistics.mean(ratios)
        min_edge_ratio = min(ratios)
        max_edge_ratio = max(ratios)
        return [mean_edge_ratio, min_edge_ratio, max_edge_ratio]

        

        



if __name__ == "__main__":
    folder = "data\\"
    #file = "3D_100.1"
    file = "socket.1"
    file = "1000points.1"
    filename = folder + file 
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"
    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = FaceTetrahedronMesh(node_file, face_file, ele_file)
    polylla_mesh = PolyllaFace(mesh)

    
    #polylla_mesh.printOFF_polyhedralmesh(filename + "_polyhedral_mesh.off")
    #polylla_mesh.printOFF_faces(filename + "_frontier_faces.off", sorted(set([num for sublist in polylla_mesh.polyhedral_mesh for num in sublist])))
    #for i in range(0, len(polylla_mesh.polyhedral_mesh)):
    #    #print(polylla_mesh.polyhedral_mesh[i])
    #    polylla_mesh.printOFF_faces(folder + file + "_PolyllaFACE_polyhedron_" + str(i) + ".off", polylla_mesh.polyhedral_mesh[i])
    

    polylla_mesh.get_info()
