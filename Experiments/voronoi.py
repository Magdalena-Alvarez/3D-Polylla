import pyvoro
import random
import numpy as np
import time
from math import sqrt
from statistics import mean
from scipy.stats import qmc
from scipy.spatial import ConvexHull


def generate_voronoi_random(numVertices):
    points = np.random.rand(numVertices,3)

# Ajustar los límites para el cubo de 1000x1000x1000
    limits = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]

    # Se puede ajustar el tamaño del bloque según sea necesario
    block_size = 1.0 # Este valor puede variar según tus necesidades

    # Calcular el diagrama de Voronoi
    t0 = time.time()
    voronoi_result = pyvoro.compute_voronoi(points, limits, block_size)
    tf = time.time()
    dtV = (tf-t0)
    print('voronoi time = ', dtV)
    vertexs = []
    polyhedrons = []
    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    minz = 0
    maxz = 0
    for cell in voronoi_result:
        vertexs+=cell['vertices']
        vertices = np.array(cell['vertices'])  # Convierte a array de NumPy para facilitar el manejo
        faces = cell['faces']
        cell_faces = []
        minx = min(minx,vertices[:, 0].min())
        miny = min(miny,vertices[:, 1].min())
        minz = min(minz,vertices[:, 2].min())

        maxx = max(maxx,vertices[:, 0].max())
        maxy = max(maxy,vertices[:, 1].max())
        maxz = max(maxz,vertices[:, 2].max())
        
        for face in faces:
            cell_faces.append(face['vertices'])

        polyhedrons.append([cell['vertices'],cell_faces, cell['volume']])

    # print(minx,maxx,miny,maxy,minz ,maxz)
    return polyhedrons , dtV


def generate_voronoi_poisson(radius):

    rng = np.random.default_rng()
    engine = qmc.PoissonDisk(d=3, radius=radius, seed=rng)
    points = engine.fill_space()

# Ajustar los límites para el cubo de 1000x1000x1000
    limits = [[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]]

    # Se puede ajustar el tamaño del bloque según sea necesario
    block_size = 1.0 # Este valor puede variar según tus necesidades

    # Calcular el diagrama de Voronoi
    t0 = time.time()
    voronoi_result = pyvoro.compute_voronoi(points, limits, block_size)
    tf = time.time()
    dtV = (tf-t0)
    print('voronoi time = ', dtV)
    vertexs = []
    polyhedrons = []
    minx = 0
    maxx = 0
    miny = 0
    maxy = 0
    minz = 0
    maxz = 0
    for cell in voronoi_result:
        vertexs+=cell['vertices']
        vertices = np.array(cell['vertices'])  # Convierte a array de NumPy para facilitar el manejo
        faces = cell['faces']
        cell_faces = []
        minx = min(minx,vertices[:, 0].min())
        miny = min(miny,vertices[:, 1].min())
        minz = min(minz,vertices[:, 2].min())

        maxx = max(maxx,vertices[:, 0].max())
        maxy = max(maxy,vertices[:, 1].max())
        maxz = max(maxz,vertices[:, 2].max())
        
        for face in faces:
            cell_faces.append(face['vertices'])

        polyhedrons.append([cell['vertices'],cell_faces, cell['volume']])

    # print(minx,maxx,miny,maxy,minz ,maxz)
    return polyhedrons , dtV



def edges(polyhedron):
    edge_list=[]
    for face in polyhedron[1]:
        for i in range(len(face)):
            ei = [face[i%len(face)],face[(i+1)%len(face)]]
            ei.sort()
            if ei not in edge_list:
                edge_list.append(ei)

    return edge_list

def edges_length_ratio(polyhedron):
    length_list=[]
    for face in polyhedron[1]:
        for i in range(len(face)):
            ei = [face[i%len(face)],face[(i+1)%len(face)]]
            ei.sort()
            if ei not in length_list:
                v1 = polyhedron[0][ei[0]]
                v2 = polyhedron[0][ei[1]]
                l = sqrt(((v2[0]-v1[0])**2 + (v2[1]-v1[1])**2 + (v2[2]-v1[2])**2))
                length_list.append(l)

    shortest = min(length_list)
    longest = max(length_list)
    return shortest/longest

def n_faces(polyhedron):
    return len(polyhedron[1])

# area:
def face_area(face_vertex):
    area = [0,0,0]
    v0 = face_vertex[0]
    for i in range(1,len(face_vertex)-1):
        v1 = face_vertex[i]
        v2 = face_vertex[i+1]
        A = np.array([v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]])
        B = np.array([v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]])
        local_area = np.cross(A,B)
        area[0]+= local_area[0]
        area[1]+= local_area[1]
        area[2]+= local_area[2]
    return 0.5 * sqrt((area[0]**2 + area[1]**2) + area[2]**2)


def polyhedron_area_ratio(polyhedron):
    area = 0
    nodes = np.array(polyhedron[0])
    for face in polyhedron[1]:
        face_vertex = nodes[face]
        area += face_area(face_vertex)
    cvhull = ConvexHull(nodes)
    cvHull_area = cvhull.area
    ratio = area / cvHull_area
    return ratio

def is_convex(polyhedron):
    nodes = polyhedron[0]
    cvhull = ConvexHull(nodes)
    return set(cvhull.vertices) == set(range(len(nodes)))

def analize_voronoi(voro_polys):
    polyhedrons, dtV = voro_polys

    edge_ratios = []
    n_faces_list = []
    areas = []
    volumen = []
    convexs_polys = 0
    for polyhedron in polyhedrons:
        # print('vertices: ', polyhedron[0])
        # print('faces:', polyhedron[1])
        # print(edges(polyhedron))
        edge_ratio = edges_length_ratio(polyhedron)
        edge_ratios.append(edge_ratio)
        n_face = n_faces(polyhedron)
        n_faces_list.append(n_face)
        area = polyhedron_area_ratio(polyhedron)
        areas.append(area)
        volumen.append(polyhedron[2])
        if is_convex(polyhedron):
            convexs_polys+=1
    print('Cantidad de Poliedros; ', len(polyhedrons))
    print('Cantidad de Poliedros convexos; ', convexs_polys)
    print('Promedio Edge ratio: ', mean(edge_ratios))
    print('Minimum Edge ratio: ', min(edge_ratios))
    print('Maximum Edge ratio: ', max(edge_ratios))

    print('Promedio Numero de Caras: ', mean(n_faces_list))
    print('Minimum Numero de Caras: ', min(n_faces_list))
    print('Maximum Numero de Caras: ', max(n_faces_list))

    print('Promedio Area Ratio: ', mean(areas))
    print('Minimum Area Ratio: ', min(areas))
    print('Maximum Area Ratio: ', max(areas))

    print('Promedio Volume: ', mean(volumen))
    print('Minimum Volume: ', min(volumen))
    print('Maximum Volume: ', max(volumen))

    convex_rate = convexs_polys/len(polyhedrons)
    edge_ratio = [mean(edge_ratios),min(edge_ratios),max(edge_ratios)]
    faces_per_poly = [mean(n_faces_list),min(n_faces_list),max(n_faces_list)]
    polyhedron_volume_ratio = [1.0,1.0,1.0]
    polyarea_ratio = [1.0,1.0,1.0]
    return [dtV, convex_rate, edge_ratio,faces_per_poly,polyhedron_volume_ratio,polyarea_ratio]