
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
        self.edges = [] #tetra case 3, poly case at least 3

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Edges: " + str(self.edges) + ")\n"
class Edge:
    def __init__(self, i, end_point1, end_point2) -> None:
        self.i = i
        self.v1 = end_point1
        self.v2 = end_point2
        self.faces = [] # boundary case 2, internal case at least 3

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Edge " + str(self.i) + " Vertex i: " + str(self.v1) + " Vertex f: " + str(self.v2) + " Faces: " + str(self.faces) + ")\n"

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