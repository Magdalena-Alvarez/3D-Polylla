#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <cmath>

double calculateTriangleArea(const std::vector<double>& v1, const std::vector<double>& v2, const std::vector<double>& v3) {
    std::vector<double> u = {v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]};
    std::vector<double> v = {v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]};
    // std::cout<<v1[0]<<" , "<<v1[1]<<" , "<<v1[2]<<"\n";
    // std::cout<<v2[0]<<" , "<<v2[1]<<" , "<<v2[2]<<"\n";
    // std::cout<<v3[0]<<" , "<<v3[1]<<" , "<<v3[2]<<"\n";
    double crossProductMagnitude = 0.5 * std::sqrt(
        std::pow(u[1] * v[2] - u[2] * v[1], 2) +
        std::pow(u[2] * v[0] - u[0] * v[2], 2) +
        std::pow(u[0] * v[1] - u[1] * v[0], 2)
    );

    return crossProductMagnitude;
}

void calculateCrossProduct(double crossProduct[], const std::vector<double>& v1, const std::vector<double>& v2, const std::vector<double>& v3) {
    std::vector<double> u = {v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]};
    std::vector<double> v = {v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]};
    // std::cout<<v1[0]<<" , "<<v1[1]<<" , "<<v1[2]<<"\n";
    // std::cout<<v2[0]<<" , "<<v2[1]<<" , "<<v2[2]<<"\n";
    // std::cout<<v3[0]<<" , "<<v3[1]<<" , "<<v3[2]<<"\n";
    
    crossProduct[0] = (u[1] * v[2] - u[2] * v[1]);
    crossProduct[1] = -(u[2] * v[0] - u[0] * v[2]);
    crossProduct[2] = (u[0] * v[1] - u[1] * v[0]);


}

double calculatePolygonArea(const std::vector<std::vector<double>> &vertices){
    double area[]= {0,0,0};
    
    std::vector<double> v0 = vertices[0];
    for (int i = 1; i < vertices.size()-1; i++){
        
        std::vector<double> v1 = vertices[i];
        std::vector<double> v2 = vertices[i + 1];

        // std::cout<<v0[0]<<" , "<<v0[1]<<" , "<<v0[2]<<"\n";
        // std::cout<<v1[0]<<" , "<<v1[1]<<" , "<<v1[2]<<"\n";
        // std::cout<<v2[0]<<" , "<<v2[1]<<" , "<<v2[2]<<"\n";
        
        double crossProduct[3];
        calculateCrossProduct(crossProduct,v0,v1,v2);
        area[0] += crossProduct[0];
        area[1] += crossProduct[1];
        area[2] += crossProduct[2];
    }
    double areaMagnitude = 0.5 * std::sqrt(
        std::pow(area[0], 2) +
        std::pow(area[1], 2) +
        std::pow(area[2], 2)
    );
    return areaMagnitude;
}

double calculatePolyhedronArea(const std::vector<std::vector<double>> &vertices, std::vector<std::vector<uint>> &faces){
    double area = 0;
    for(int i = 0; i < faces.size(); i++){
        std::vector<std::vector<double>> coords;
        for(int face = 0; face < faces[i].size(); face++){
            coords.push_back(vertices[faces[i][face]]);
        }
        double polygon_area = calculatePolygonArea(coords);
        area += polygon_area;
    }
    return area;
}

double calculatePointProduct(double n[], std::vector<double> v1){
    return v1[0]*n[0] + v1[1]*n[1] + v1[2]*n[2];
}

