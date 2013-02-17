cimport cython
cimport numpy as np
import numpy as np
from UserDict import DictMixin

cdef extern from "errno.h":
    cdef extern int errno

cdef extern from "string.h":
    char *strerror(int)

cdef extern from "hdf/hntdefs.h":
    cdef enum:
        DFNT_UCHAR = 3
        DFNT_CHAR = 4
        DFNT_FLOAT32 = 5
        DFNT_FLOAT64 = 6
        DFNT_INT8 = 20
        DFNT_UINT8 = 21
        DFNT_INT16 = 22
        DFNT_UINT16 = 23
        DFNT_INT32 = 24
        DFNT_UINT32 = 25
        DFNT_INT64 = 26
        DFNT_UINT64 = 27

cdef extern from "hdf/hdf.h":
    cdef enum:
        FAIL = -1
        DFACC_READ = 1
        MAX_VAR_DIMS = 32
        FIELDNAMELENMAX = 128
    
    ctypedef np.npy_int16 int16
    ctypedef np.npy_int32 int32
    ctypedef int intn
    ctypedef int hdf_err_code_t
    
    int32 SDstart(char *, int32)
    int32 SDnametoindex(int32, char *)
    int32 SDselect(int32, int32)
    intn SDgetinfo(int32, char *, int32 *, int32 [], int32 *, int32 *)
    intn SDreaddata(int32, int32 *, int32 *, int32 *, void *)
    intn SDendaccess(int32)
    intn SDend(int32)
    intn SDattrinfo(int32, int32, char *, int32 *, int32 *)
    intn SDreadattr(int32, int32, void *)
    int32 SDfindattr(int32, char *)
    intn SDfileinfo(int32, int32 *, int32 *)
    int16 HEvalue(int32)
    char *HEstring(hdf_err_code_t)

DTYPE = {
    DFNT_UCHAR: np.ubyte,
    DFNT_CHAR: np.byte,
    DFNT_FLOAT32: np.float32,
    DFNT_FLOAT64: np.float64,
    DFNT_INT8: np.int8,
    DFNT_UINT8: np.uint8,
    DFNT_INT16: np.int16,
    DFNT_UINT16: np.uint16,
    DFNT_INT32: np.int32,
    DFNT_UINT32: np.uint32,
    DFNT_INT64: np.int64,
    DFNT_UINT64: np.uint64,
}


class Attributes(DictMixin):
    def __init__(self, hdf, dataset=None):
        self.hdf = hdf
        self.dataset = dataset
    
    def __getitem__(self, key):
        return self.hdf._readattr(self.dataset, key)

    def keys(self):
        return self.hdf._attributes(self.dataset)


class Dataset(object):
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name
        info = self.hdf._getinfo(name)
        self.shape = info['shape']
        self.rank = len(self.shape)
        self.attributes = Attributes(self.hdf, name)
        
    def __getitem__(self, key):
        starta = np.zeros(self.rank, dtype=np.int32)
        edgesa = self.shape.copy()
        
        if type(key) != tuple:
            key = (key,)
        
        if len(key) > self.rank:
            raise IndexError('too many indices')
        
        dims = np.ones(self.rank, dtype=np.bool)
        for i, s, n in zip(range(self.rank), key, self.shape):
            if type(s) != slice:
                if s < 0: s += n
                if s < 0 or s >= n: raise IndexError('index out of bounds')
                starta[i] = s
                edgesa[i] = 1
                dims[i] = False
            else:
                if s.step is not None:
                    raise IndexError('stride not supported')
                start, stop = s.start, s.stop
                if start is None: start = 0
                if stop is None: stop = n
                if start < 0: start += n
                if stop < 0: stop += n
                start = min(max(0, n-1), max(0, start))
                stop = min(n, max(0, stop))
                starta[i] = start
                edgesa[i] = max(0, stop - start)
        
        data = self.hdf._read(self.name, starta, edgesa)
        shape = []
        for n, d in zip(data.shape, dims):
            if d: shape.append(n)
        if len(shape) == 0: return data.ravel()[0]
        else: return data.reshape(shape)


class SDS(object):
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name

    def __enter__(self):
        errno = 0
        index = SDnametoindex(self.hdf.sd, self.name)
        if index == FAIL: raise KeyError(self.name)
        self.sds = SDselect(self.hdf.sd, index)
        if self.sds == FAIL:
            self.hdf._error('HDF: SDselect of dataset "%s" failed' % self.name)
        return self.sds
    
    def __exit__(self, exc_type, exc_value, traceback):
        SDendaccess(self.sds)


