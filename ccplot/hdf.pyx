cimport cython
cimport numpy as np
import sys
import os
import numpy as np
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

cdef extern from "mfhdf.h":
    cdef enum:
        FAIL = -1
        DFACC_READ = 1
        H4_MAX_VAR_DIMS = 32
        FIELDNAMELENMAX = 128
        VSNAMELENMAX = 64
        FULL_INTERLACE = 0

    ctypedef np.npy_uint8 uint8
    ctypedef np.npy_int8 int8
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

    int32 Hopen(char *, intn, int16)
    intn Vstart(int32)
    int32 VSattach(int32, int32, char *)
    int32 VSdetach(int32)
    intn Vend(int32 file_id)
    intn Hclose(int32 file_id)
    intn VSinquire(int32, int32 *, int32 *, char *, int32 *, char *)
    int32 VSfind(int32, char *)
    intn VSsetfields(int32, char *)
    int32 VSread(int32, uint8 *, int32, int32)
    int32 VSgetname(int32, char *)
    int32 VSgetid(int32, int32)
    int32 VSgetclass(int32, char *)
    int32 VSsizeof(int32 vdata_id, char *field_name_list)
    intn VSfpack(int32, intn, char *, VOIDP, intn, intn,char *, VOIDP)
    int32 VFfieldtype(int32, int32)
    intn VSfindex(int32, char *, int32 *)
    char *VFfieldname(int32, int32)
    int32 VFnfields(int32)

cdef extern from "vg.h":
    cdef enum:
        _HDF_VSUNPACK = 1

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
    def __init__(self, hdf, dataset=None):
        self.hdf = hdf
        self.dataset = dataset

    @autostr
    def __getitem__(self, key):
        return self.hdf._readattr(self.dataset, key)

    @autostr
    def keys(self):
        return self.hdf._attributes(self.dataset)


class Dataset(Autostr):
    @autostr
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name
        info = self.hdf._getinfo(name)
        self.shape = info['shape']
        self.rank = len(self.shape)
        self.attributes = Attributes(self.hdf, name)

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

        data = self.hdf._read(self.name, starta, edgesa)
        shape = []
        for n, d in zip(data.shape, dims):
            if d: shape.append(n)
        if len(shape) == 0: return data.ravel()[0]
        else: return data.reshape(shape)


class Vdata(DictMixin, Autostr):
    @autostr
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name
        # Ensure that such Vdata exists.
        self.fields = self.hdf._vdata_fields(name)

    @autostr
    def __getitem__(self, key):
        data = self.hdf._read_vdata(self.name, key)
        if type(data) == np.ndarray and len(data) == 1:
            return data[0]
        return data

    @autostr
    def keys(self):
        return self.fields


class SDS(Autostr):
    @autostr
    def __init__(self, hdf, name):
        self.hdf = hdf
        self.name = name

    def __enter__(self):
        errno = 0
        index = SDnametoindex(self.hdf.sd, self.name)
        if index == FAIL: raise KeyError(self._autostr(self.name))
        self.sds = SDselect(self.hdf.sd, index)
        if self.sds == FAIL:
            self.hdf._error('HDF: SDselect of dataset "%s" failed' % self.name)
        return self.sds

    def __exit__(self, exc_type, exc_value, traceback):
        SDendaccess(self.sds)


