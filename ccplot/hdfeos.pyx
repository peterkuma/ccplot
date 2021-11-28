cimport cython
cimport numpy as np
import sys
import os
import numpy as np
from ccplot import hdf
from .autostr import autostr, Autostr

if sys.version_info[0] == 2:
    from UserDict import DictMixin as DictMixin
else:
    from collections.abc import Mapping
    class DictMixin(Mapping):
        def __iter__(self):
            yield from self.keys()
        def __len__(self):
            return len(self.keys())

cdef extern from "errno.h":
    cdef extern int errno

    cdef enum:
        EIO = 5

cdef extern from "string.h":
    char *strerror(int)

cdef extern from "hntdefs.h":
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

cdef extern from "hdf.h":
    cdef enum:
        FAIL = -1
        DFACC_READ = 1
        H4_MAX_VAR_DIMS = 32
        FIELDNAMELENMAX = 128
        DFACC_RDONLY = 1

    ctypedef np.npy_int16 int16
    ctypedef np.npy_int32 int32
    ctypedef int intn
    ctypedef int hdf_err_code_t
    ctypedef void * VOIDP

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
    int16 HEvalue(int32)
    char *HEstring(hdf_err_code_t)

cdef extern from "HdfEosDef.h":
    int32 SWopen(char *, intn)
    int32 SWattach(int32, char *)
    intn SWfieldinfo(int32, char *, int32 *, int32 [], int32 *, char *)
    intn SWreadattr(int32, char *, VOIDP)
    intn SWattrinfo(int32, char *, int32 *, int32 *)
    intn SWreadfield(int32, char *, int32 [], int32 [], int32 [], VOIDP)
    intn SWgetfillvalue(int32, char *, VOIDP)
    intn SWdetach(int32)
    intn SWclose(int32)
    int32 SWinqmaps(int32, char *, int32 [], int32 [])
    int32 SWinqattrs(int32, char *, int32 *)
    int32 SWinqswath(char *, char *, int32 *)
    int32 SWnentries(int32, int32, int32 *)
    int32 SWinqgeofields(int32, char *, int32 [], int32 [])
    int32 SWinqdatafields(int32, char *, int32 [], int32 [])

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


class Attributes(DictMixin, Autostr):
    @autostr
    def __init__(self, hdfeos, swath=None, dataset=None):
        self.hdfeos = hdfeos
        self.swath = swath
        self.dataset = dataset

    @autostr
    def __getitem__(self, key):
        if self.swath is None:
            return self.hdfeos.hdf.attributes[key]

        try:
            return self.hdfeos._readattr(self.swath, self.dataset, key)
        except KeyError:
            if self.dataset is not None:
                try:
                    return self.hdfeos.hdf[self.dataset].attributes[key]
                except KeyError: raise KeyError(self._autostr(key))
            else: raise KeyError(self._autostr(key))

    @autostr
    def keys(self):
        if self.swath is None:
            return self.hdfeos.hdf.attributes.keys()

        attrs = self.hdfeos._attributes(self.swath, self.dataset)
        if self.dataset is not None:
            try: attrs += self.hdfeos.hdf[self.dataset].attributes.keys()
            except KeyError: pass
        return attrs


class Dataset(Autostr):
    @autostr
    def __init__(self, hdfeos, swath, name):
        self.hdfeos = hdfeos
        self.swath = swath
        self.name = name
        info = self.hdfeos._getinfo(swath, name)
        self.shape = info['shape']
        self.rank = len(self.shape)
        self.dims = info['dimlist']
        self.attributes = Attributes(self.hdfeos, swath, name)

    @autostr
    def __getitem__(self, key):
        starta = np.zeros(self.rank, dtype=np.int32)
        edgesa = self.shape.copy()

        if type(key) != tuple:
            key = (key,)

        if len(key) > self.rank:
            raise IndexError('too many indices')

        dims = np.ones(self.rank, dtype=bool)
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

        data = self.hdfeos._read(self.swath, self.name, starta, edgesa)
        shape = []
        for n, d in zip(data.shape, dims):
            if d: shape.append(n)
        if len(shape) == 0: return data.ravel()[0]
        else: return data.reshape(shape)