class HDF(DictMixin):
    def __init__(self, filename):
        self.filename = filename
        self.sd = SDstart(filename, DFACC_READ);
        if self.sd == FAIL: self._error('HDF: SDstart failed', from_errno=True)
        self.attributes = Attributes(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        SDend(self.sd)
        self.sd = None

    def __getitem__(self, key):
        #with SDS(self, key) as sds: pass # Ensure SDS exists.
        return Dataset(self, key)

    def keys(self):
        cdef int32 rank, data_type, num_datasets, num_global_attrs, num_attrs
        cdef np.ndarray[int32, ndim=1] dims
        cdef np.ndarray[char, ndim=1] tmp

        dims = np.zeros(MAX_VAR_DIMS, dtype=np.int32)

        res = SDfileinfo(self.sd, &num_datasets, &num_global_attrs)
        if res == FAIL: self._error('HDF: SDfileinfo failed')

        datasets = []
        for i in range(num_datasets):
            tmp = np.zeros(FIELDNAMELENMAX, dtype=np.byte)
            sds = SDselect(self.sd, i)
            res = SDgetinfo(sds, <char *>tmp.data, &rank, <int32 *>dims.data, &data_type, &num_attrs)
            if res == FAIL: self._error('HDF: SDgetinfo failed')
            sds_name = bytearray(tmp).decode('ascii').rstrip('\0')
            datasets.append(sds_name)
        return datasets

    def _error(self, errmsg=None, from_errno=False):
        errcode = HEvalue(1)
        if errcode != 0:
            msg = '%s: %s' % (errmsg, HEstring(errcode))
            raise IOError(errcode, msg, self.filename)
        elif errno != 0 and from_errno:
            raise IOError(errno, strerror(errno), self.filename)
        elif errmsg is not None:
            raise IOError(0, errmsg, self.filename)
        else:
            raise IOError(0, 'HDF: Unknown error', self.filename)

    def _attributes(self, dataset=None):
        cdef int32 num_datasets, num_global_attrs

        if dataset is None:
            res = SDfileinfo(self.sd, &num_datasets, &num_global_attrs)
            if res == FAIL: self._error('HDF: SDfileinfo failed')
            return self._attributes2(self.sd, num_global_attrs)
        else:
            info = self._getinfo(dataset)
            with SDS(self, dataset) as sds:
                return self._attributes2(sds, info['num_attrs'])
    
    def _attributes2(self, obj_id, n):
        cdef np.ndarray[char, ndim=1] tmp
        cdef int32 data_type, count

        attrs = []
        for i in range(n):
            tmp = np.zeros(FIELDNAMELENMAX, dtype=np.byte)
            res = SDattrinfo(obj_id, i, <char *>tmp.data, &data_type, &count)
            if res == FAIL: self._error('HDF: SDattrinfo failed')
            attr_name = bytearray(tmp).decode('ascii').rstrip('\0')
            attrs.append(attr_name)
        return attrs
   
    def _getinfo(self, name):
        cdef int32 rank, data_type, num_attrs
        cdef np.ndarray[int32, ndim=1] dims
        dims = np.zeros(MAX_VAR_DIMS, dtype=np.int32)
        with SDS(self, name) as sds:
            res = SDgetinfo(sds, NULL, &rank, <int32 *>dims.data, &data_type, &num_attrs)
        if res == FAIL: self._error('HDF: SDgetinfo on dataset "%s" failed' % name)
        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError('%s: %s: Data type %s not implemented'
                                              % (self.filename, name, data_type))
        return {
            'shape': dims[:rank],
            'dtype': dtype,
            'num_attrs': num_attrs,
        }
    
    def _normalize(self, index, dims, default=0, incl=False):
        if len(index) > len(dims):
            raise IndexError('too many indices')
        r = len(index)
        newindex = np.ones(len(dims), dtype=np.int32)*default
        newindex[:r] = index
        for i in range(len(dims)):
            if newindex[i] < 0: newindex[i] += dims[i]
            if newindex[i] < 0 or newindex[i] > dims[i] or \
               (newindex[i] == dims[i] and not incl):
                raise IndexError('index out of bounds')
        return newindex
    
    def _read(self, name, start, edges):
        info = self._getinfo(name)
        shape = info['shape']
        dtype = info['dtype']
        
        if len(start) != len(shape) or len(edges) != len(shape):
            raise IndexError('invalid number of indices')
        
        if np.any(np.logical_or(start < 0, start >= shape)) or\
           np.any(np.logical_or(edges < 0, edges - start > shape)):
            raise IndexError('index out of bounds')
        
        cdef np.ndarray[int32, ndim=1] cstart = np.array(start, dtype=np.int32)
        cdef np.ndarray[int32, ndim=1] cedges = np.array(edges, dtype=np.int32)
        data = np.zeros(edges, dtype=dtype)
        cdef np.ndarray[char, ndim=1] buf = data.view(dtype=np.int8).ravel()
        with SDS(self, name) as sds:
            res = SDreaddata(sds, <int32 *>cstart.data, NULL, <int32 *>cedges.data, <void *>buf.data);
        data = buf.view(dtype=dtype).reshape(edges)
        return data
    
    def _readattr(self, dataset, name):
        if dataset is not None:
            with SDS(self, dataset) as sds:
                return self._readattr2(sds, name)
        else:
            return self._readattr2(self.sd, name)
    
    def _readattr2(self, obj_id, name):
        cdef int32 data_type, count
        index = SDfindattr(obj_id, name)
        if index == FAIL: raise KeyError(name)
        cdef np.ndarray[char, ndim=1] tmp
        tmp = np.zeros(FIELDNAMELENMAX, dtype=np.byte)
        res = SDattrinfo(obj_id, index, <char *>tmp.data, &data_type, &count)
        if res == FAIL:
            self._error('HDF: SDattrinfo of "%s" failed' % name)
        
        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError(
            '%s: %s: Data type %s not implemented' %\
            (self.filename, name, data_type))
        
        data = np.zeros(count, dtype=dtype)
        cdef np.ndarray[char, ndim=1] buf = data.view(dtype=np.int8).ravel()
        res = SDreadattr(obj_id, index, <void *>buf.data);
        if res == FAIL:
            self._error('HDF: SDreadattr of "%s" failed' % name)
        
        if data_type == DFNT_CHAR:
            return bytearray(data).decode('ascii').rstrip('\0')

        return data[0] if count == 1 else data