class HDF(DictMixin, Autostr):
    def __init__(self, filename, encoding='utf-8', mode=None):
        if mode not in (None, 'binary', 'text'):
            raise ValueError('mode must be one of: None, "binary", "text"')
        if mode is None:
            mode = 'text' if type(filename) is str else 'binary'
        self._mode = mode
        self._encoding = encoding
        filename = os.fsencode(filename)
        self.filename = filename

        self.sd = SDstart(filename, DFACC_READ)
        if self.sd == FAIL: self._error('HDF: SDstart failed', from_errno=True)

        self.hd = Hopen(filename, DFACC_READ, 0)
        if self.hd == FAIL: self._error('HDF: Hopen failed', from_errno=True)

        res = Vstart(self.hd)
        if res == FAIL: self._error('HDF: Vstart failed', from_errno=True)

        self.attributes = Attributes(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        SDend(self.sd)
        self.sd = None
        Vend(self.hd)
        Hclose(self.hd)
        self.hd = None

    @autostr
    def __getitem__(self, key):
        # Try SDS.
        try:
            with SDS(self, key) as sds: pass
            return Dataset(self, key)
        except KeyError: pass

        # Try Vdata.
        try:
            return Vdata(self, key)
        except KeyError: pass

        raise KeyError(self._autostr(key))

    @autostr
    def keys(self):
        return self._list_datasets() + self._list_vdata()

    def _list_datasets(self):
        cdef int32 rank, data_type, num_datasets, num_global_attrs, num_attrs
        cdef np.ndarray[int32, ndim=1] dims
        cdef np.ndarray[char, ndim=1] tmp

        dims = np.zeros(H4_MAX_VAR_DIMS, dtype=np.int32)

        res = SDfileinfo(self.sd, &num_datasets, &num_global_attrs)
        if res == FAIL: self._error('HDF: SDfileinfo failed')

        datasets = []
        for i in range(num_datasets):
            tmp = np.zeros(FIELDNAMELENMAX, dtype=np.byte)
            sds = SDselect(self.sd, i)
            res = SDgetinfo(sds, <char *>tmp.data, &rank, <int32 *>dims.data, &data_type, &num_attrs)
            if res == FAIL: self._error('HDF: SDgetinfo failed')
            sds_name = bytes(bytearray(tmp)).rstrip(b'\0')
            datasets.append(sds_name)
        return datasets

    def _list_vdata(self):
        """Return a list of pure Vdata elements."""
        cdef char[VSNAMELENMAX] tmp
        out = []
        ref = VSgetid(self.hd, -1)
        while ref != FAIL:
            id = VSattach(self.hd, ref, 'r')
            if id == FAIL: self._error('HDF: VSattach failed')
            try:
                res = VSgetname(id, tmp)
                if res == FAIL: self._error('HDF: VSgetname failed')
                name = tmp
                res = VSgetclass(id, tmp)
                if res == FAIL: self._error('HDF: VSgetclass failed')
                vdata_class = tmp
                if len(vdata_class) == 0 and len(name) > 0:
                    out.append(name)
            finally:
                res = VSdetach(id)
                if res == FAIL: self._error('HDF: VSdetach failed')
            ref = VSgetid(self.hd, ref)
        return out

    def _error(self, errmsg=None, from_errno=False):
        errcode = HEvalue(1)
        if errcode != 0:
            msg = '%s: %s' % (errmsg, autostr(HEstring(errcode)))
            raise IOError(errcode, msg, os.fsdecode(self.filename))
        elif errno != 0 and from_errno:
            raise IOError(errno, autostr(strerror(errno)), os.fsdecode(self.filename))
        elif errmsg is not None:
            raise IOError(0, errmsg, os.fsdecode(self.filename))
        else:
            raise IOError(0, 'HDF: Unknown error', os.fsdecode(self.filename))

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
            attr_name = bytes(bytearray(tmp)).rstrip(b'\0')
            attrs.append(attr_name)
        return attrs

    def _getinfo(self, name):
        cdef int32 rank, data_type, num_attrs
        cdef np.ndarray[int32, ndim=1] dims
        dims = np.zeros(H4_MAX_VAR_DIMS, dtype=np.int32)
        with SDS(self, name) as sds:
            res = SDgetinfo(sds, NULL, &rank, <int32 *>dims.data, &data_type, &num_attrs)
        if res == FAIL: self._error('HDF: SDgetinfo on dataset "%s" failed' % name)
        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError('%s: %s: Data type %d not implemented'
                                              % (os.fsdecode(self.filename), self._autostr(name), data_type))
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
        if index == FAIL: raise KeyError(self._autostr(name))
        cdef np.ndarray[char, ndim=1] tmp
        tmp = np.zeros(FIELDNAMELENMAX, dtype=np.byte)
        res = SDattrinfo(obj_id, index, <char *>tmp.data, &data_type, &count)
        if res == FAIL:
            self._error('HDF: SDattrinfo of "%s" failed' % name)

        try: dtype = DTYPE[data_type]
        except KeyError: raise NotImplementedError(
            '%s: %s: Data type %d not implemented' %\
            (os.fsdecode(self.filename), self._autostr(name), data_type))

        data = np.zeros(count, dtype=dtype)
        cdef np.ndarray[char, ndim=1] buf = data.view(dtype=np.int8).ravel()
        res = SDreadattr(obj_id, index, <void *>buf.data);
        if res == FAIL:
            self._error('HDF: SDreadattr of "%s" failed' % name)

        if data_type == DFNT_CHAR:
            return bytes(bytearray(data)).rstrip(b'\0')

        return data[0] if count == 1 else data

    def _read_vdata(self, vdata, name):
        cdef int32 n_records
        cdef np.ndarray[uint8, ndim=1] buf, data
        cdef int32 index

        ref = VSfind(self.hd, vdata)
        if ref == 0: raise KeyError(self._autostr(vdata))
        id = VSattach(self.hd, ref, 'r')
        if id == FAIL: self._error('HDF: VSattach of "%s" failed' % vdata)
        try:
            res = VSinquire(id, &n_records, NULL, NULL, NULL, NULL)
            if res == FAIL: self._error('HDF: VSinquire failed')

            res = VSsetfields(id, name)
            if res == FAIL: raise KeyError(self._autostr(name))

            size = VSsizeof(id, name)
            if size == FAIL: self._error('HDF: VSsizeof failed')

            buf = np.zeros(size*n_records, dtype=np.uint8)
            res = VSread(id, <uint8 *>buf.data, n_records, FULL_INTERLACE)
            data = buf

            # Find out field type.
            res = VSfindex(id, name, &index)
            if res == FAIL: self._error('HDF: VSfindex failed')
            data_type = VFfieldtype(id, index)
            if data_type == FAIL: self._error('HDF: VFfieldtype failed')
            try:
                dtype = DTYPE[data_type]
            except KeyError:
                raise NotImplementedError(
                    '%s: %s: %s: Data type %d not implemented' %
                    (os.fsdecode(self.filename), self._autostr(vdata), self._autostr(name), data_type)
                )

            if data_type == DFNT_CHAR:
                return bytes(bytearray(data)).rstrip(b'\0')
            else:
                return data.view(dtype=dtype)

        finally:
            res = VSdetach(id)
            if res == FAIL: self._error('HDF: VSdetach failed')

    def _vdata_fields(self, name):
        cdef char *tmp
        fields = []
        ref = VSfind(self.hd, name)
        if ref == 0: raise KeyError(self._autostr(name))
        id = VSattach(self.hd, ref, 'r')
        if id == FAIL: self._error('HDF: VSattach of "%s" failed' % self._autostr(name))
        try:
            nfields = VFnfields(id)
            if nfields == FAIL: self._error('HDF: VFnfields failed')
            for index in range(nfields):
                tmp = VFfieldname(id, index)
                if tmp == NULL: self._error('HDF: VFfieldname failed')
                name = tmp
                fields.append(name)
        finally:
            res = VSdetach(id)
            if res == FAIL: self._error('HDF: VSdetach failed')
        return fields
