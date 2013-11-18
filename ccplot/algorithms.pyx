cimport cython
cimport numpy as np
import numpy as np

cdef extern from "math.h":
    double floor(double)
    double ceil(double)
    double round(double)

cdef extern from "numpy/npy_math.h":
    bint npy_isnan(double x)


def interp2d_12(np.ndarray[float, ndim=2, mode="c"] data not None,
                np.ndarray[float, ndim=1, mode="c"] X not None,
                np.ndarray[float, ndim=2, mode="c"] Z not None,
                float x1, float x2, int nx,
                float z1, float z2, int nz):
    """Interpolate 2D data with coordinates given by 1D and 2D arrays.

    data is a two-dimensional array of data to be interpolated.
    X and Z are one- and two-dimensional arrays, giving coordinates
    of data points along the first and second axis, resp.

    data, X and Z are expected to be C-contiguous float32 numpy arrays
    with no mask and no transformation (such as transposition) applied.
    """
    cdef int i, j, n, m
    cdef float n1, n2
    cdef float m1, m2
    cdef float xs, zs
    cdef int w, h

    xs = (x2 - x1)/nx
    zs = (z2 - z1)/nz
    w = data.shape[0]
    h = data.shape[1]

    output = np.zeros((nx, nz), dtype=np.float32)
    cdef np.ndarray[float, ndim=2] out = output
    cdef np.ndarray[int, ndim=2] q = np.zeros((nx, nz), dtype=np.int32)

    for i in range(w):
        n1 = ((X[i-1] + X[i])/2 - x1)/xs if i-1 >= 0 else -1
        n2 = ((X[i+1] + X[i])/2 - x1)/xs if i+1 < w else nx
        if n2 - n1 < 1: n1 = n2 = (X[i] - x1)/xs

        for j in range(h):
            m1 = ((Z[i,j-1] + Z[i,j])/2 - z1)/zs if j-1 >= 0 else -1
            m2 = ((Z[i,j+1] + Z[i,j])/2 - z1)/zs if j+1 < h else nz
            if m2 - m1 < 1: m1 = m2 = (Z[i,j] - z1)/zs

            for n in range(<int>(n1+0.5), <int>(n2+0.5+1)):
                for m in range(<int>(m1+0.5), <int>(m2+0.5+1)):
                    if n < 0 or n >= nx: continue
                    if m < 0 or m >= nz: continue
                    if npy_isnan(data[i,j]): continue
                    out[n,m] += data[i,j]
                    q[n,m] += 1

    for n in range(nx):
        for m in range(nz):
            out[n,m] /= q[n,m]

    return output
