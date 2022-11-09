import point_cloud_utils as pcu

# v is a nv by 3 NumPy array of vertices
# f is an nf by 3 NumPy array of face indexes into v
# n is a nv by 3 NumPy array of vertex normals
v, f, n = pcu.load_mesh_vfn("box.off")

# Generate 10000 samples on a mesh with poisson disk samples
# f_i are the face indices of each sample and bc are barycentric coordinates of the sample within a face
f_i, bc = pcu.sample_mesh_poisson_disk(v, f, n, 10000)

# Use the face indices and barycentric coordinate to compute sample positions and normals
v_poisson = pcu.interpolate_barycentric_coords(f, f_i, bc, v)
n_poisson = pcu.interpolate_barycentric_coords(f, f_i, bc, n)