double matrix3Determinant(const std::vector<double> &v1, const std::vector<double> &v2, const std::vector<double> &v3){
    
    double det_sub_matrix1 = v2[1]*v3[2] - v2[2]*v3[1];
    double det_sub_matrix2 = v1[1]*v3[2] - v3[1]*v1[2];
    double det_sub_matrix3 = v1[1]*v2[2] - v2[1]*v1[2];
    double det = v1[0]* det_sub_matrix1 - v2[0]*det_sub_matrix2 + v3[0]*det_sub_matrix3;

    // double detP = v1[0]*v2[1]*v3[2] + v1[1]*v2[2]*v3[0] + v1[2]*v2[0]*v3[1];
    // double detN = v1[2]*v2[1]*v3[0] + v1[0]*v2[2]*v3[1] + v1[1]*v2[0]*v3[2];
    
    return det;
}
double calculatePolyhedronVolume(const std::vector<std::vector<double>> &vertices, std::vector<std::vector<uint>> &faces){
    double sumVol = 0;
    for (int i = 0; i < faces.size(); i++){
        std::vector<double> v1 = vertices[faces[i][0]];
        std::vector<double> v2 = vertices[faces[i][1]];
        std::vector<double> v3 = vertices[faces[i][2]];

        double cross_product[3];
        calculateCrossProduct(cross_product,v1,v2,v3) ;

        sumVol += calculatePointProduct(cross_product,v1);
    }
    
    return sumVol / 6.0;
}

int main() {
    // File path
    std::string filePath = "face_polys20.txt";

    // Create an input file stream
    std::ifstream inputFile(filePath);

    // Check if the file is open
    if (!inputFile.is_open()) {
        std::cerr << "Error opening the file: " << filePath << std::endl;
        return 1;
    }

    
    std::vector<std::pair<std::vector<std::vector<double>>,std::vector<std::vector<uint>>>> polyhedron_list;
    // Read the file content line by line
    std::string line;
    std::string cantidad_polys;
    std::getline(inputFile, cantidad_polys);
    int poly_num = std::stoi(cantidad_polys);
    std::cout <<poly_num<<" polygons\n";
    for (int i = 0; i < poly_num; i++){
        std::vector<std::vector<double>> vertex_list;
        std::vector<std::vector<uint>> face_list;
        std::getline(inputFile, line);
        std::istringstream info(line);
        std::string nodes;
        std::string faces;
        std::getline(info,nodes,' ');
        std::getline(info,faces,' ');
        int node_num = std::stoi(nodes);
        int face_num = std::stoi(faces);
        std::cout<<"the polyhedron "<<i<<" have "<<node_num<<" nodes and "<<face_num<<" faces.\n"; 
        for(int n = 0; n < node_num; n++){
            std::getline(inputFile, line);
            std::istringstream tokenStream(line);
            std::string x;
            std::string y;
            std::string z;
            std::getline(tokenStream,x,' ');
            std::getline(tokenStream,y,' ');
            std::getline(tokenStream,z,' ');
            std::vector<double> vertex = {std::stod(x),std::stod(y),std::stod(z)};
            vertex_list.push_back(vertex);
            // std::cout<<"It node "<<n<< " is: "<<x<<" , "<<y<<" , "<<z<<'\n';
        }
        double polyhedronArea = 0;
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
            // std::cout<<"It face "<<f<<" is: "<<v1<<" , "<<v2<<" , "<<v3<<'\n';
            double area;
            
            // area = calculateTriangleArea(vertex_list[uv1],vertex_list[uv2],vertex_list[uv3]);
            // std::cout<<"AreaT = "<<area<<'\n';
            std::vector<std::vector<double>> vertices = {vertex_list[uv1],vertex_list[uv2],vertex_list[uv3]};
            area = calculatePolygonArea(vertices);
            polyhedronArea+= area;
            // std::cout<<"Area = "<<area<<'\n';
        }
        std::cout<<"The area of the polyhedron is = "<<polyhedronArea<<'\n';
        std::pair<std::vector<std::vector<double>>,std::vector<std::vector<uint>>> poly_info(vertex_list,face_list);
        polyhedron_list.push_back(poly_info);
        double polyhedronArea2 = calculatePolyhedronArea(poly_info.first,poly_info.second);
        std::cout<<"The calculated area of the polyhedron is = "<<polyhedronArea2<<'\n';
        std::cout<<"The calculated volume of the polyhedron is = "<<calculatePolyhedronVolume(poly_info.first,poly_info.second)<<'\n';
        std::cout<<"The area/volume ratio is = "<<polyhedronArea2 / calculatePolyhedronVolume(poly_info.first,poly_info.second)<<'\n';
    }
    std::ofstream myfile;
    myfile.open ("output.txt");
    myfile << "Writing this to a file.\n";
    myfile.close();
    
    // Close the file
    inputFile.close();

    return 0;
}
