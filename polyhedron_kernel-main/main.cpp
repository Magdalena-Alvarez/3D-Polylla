#include "polyhedron_kernel.h"
#include <chrono>
#include <cinolib/meshes/meshes.h>

using namespace cinolib;


std::vector<std::pair<std::vector<vec3d>, std::vector<std::vector<uint>>>> readFile(std::string filename){
    
    std::ifstream inputFile(filename);

    // Check if the file is open
    if (!inputFile.is_open()) {
        std::cerr << "Error opening the file: " << filename << std::endl;
    }
    std::vector<std::pair<std::vector<vec3d>,std::vector<std::vector<uint>>>> polyhedron_list;
    

    // Read the file content line by line
    std::string line;
    std::string cantidad_polys;
    std::getline(inputFile, cantidad_polys);
    int poly_num = std::stoi(cantidad_polys);
    std::cout <<poly_num<<" polygons\n";
    for (int i = 0; i < poly_num; i++){
      std::vector<vec3d> vertex_list;
      std::vector<std::vector<uint>>  face_list; 
        std::getline(inputFile, line);
        std::istringstream info(line);
        std::string nodes;
        std::string faces;
        std::getline(info,nodes,' ');
        std::getline(info,faces,' ');
        int node_num = std::stoi(nodes);
        int face_num = std::stoi(faces);
        // std::cout<<"the polyhedron "<<i<<" have "<<node_num<<" nodes and "<<face_num<<" faces.\n"; 
        for(int n = 0; n < node_num; n++){
            std::getline(inputFile, line);
            std::istringstream tokenStream(line);
            std::string x;
            std::string y;
            std::string z;
            std::getline(tokenStream,x,' ');
            std::getline(tokenStream,y,' ');
            std::getline(tokenStream,z,' ');
            vec3d vertex(std::stod(x),std::stod(y),std::stod(z));
            vertex_list.push_back(vertex);
            // std::cout<<"It node "<<n<< " is: "<<x<<" , "<<y<<" , "<<z<<'\n';
        }
        for(int f = 0; f < face_num; f++){
            std::getline(inputFile, line);
            std::istringstream tokenStream(line);
            std::string nv;
            std::string v1;
            std::string v2;
            std::string v3;
            std::getline(tokenStream,nv,' ');
            std::getline(tokenStream,v1,' ');
            std::getline(tokenStream,v2,' ');
            std::getline(tokenStream,v3,' ');
            uint uv1 = uint(std::stoul(v1));
            uint uv2 = uint(std::stoul(v2));
            uint uv3 = uint(std::stoul(v3));
            std::vector<uint> face = {uv1,uv2,uv3};
            face_list.push_back(face);
            // std::cout<<"It face "<<f<<" are: "<<v1<<" , "<<v2<<" , "<<v3<<'\n';
        }
        std::pair<std::vector<vec3d>,std::vector<std::vector<uint>>> poly_info(vertex_list,face_list);
        polyhedron_list.push_back(poly_info);
    }
  return polyhedron_list;
}

vec3d calculateCrossProduct(const vec3d& v1, const vec3d& v2, const vec3d& v3) {
    std::vector<double> u = {v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]};
    std::vector<double> v = {v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]};
    vec3d A = v2-v1;
    vec3d B = v3-v1;

    return A.cross(B);
}

double calculatePolygonArea(const std::vector<vec3d> &vertices){
    double area[]= {0,0,0};
    
    vec3d v0 = vertices[0];
    for (int i = 1; i < vertices.size()-1; i++){
        
        vec3d v1 = vertices[i];
        vec3d v2 = vertices[i + 1];

        // std::cout<<v0[0]<<" , "<<v0[1]<<" , "<<v0[2]<<"\n";
        // std::cout<<v1[0]<<" , "<<v1[1]<<" , "<<v1[2]<<"\n";
        // std::cout<<v2[0]<<" , "<<v2[1]<<" , "<<v2[2]<<"\n";
        
        double crossProduct[3];
        vec3d local_area = calculateCrossProduct(v0,v1,v2);
        area[0] += local_area[0];
        area[1] += local_area[1];
        area[2] += local_area[2];
    }
    double areaMagnitude = 0.5 * std::sqrt(
        std::pow(area[0], 2) +
        std::pow(area[1], 2) +
        std::pow(area[2], 2)
    );
    return areaMagnitude;
}

