a = [[],[],[],[],[],[],[],[]]
vertex = [(0,1,2), (0,2,3),(4,5,6),(4,6,7),(4,1,0),(4,5,1),(5,6,2),(5,2,1),(6,7,3),(6,3,2),(7,4,0),(7,0,3)]
edges = []
for i in range(len(vertex)):
	v1 = vertex[i][0]
	v2 = vertex[i][1]
	v3 = vertex[i][2]
	if v2 not in a[v1] and v1 not in a[v2]:
		a[v1].append(v2)
	if v3 not in a[v2] and v2 not in a[v3]:
		a[v2].append(v3)
	if v1 not in a[v3] and v3 not in a[v1]:
		a[v3].append(v1)
for i in range(len(a)):
	for v in a[i]:
		edges.append((i,v))
print(edges)

print(a)