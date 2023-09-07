import sys
arguments = sys.argv

vertexs = arguments[1]
faces = arguments[2]
tetras = arguments[3]

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
        self.edges = [] #tetra case 3, poly case at least 3

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Face " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Edges: " + str(self.edges) + " Neighs: " + str(self.neighs) + ")\n"
class Edge:
    def __init__(self, i, end_point1, end_point2) -> None:
        self.i = i
        self.v1 = end_point1
        self.v2 = end_point2
        self.vertex = [end_point1,end_point2]
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
        self.vertex = [v1,v2,v3,v4]
        self.neighs = [] #4 neighs
        self.is_boundary = False #if len(neighs) > 4 True
        self.faces = []
        self.edges = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "(Tetra " + str(self.i) + " Vertex 1: " + str(self.v1) + " Vertex 2: " + str(self.v2)  + " Vertex 3: " + str(self.v3) + " Vertex 4: " + str(self.v4) + " Neighs" + str(self.neighs) +")\n"
    

def look_for_faces(v1, v2, v3, v4, tetra, face_list):
      faces = []
      edges = []
      c = 0
      for face in face_list:
            if c >= 4:
                  break
            if (v1 in face.vertex) and (v2 in face.vertex) and (v3 in face.vertex):
                  faces.append(face.i)
                  face.neighs.append(tetra.i)
                  edges += face.edges
                  c += 1
            if (v2 in face.vertex) and (v3 in face.vertex) and (v4 in face.vertex):
                  faces.append(face.i)
                  face.neighs.append(tetra.i)
                  edges += face.edges
                  c += 1
            if (v3 in face.vertex) and (v4 in face.vertex) and (v1 in face.vertex):
                  faces.append(face.i)
                  face.neighs.append(tetra.i)
                  edges += face.edges
                  c += 1
            if (v4 in face.vertex) and (v2 in face.vertex) and (v1 in face.vertex):
                  faces.append(face.i)
                  face.neighs.append(tetra.i)
                  edges += face.edges
                  c += 1
      tetra.edge = list(set(edges))
      return faces

def saveLog(filename, info_list):
      f = open(filename,'w')
      for i in info_list:
            f.write(str(i))


a = []
vertex_list = []
edge_list = []
face_list = []
tetra_list = []
print("Reading vertex file")
filev = open(vertexs, 'r')

for line in filev:
	l = line.split()
	v = Vertex(l[0], l[1], l[2], l[3])
	vertex_list.append(v)
	a.append([[],[]]) 
        
print("Reading face file")
filef = open(faces, 'r')
#fi = 0
for line in filef:
	l = line.split()
	if l[0] == '#' or len(l) < 4:
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


	if v2 not in a[v1][0] and v1 not in a[v2][0]:
		a[v1][0].append(v2)
		a[v1][1].append([fi])
		savedE1 = True

	if v3 not in a[v2][0] and v2 not in a[v3][0]:
		a[v2][0].append(v3)
		a[v2][1].append([fi])
		savedE2 = True
	if v1 not in a[v3][0] and v3 not in a[v1][0]:
		a[v3][0].append(v1)
		a[v3][1].append([fi])
		savedE3 = True

	#if it isn't saved it already exist (only two optinos)
	if not savedE1:
		if v2 in a[v1][0]:
			index = a[v1][0].index(v2)
			a[v1][1][index].append(fi)
		else:
			index = a[v2][0].index(v1)
			a[v2][1][index].append(fi)

	if not savedE2:
		if v3 in a[v2][0]:
			index = a[v2][0].index(v3)
			a[v2][1][index].append(fi)
		else:
			index = a[v3][0].index(v2)
			a[v3][1][index].append(fi)
	if not savedE3:
		if v1 in a[v3][0]:
			index = a[v3][0].index(v1)
			a[v3][1][index].append(fi)
		else:
			index = a[v1][0].index(v3)
			a[v1][1][index].append(fi)
	#fi +=1
ei = 0
print("Processing edges ")
for vi in range(len(a)):
	for i in range(len(a[vi][0])):
		vf = a[vi][0][i]
		faces = a[vi][1][i]
		edge = Edge(ei,vi,vf)
		edge.faces = faces
		edge_list.append(edge)
		
		for f in faces:
			face = face_list[f]
			face.edges.append(ei)
		ei += 1

#print(edges)
print(face_list)

print("Reading tetrahedron file")
filet = open(tetras, 'r')
#fi = 0

for line in filet:
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

    t.faces = look_for_faces(v1,v2,v3,v4,t,face_list)

    savedF1 = False
    savedF2 = False
    savedF3 = False
    savedF4 = False
#print(tetra_list)
saveLog("logTetra.txt", tetra_list)
saveLog("logFace.txt", face_list)