double calculatePolyhedronArea(const std::vector<vec3d> &vertices, std::vector<std::vector<uint>> &faces){
    double area = 0;
    for(int i = 0; i < faces.size(); i++){
        std::vector<vec3d> coords;
        for(int face = 0; face < faces[i].size(); face++){
            coords.push_back(vertices[faces[i][face]]);
        }
        double polygon_area = calculatePolygonArea(coords);
        area += polygon_area;
    }
    return area;
}
double matrix3Determinant(const vec3d &v1, const vec3d &v2, const vec3d &v3){
    
    double det_sub_matrix1 = v2[1]*v3[2] - v2[2]*v3[1];
    double det_sub_matrix2 = v1[1]*v3[2] - v3[1]*v1[2];
    double det_sub_matrix3 = v1[1]*v2[2] - v2[1]*v1[2];
    double det = v1[0]* det_sub_matrix1 - v2[0]*det_sub_matrix2 + v3[0]*det_sub_matrix3;

    // double detP = v1[0]*v2[1]*v3[2] + v1[1]*v2[2]*v3[0] + v1[2]*v2[0]*v3[1];
    // double detN = v1[2]*v2[1]*v3[0] + v1[0]*v2[2]*v3[1] + v1[1]*v2[0]*v3[2];
    
    return det;
}
double calculatePolyhedronVolume(const std::vector<vec3d> &vertices, std::vector<std::vector<uint>> &faces){
    double sumDet = 0;
    for (int i = 0; i < faces.size(); i++){
        vec3d v1 = vertices[faces[i][0]];
        vec3d v2 = vertices[faces[i][1]];
        vec3d v3 = vertices[faces[i][2]];

        double det = matrix3Determinant(v1,v2,v3);
        sumDet += det;
    }
    
    return sumDet / 6.0;
}
int main(int argc, char *argv[]) {
  std::string input =
      (argc == 2) ? std::string(argv[1])
                  : std::string(DATA_PATH) + "complex_models/rt4_arm.off";
  std::cout << "Input: " << input << std::endl;


  // vec3d v1(0.457277 ,0.370734 ,0.207050);
  // vec3d v2(0.442931, 0.684102 ,0.000000);
  // vec3d v3(1.000000, 0.560012 ,0.000000);
  // vec3d v4(1.000000 ,0.000000 ,0.000000);
  // std::vector<vec3d> v = {v1,v2,v3,v4};
  // std::vector<uint> p1 = {1 ,2 ,0};
  // std::vector<uint> p2 = {3 ,1 ,0};
  // std::vector<uint> p3 = {3 ,1 ,2};
  // std::vector<uint> p4 = {3, 2 ,0};
  // std::vector<std::vector<uint>> p = {p1,p2,p3,p4};
  if (argc == 2){
    std::vector<std::pair<std::vector<vec3d>, std::vector<std::vector<uint>>>> polys_info;
    polys_info = readFile(input);
    int vector_size = polys_info.size();
    input.erase(input.end() - 4, input.end());
    std::vector<double> ratios;
    for(int i = 0; i < vector_size; i++){
      std::pair<std::vector<vec3d>, std::vector<std::vector<uint>>> polyhedron = polys_info[i];
      std::vector<vec3d> v = polyhedron.first;
      std::vector<std::vector<uint>> p = polyhedron.second;
      Polygonmesh<> m(v,p);
      double area = calculatePolyhedronArea(v,p);
      double volume = calculatePolyhedronVolume(v,p);
      std::cout << "Polyhedron volume is = "<<volume<<'\n';



      auto start = std::chrono::steady_clock::now();

      PolyhedronKernel K;
      K.initialize(m.vector_verts());
      // std::cout<<"compute\n";
      K.compute(m.vector_verts(), m.vector_polys(), m.vector_poly_normals());

      auto time = std::chrono::duration_cast<std::chrono::milliseconds>(
          std::chrono::steady_clock::now() - start);
      // std::cout<<"vertexs: \n";
      // for (int n = 0; n < K.kernel_verts.size(); n++){
      //   vec3d node = K.kernel_verts[n];
      //   std::cout << node.x() << " , " << node.y() << " , " << node.z() << '\n'; 
      // }
      Polygonmesh<> kernel(K.kernel_verts, K.kernel_faces);
      std::cout << "Kernel: " << kernel.num_verts() << " verts, "
                << kernel.num_polys() << " faces" << std::endl
                << "Elapsed time: " << time.count() << " ms" << std::endl;
      double kernel_volume = calculatePolyhedronVolume(K.kernel_verts, K.kernel_faces);
      std::cout << "Kernel volume = "<<kernel_volume<<'\n';
      
      std::string output = input + std::to_string(i) + "_kernel.off";
      kernel.save(output.c_str());
      std::cout << "Saved in: " << output << std::endl;
      double ratio = kernel_volume/volume;
      std::cout << "Volume ratio = "<<ratio<<'\n';
      ratios.push_back(ratio);
    }
    double sum,prom;
    double max = *std::max_element(ratios.begin(), ratios.end()), min = *std::min_element(ratios.begin(), ratios.end());
    sum = std::accumulate(ratios.begin(), ratios.end(), 0);
    prom = sum / ratios.size();
    std::cout<<"Ratio statistics: \nMean: "<<prom<<'\n'<<"Min: "<<min<<'\n'<<"Max: "<<max<<'\n';
  }
  else{
    Polygonmesh<> m(input.c_str());

    // Polygonmesh<> m(v,p);

    auto start = std::chrono::steady_clock::now();

    PolyhedronKernel K;
    K.initialize(m.vector_verts());
    // std::cout<<"compute\n";
    K.compute(m.vector_verts(), m.vector_polys(), m.vector_poly_normals());

    auto time = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start);

    Polygonmesh<> kernel(K.kernel_verts, K.kernel_faces);
    std::cout << "Kernel: " << kernel.num_verts() << " verts, "
              << kernel.num_polys() << " faces" << std::endl
              << "Elapsed time: " << time.count() << " ms" << std::endl;

    input.erase(input.end() - 4, input.end());
    std::string output = input + "_kernel.off";
    kernel.save(output.c_str());
    std::cout << "Saved in: " << output << std::endl;
  }
}
