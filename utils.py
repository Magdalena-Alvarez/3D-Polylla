
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
     
import vtk
def vtk_to_obj(filename):
       
# Load VTK file
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(filename+".vtk")
        reader.Update()

# Get points and cells from VTK dataset
        points = reader.GetOutput().GetPoints()
        cells = reader.GetOutput().GetCells()

# Convert VTK points to NumPy array
        points_array = [points.GetPoint(i) for i in range(points.GetNumberOfPoints())]

# Write OBJ file
        with open(filename+".obj", "w") as obj_file:
    # Write vertices
                for point in points_array:
                        obj_file.write(f"v {point[0]} {point[1]} {point[2]}\n")

    # Write faces
                cells.InitTraversal()
                while True:
                        cell = vtk.vtkIdList()
                        if cells.GetNextCell(cell):
                                cell_size = cell.GetNumberOfIds()
                                obj_file.write(f"f {' '.join([str(cell.GetId(i) + 1) for i in range(cell_size)])}\n")
                        else:
                                break
