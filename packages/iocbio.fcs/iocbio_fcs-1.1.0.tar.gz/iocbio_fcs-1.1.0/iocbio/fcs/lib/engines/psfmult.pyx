from libcpp.vector cimport vector
from libc.stdint cimport int32_t
import numpy as np
cimport numpy as np

ctypedef np.float64_t DTYPE_t
ctypedef np.int32_t ITYPE_t

cdef extern from "psfmult_impl.cpp":
    cdef void psfmult_impl(const vector[double] &psf,
                            const vector[int32_t] &x,
                            const vector[int32_t] &y,
                            const vector[int32_t] &z,
                            vector[double] &psfpsf,
                            vector[int32_t] &dx,
                            vector[int32_t] &dy,
                            vector[int32_t] &dz)

def psfmult(np.ndarray[DTYPE_t, ndim=1, mode="c"] psf,
             np.ndarray[ITYPE_t, ndim=1, mode="c"] x,
             np.ndarray[ITYPE_t, ndim=1, mode="c"] y,
             np.ndarray[ITYPE_t, ndim=1, mode="c"] z):
     cdef vector[double] psfpsf
     cdef vector[int32_t] dx
     cdef vector[int32_t] dy
     cdef vector[int32_t] dz
     psfmult_impl(psf, x, y, z, psfpsf, dx, dy, dz)
     return np.array(psfpsf), np.array(dx, dtype=np.int32), np.array(dy, dtype=np.int32), np.array(dz, dtype=np.int32)
