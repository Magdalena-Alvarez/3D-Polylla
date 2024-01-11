cmake_minimum_required(VERSION 3.2)

project(kernel_library)

# Add the source files
set(SOURCES polyhedron_kernel.cpp)

set(SOURCES ${SOURCES} sort_points.h)

# Create the shared library
add_library(${PROJECT_NAME} SHARED ${SOURCES})

find_package(cinolib REQUIRED)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(${PROJECT_NAME} cinolib)
#cmake .. -DCMAKE_BUILD_TYPE=Release -Dcinolib_DIR=/home/malvarez/Documents/Tesis/polyhedron_kernel-main