#include <pybind11/pybind11.h>
#include "polyhedron_kernel.h"

namespace py = pybind11;

PYBIND11_MODULE(polyhedron_kernel, m) {
    py::class_<PolyhedronKernel>(m, "PolyhedronKernel")
        .def(py::init<>())
        .def("initialize", &PolyhedronKernel::initialize);
        .def("compute", &PolyhedronKernel::compute);
}