class Swath(DictMixin, Autostr):
    @autostr
    def __init__(self, hdfeos, name):
        self.hdfeos = hdfeos
        self.name = name
        self.attributes = Attributes(self.hdfeos, self.name)
        self.maps = self.hdfeos._maps(self.name)

    @autostr
    def __getitem__(self, key):
        return Dataset(self.hdfeos, self.name, key)

    @autostr
    def keys(self):
        return self.hdfeos._list_geofields(self.name) + \
            self.hdfeos._list_datafields(self.name)

class SW(Autostr):
    @autostr
    def __init__(self, hdfeos, name):
        self.hdfeos = hdfeos
        self.name = name

    def __enter__(self):
        self.sw = SWattach(self.hdfeos.id, self.name)
        if self.sw == FAIL:
            raise KeyError(self._autostr(self.name))
        return self.sw

    def __exit__(self, exc_type, exc_value, traceback):
        res = SWdetach(self.sw)
        if res == -1:
            raise IOError(EIO, 'Failed to detach swath %d' %\
                          self.sw, os.fsdecode(self.hdfeos.filename))


class HDFEOS(DictMixin, Autostr):
    def __init__(self, filename, encoding='utf-8', mode=None):
        if mode not in (None, 'binary', 'text'):
            raise ValueError('mode must be one of: None, "binary", "text"')
        if mode is None:
            mode = 'text' if type(filename) is str else 'binary'
        self._mode = mode
        self._encoding = encoding
        filename = os.fsencode(filename)
        self.hdf = hdf.HDF(filename)
        self.filename = filename
        self.id = SWopen(filename, DFACC_RDONLY);
        if self.id == -1:
            raise IOError(EIO, 'Cannot open file', os.fsdecode(self.filename))
        self.attributes = Attributes(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.hdf.close()
        self.close()

    def close(self):
        SWclose(self.id)
        self.id = None

    @autostr
    def __getitem__(self, key):
        with SW(self, key) as sw: pass
        return Swath(self, key)

    def _list_swaths(self):
        cdef int32 strbufsize
        res = SWinqswath(self.filename, NULL, &strbufsize)
        if res == FAIL:
            raise IOError(EIO, 'SWinqswath failed', os.fsdecode(self.filename))
        cdef np.ndarray[char, ndim=1] tmp
        tmp = np.zeros(strbufsize + 1, dtype=np.byte)
        res = SWinqswath(self.filename, <char *>tmp.data, &strbufsize)
        if res == FAIL:
            raise IOError(EIO, 'SWinqswath failed', os.fsdecode(self.filename))
        swaths = bytes(bytearray(tmp)).rstrip(b'\0')
        return swaths.split(b',')

    def _list_geofields(self, swath):
        cdef int32 strbufsize
        cdef np.ndarray[char, ndim=1] tmp
        with SW(self, swath) as sw:
            res = SWnentries(sw, 3, &strbufsize)
            if res == FAIL:
                raise IOError(EIO, 'SWnentries failed', os.fsdecode(self.filename))
            tmp = np.zeros(strbufsize + 2, dtype=np.byte)
            res = SWinqgeofields(sw, <char *>tmp.data, NULL, NULL)
            if res == FAIL:
                raise IOError(EIO, 'SWinqgeofields failed', os.fsdecode(self.filename))
        geofields = bytes(bytearray(tmp)).rstrip(b'\0')
        return geofields.split(b',')

    def _list_datafields(self, swath):
        cdef int32 strbufsize
        cdef np.ndarray[char, ndim=1] tmp
        with SW(self, swath) as sw:
            res = SWnentries(sw, 4, &strbufsize)
            if res == FAIL:
                raise IOError(EIO, 'SWnentries failed', os.fsdecode(self.filename))
            tmp = np.zeros(strbufsize + 2, dtype=np.byte)
            res = SWinqdatafields(sw, <char *>tmp.data, NULL, NULL)
            if res == FAIL:
                raise IOError(EIO, 'SWinqdatafields failed', os.fsdecode(self.filename))
        datafields = bytes(bytearray(tmp)).rstrip(b'\0')
        return datafields.split(b',')

    def _maps(self, swath):
        cdef int32 strbufsize
        cdef np.ndarray[int32, ndim=1] offset
        cdef np.ndarray[int32, ndim=1] increment

        offset = np.zeros(H4_MAX_VAR_DIMS, dtype=np.int32)
        increment = np.zeros(H4_MAX_VAR_DIMS, dtype=np.int32)

        cdef np.ndarray[char, ndim=1] tmp

        with SW(self, swath) as sw:
            res = SWnentries(sw, 1, &strbufsize)
            if res == FAIL:
                raise IOError(EIO, 'SWnentries failed', os.fsdecode(self.filename))
            tmp = np.zeros(strbufsize + 2, dtype=np.byte)
            res = SWinqmaps(sw, <char *>tmp.data, <int32 *>offset.data, <int32 *> increment.data)
            if res == FAIL:
                raise IOError(EIO, 'SWinqmaps failed', os.fsdecode(self.filename))

        dimmap = bytes(bytearray(tmp)).rstrip(b'\0')

        n = 0
        maps = {}
        for dm in dimmap.split(b','):
            pair = dm.split(b'/')
            if len(pair) != 2 or not n < H4_MAX_VAR_DIMS: continue
            geofield, datafield = pair
            maps[(geofield, datafield)] = (offset[n], increment[n])
            n = n + 1

        return maps

    def _attributes(self, swath=None, dataset=None):
        cdef int32 strbufsize
        cdef np.ndarray[char, ndim=1] tmp

        with SW(self, swath) as sw:
            res = SWinqattrs(sw, NULL, &strbufsize)
            if res == FAIL:
                raise IOError(EIO, 'SWinqattrs failed', os.fsdecode(self.filename))

            tmp = np.zeros(strbufsize+1, dtype=np.byte)
            res = SWinqattrs(sw, <char *>tmp.data, &strbufsize)
            if res == FAIL:
                raise IOError(EIO, 'SWinqattrs failed', os.fsdecode(self.filename))

        attrlist = bytes(bytearray(tmp)).rstrip(b'\0')
        if attrlist == b'': return []
        attrlist = attrlist.split(b',')

        if dataset is None:
            return [attr for attr in attrlist if b'.' not in attr]
        else:
            attrs = []
            for attr in attrlist:
                if not attr.startswith(dataset): continue
                attrs.append(attr[len(dataset)+1:])
            return attrs

    def _getinfo(self, swath, name):
        cdef int32 rank, data_type
        cdef np.ndarray[int32, ndim=1] dims
        cdef np.ndarray[char, ndim=1] tmp

        dims = np.zeros(H4_MAX_VAR_DIMS, dtype=np.int32)
        tmp = np.zeros(FIELDNAMELENMAX*(H4_MAX_VAR_DIMS+2)*2, dtype=np.byte)

        with SW(self, swath) as sw:
            res = SWfieldinfo(sw, name, &rank, <int32 *>dims.data, &data_type, <char *>tmp.data)
        if res == FAIL: raise KeyError(self._autostr(name))
        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError('%s: %s: Data type %d not implemented'
                                              % (os.fsdecode(self.filename), self._autostr(name), data_type))

        dimlist = bytes(bytearray(tmp)).rstrip(b'\0')
        dimlist = dimlist.split(b',') if dimlist != b'' else []

        return {
            'shape': dims[:rank],
            'dtype': dtype,
            'dimlist': dimlist,
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

    def _read(self, swath, name, start, edges):
        info = self._getinfo(swath, name)
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
        with SW(self, swath) as sw:
            res = SWreadfield(sw, name, <int32 *>cstart.data, NULL, <int32 *>cedges.data, <void *>buf.data)
        data = buf.view(dtype=dtype).reshape(edges)
        return data

    def _readattr(self, swath, dataset, name):
        cdef int32 data_type, count
        attrname = name if dataset is None else b'%s.%s' % (dataset, name)

        with SW(self, swath) as sw:
            res = SWattrinfo(sw, attrname, &data_type, &count)
        if res == FAIL: raise KeyError(self._autostr(name))

        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError('%s: %s: Data type %d not implemented'
                                              % (os.fsdecode(self.filename), self._autostr(attrname), data_type))
        count = count/dtype().itemsize

        data = np.zeros(count, dtype=dtype)
        cdef np.ndarray[char, ndim=1] buf = data.view(dtype=np.int8).ravel()
        with SW(self, swath) as sw:
            res = SWreadattr(sw, attrname, <void *>buf.data)
        if res == FAIL:
            raise IOError(EIO, 'Cannot read attribute "%s"' % self._autostr(attrname),
                          os.fsdecode(self.filename))

        if data_type == DFNT_CHAR:
            return bytes(bytearray(data)).rstrip(b'\0')

        return data[0] if count == 1 else data

    @autostr
    def keys(self):
        return self._list_swaths()
