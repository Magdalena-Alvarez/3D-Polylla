import sys
arguments = sys.argv

vertexs = arguments[1]
faces = arguments[2]

class Vertex:
    def __init__(self, i, x, y, z):
        self.i = i  
        self.x = x
        self.y = y
        self.z = z

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
a = []
vertex = [(0,0,1,2), (1,0,2,3),(2,4,5,6),(3,4,6,7),(4,4,1,0),(5,4,5,1),(6,5,6,2),(7,5,2,1),(8,6,7,3),(9,6,3,2),(10,7,4,0),(11,7,0,3)]
edges = []
vertex_list = []
face_list = []
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
		edges.append(edge)
		
		for f in faces:
			face = face_list[f]
			face.edges.append(ei)
		ei += 1

#print(edges)
#print(face_list)
