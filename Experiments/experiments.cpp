#include <iostream>

#include "verdict.h"
#include <fstream>
#include <string>
#include <vector>


int main(){
    
    std::cout<<"Start experiments\n\n\n";
    std::cout<<"Reading the file\n\n";
    std::fstream myfile ("../../logs/face_orig20.off");
    if(!myfile){
        std::cout<<"Fail reading the file\n\n";
    }
    else{
        std::cout<<"File is ready\n\n";
        std::string myText;
        //reading 'off' text
        myfile>>myText;
        //start reading the data
        myfile>>myText;
        int n_vertex = stoi(myText);

        myfile>>myText;
        int n_faces = stoi(myText);

        myfile>>myText;
        float vertex[n_vertex];
        float v;
        for (int i = 0; i<n_vertex; i++) {

            myfile>>v;
            vertex[i] = v;
            std::cout << v<<'\n';
        }

        std::vector<int*> faces;
        int v;
        for (int i = 0; i<n_faces; i++) {
            int face[3];
            //first num 
            myfile>>v;
            myfile>>v;
            face[0] = v;
            face[1] = v;
            face[2] = v;
            faces.push_back(face);
            std::cout << v<<'\n';
        }

        for (int i = 0; i<n_vertex;i++){
            std:: cout << vertex[i]<<'\n';
        }
    }

    myfile.close();


    return 0;
}