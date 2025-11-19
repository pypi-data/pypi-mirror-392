from libc.stdint cimport int32_t
import numpy as np
cimport numpy as np

ctypedef np.float64_t DTYPE_t
ctypedef np.int32_t ITYPE_t

cdef extern from "prodtools_impl.cpp":
    cdef double proddot_impl(const int sz,
                             const double *psfpsf,
                             const double *x_integ,
                             const double *y_integ,
                             const double *z_integ,
                             const int32_t *x_index,
                             const int32_t *y_index,
                             const int32_t *z_index)

def proddot(np.ndarray[DTYPE_t, ndim=1, mode="c"] psfpsf,
            np.ndarray[DTYPE_t, ndim=1, mode="c"] x_integ,
            np.ndarray[DTYPE_t, ndim=1, mode="c"] y_integ,
            np.ndarray[DTYPE_t, ndim=1, mode="c"] z_integ,
            np.ndarray[ITYPE_t, ndim=1, mode="c"] x_index,
            np.ndarray[ITYPE_t, ndim=1, mode="c"] y_index,
            np.ndarray[ITYPE_t, ndim=1, mode="c"] z_index
):
    cdef int sz = psfpsf.shape[0]
    return proddot_impl(sz, <const double*>psfpsf.data,
        <const double*>x_integ.data, <const double*>y_integ.data, <const double*>z_integ.data,
        <const int32_t*>x_index.data, <const int32_t*>y_index.data, <const int32_t*>z_index.data)
