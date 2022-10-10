from mesh import TetrahedronMesh
import numpy as np
import sys
from collections import Counter


class PolyllaFace:
    def __init__(self, mesh):
        self.mesh = mesh
        
        self.longest_faces = self.calculate_max_faces()
        self.seed_tetra = self.calculate_seed_tetrahedrons()
        self.bitvector_frontier_edges = self.calculate_frontier_faces()

        self.visited_tetra = [False] * mesh.n_tetrahedrons
        self.polyhedron_mesh = []        
        for terminal_tetra in self.seed_tetra:
            polyhedron = []
            self.DepthFirstSearch(polyhedron, terminal_tetra)
            self.polyhedron_mesh.append(polyhedron)

        

    def calculate_area_triangle_3d(self, v1, v2, v3):
        av1 = np.array([v1.x, v1.y, v1.z])
        av2 = np.array([v2.x, v2.y, v2.z])
        av3 = np.array([v3.x, v3.y, v3.z])
        a = np.linalg.norm(np.cross(av2-av1, av3-av1))
        return a

    def calculate_max_faces(self):
        longest = []
        for tetra in self.mesh.tetra_list:
            # Calcula el area de cada cara
            f1 = mesh.face_list[tetra.faces[0]]
            f2 = mesh.face_list[tetra.faces[1]]
            f3 = mesh.face_list[tetra.faces[2]]
            f4 = mesh.face_list[tetra.faces[3]]


            a0 = self.calculate_area_triangle_3d(self.mesh.node_list[f1.v1], self.mesh.node_list[f1.v2], self.mesh.node_list[f1.v3])
            a1 = self.calculate_area_triangle_3d(self.mesh.node_list[f2.v1], self.mesh.node_list[f2.v2], self.mesh.node_list[f2.v3])
            a2 = self.calculate_area_triangle_3d(self.mesh.node_list[f3.v1], self.mesh.node_list[f3.v2], self.mesh.node_list[f3.v3])
            a3 = self.calculate_area_triangle_3d(self.mesh.node_list[f4.v1], self.mesh.node_list[f4.v2], self.mesh.node_list[f4.v3])

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
                longest_face_n1 = mesh.tetra_list[n1].faces[self.longest_faces[n1]]
                longest_face_n2 = mesh.tetra_list[n2].faces[self.longest_faces[n2]]
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
                longest_face_n1 = mesh.tetra_list[n1].faces[self.longest_faces[n1]]
                longest_face_n2 = mesh.tetra_list[n2].faces[self.longest_faces[n2]]

                # Si no es la cara más larga de ningún tetra de n1 o n2, es una frontier-edge
                frontier_faces.append(f != longest_face_n1 and f != longest_face_n2)
            
        return frontier_faces

    def DepthFirstSearch(self, polyhedron, tetra):
        self.visited_tetra[tetra] = True
        ## for each face of tetra
        for i in range(0, 4):
            face_id = self.mesh.tetra_list[tetra].faces[i]
            tetra_neighs = self.mesh.tetra_list[tetra].neighs
            print(tetra_neighs)
            if face_id != -1:
                if self.bitvector_frontier_edges[face_id] == True:
                    polyhedron.append(face_id)
                else:
                    next_tetra = tetra_neighs[i]
                    if(self.visited_tetra[next_tetra] == False):
                        self.DepthFirstSearch(polyhedron, next_tetra)
        


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

if __name__ == "__main__":
    folder = "data\\"
    filename = folder + "3D_100.1"
    node_file = filename + ".node"
    ele_file = filename + ".ele"
    face_file = filename + ".face"
    edge_file = filename + ".edge"
    print("reading files" + node_file + edge_file + face_file + edge_file)
    mesh = TetrahedronMesh(node_file, face_file, ele_file, edge_file)
    polylla_mesh = PolyllaFace(mesh)
    for i in range(0, len(polylla_mesh.polyhedron_mesh)):
        print(polylla_mesh.polyhedron_mesh[i])
        polylla_mesh.printOFF_faces(folder + "polyhedron_" + str(i) + ".off", polylla_mesh.polyhedron_mesh[i])
    
    #polylla_mesh.printOFF_polyhedralmesh(filename + "_polyhedron_mesh.off")
    #polylla_mesh.printOFF_faces(filename + "_frontier_faces.off", sorted(set([num for sublist in polylla_mesh.polyhedron_mesh for num in sublist])))

    print(polylla_mesh.polyhedron_mesh)
    ## detect repeated face in polyhgons from polyhedron_mesh
    repeated_faces = []
    for i in range(0, len(polylla_mesh.polyhedron_mesh)):
            print("polyhedron: " + str(i) + " " + str(polylla_mesh.polyhedron_mesh[i]))
            print([k for k,v in Counter(polylla_mesh.polyhedron_mesh[i]).items() if v>1])
    