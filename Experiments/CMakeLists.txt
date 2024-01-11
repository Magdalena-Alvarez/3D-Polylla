cmake_minimum_required(VERSION 3.16)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED 1)

project(Polylla_Experiments)

add_executable(Exps experiments.cpp)
find_package(Verdict)