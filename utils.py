
def ccw_check(face,tetra,node_list):
    
    a = node_list[tetra.v1]
    b = node_list[tetra.v2]
    c = node_list[tetra.v3]
    d = node_list[tetra.v4]

    
    center = [(a.x+b.x+c.x+d.x)/4, (a.y+b.y+c.y+d.y)/4,(a.z+b.z+c.z+d.z)/4]
    
    A = node_list[face.v1]
    B = node_list[face.v2]
    C = node_list[face.v3]

    cruz_prod = [(B.y-A.y)*(C.z-A.z) - (B.z - A.z)*(C.y-A.y),
            (B.z-A.z)*(C.x-A.x) - (C.z-A.z)*(B.x-A.x),
            (B.x-A.x)*(C.y-A.y) - (B.y-A.y)*(C.x-A.x)]
    
    ref_vec = [A.x - center[0], 
               A.y - center[1], 
               A.z - center[2]]

    dot_product = cruz_prod[0]*ref_vec[0] + \
                    cruz_prod[1]*ref_vec[1] + \
                    cruz_prod[2]*ref_vec[2]


    return dot_product > 0

import numpy as np

# Función para calcular el vector normal de una cara del poliedro
def calculate_face_normal(face):
    # Seleccionar tres puntos de la cara para calcular el vector normal
    p1, p2, p3 = face[:3]
    # Calcular los vectores que representan dos aristas de la cara
    edge1 = p2 - p1
    edge2 = p3 - p1
    # Calcular el producto cruz entre los vectores para obtener el vector normal
    normal = np.cross(edge1, edge2)
    # Normalizar el vector para obtener una dirección consistente
    normal /= np.linalg.norm(normal)
    return normal

# Función para verificar si un poliedro es convexo
def is_polyhedron_convex(points, faces):
    # Calcular el vector normal de cada cara
    points = np.array(points)
    faces = np.array(faces)
#     print(points, faces)
    face_normals = np.array([calculate_face_normal(points[face]) for face in faces])
    # Verificar si todos los vectores normales apuntan en la misma dirección (todos positivos o todos negativos)
    if np.all(np.dot(face_normals, face_normals[0]) > 0):
        return True  # El poliedro es convexo
    else:
        return False  # El poliedro no es convexo

# Ejemplo de puntos y caras de un poliedro
# def convex_polyhedrons(self):
#         conv_polys = 0
#         for polyhedron in self.polyhedral_mesh:
#             nodes_index = []
#             nodes = []
#             for tetra in polyhedron.tetras:
#                     vertex = [self.mesh.tetra_list[tetra].v1, self.mesh.tetra_list[tetra].v2,self.mesh.tetra_list[tetra].v3,self.mesh.tetra_list[tetra].v4]
#                     for v in vertex:
#                         if v not in nodes_index :
#                             nodes_index.append(v)
#             for i in range(len(nodes_index)):
#                 v = np.array([self.mesh.node_list[nodes_index[i]].x,self.mesh.node_list[nodes_index[i]].y,self.mesh.node_list[nodes_index[i]].z])
#                 nodes.append(v)
#             # nodes = np.array(nodes)
#             faces = []
#             # print(nodes)
#             for f in polyhedron.faces:
#                 t = self.mesh.face_list[f].neighs[0] if (self.mesh.face_list[f].neighs[0] in polyhedron.tetras) else self.mesh.face_list[f].neighs[1]
#                 if ccw_check(self.mesh.face_list[f], self.mesh.tetra_list[t],self.mesh.node_list):
#                     # print(self.mesh.face_list[f])
#                     v1 = nodes_index.index(self.mesh.face_list[f].v1)
#                     v2 = nodes_index.index(self.mesh.face_list[f].v2)
#                     v3 = nodes_index.index(self.mesh.face_list[f].v3)
#                 else:
#                     v1 = nodes_index.index(self.mesh.face_list[f].v1)
#                     v2 = nodes_index.index(self.mesh.face_list[f].v3)
#                     v3 = nodes_index.index(self.mesh.face_list[f].v2)
#                 face = np.array([v1,v2,v3])
#                 faces.append(face)
                
#             if is_polyhedron_convex(nodes,faces):
#                 conv_polys+= 1
#                 polyhedron.is_convex = True
#             # cvhull = ConvexHull(nodes)
#             # # cvHull_area = cvhull.area
#             # if set(cvhull.vertices) == set(range(len(nodes))):
#             #     conv_polys+=1
#             #     polyhedron.is_convex = True

#         return conv_polys/len(self.polyhedral_mesh)