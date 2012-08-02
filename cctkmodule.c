#include <Python.h>
#include <numpy/arrayobject.h>

/*
 * Intrapolates values of a 2D array data with input y-coordinates
 * yin1d. yin1d is a 1-dimensional array. x dimension is preserved.
 * IMPORTANT: Both yin1d and yout1d are assumed to be monotonically increasing
 * with y. Each element of the output array out is set to the value of
 * the nearest element in the input array data.
 *
 * 	npy_float *data		- Input data 2D array.
 * 	npy_float *yin1d	- y-coordinates of data.
 * 	npy_float *yout1d	- y-coordinates of the output array.
 *	int xdim		- x dimension of data and out.
 *	int yindim		- y dimension of data and x or y dimension of yin1or2d.
 *	int youtdim		- y dimension of yout1d and out.
 *	npy_float *out		- Output 2D array.
 */
static void
lininty2d1(PyObject *data, PyObject *yin1d, PyObject *yout1d, PyObject *out)
{
	int i = 0, j = 0, k = 0, k0 = 0;
	npy_float *outbin = NULL, *bin1 = NULL, *bin2 = NULL;
	npy_float mindistance = INFINITY;
	npy_float dist = 0;
	int xdim = 0, yindim = 0, youtdim = 0;

	xdim = PyArray_DIMS(data)[0];
	yindim = PyArray_DIMS(data)[0];
	youtdim = PyArray_DIMS(yout1d)[0];

	for (j = 0, k0 = 0; j < youtdim; j++) {
		mindistance = INFINITY;
		bin1 = (npy_float *) PyArray_GETPTR1(yout1d, j);
		for (k = k0; k < yindim; k++) {
			bin2 = (npy_float *) PyArray_GETPTR1(yin1d, k);
			dist = *bin1 - *bin2;
			if (dist < 0) dist = -dist;
			if (dist < mindistance) {
				mindistance = dist;
				k0 = k;
			} else break; /* yin1d is monotonically inc. */
		}
		for (i = 0; i < xdim; i++) {
			outbin = (npy_float *) PyArray_GETPTR2(out, i, j);
			*outbin = *((npy_float *) PyArray_GETPTR2(data, i, k0));
		}
	}
}

/*
 * Intrapolates values of a 2D array data with input y-coordinates
 * yin2d. yin2d is a 2-dimensional array. x dimension is preserved.
 * IMPORTANT: Both yin2d and yout1d are assumed to be monotonically increasing
 * with y. Each element of the output array out is set to the value of
 * the nearest element in the input array data.
 *
 * 	npy_float *data		- Input data 2D array.
 * 	npy_float *yin2d	- y-coordinates of data.
 * 	npy_float *yout1d	- y-coordinates of the output array.
 *	int xdim		- x dimension of data and out.
 *	int yindim		- y dimension of data and x or y dimension of yin1or2d.
 *	int youtdim		- y dimension of yout1d and out.
 *	npy_float *out		- Output 2D array.
 */
static void
lininty2d2(PyObject *data, PyObject *yin2d, PyObject *yout1d, PyObject *out)
{
	npy_intp i = 0, j = 0, k = 0, k0 = 0;
	npy_float *outbin = NULL, *bin1 = NULL, *bin2 = NULL;
	npy_float mindistance = INFINITY;
	npy_float dist = 0;
	npy_intp xdim = 0, yindim = 0, youtdim = 0;

	xdim = PyArray_DIMS(data)[0];
	yindim = PyArray_DIMS(data)[1];
	youtdim = PyArray_DIMS(yout1d)[0];
	
	/*
	 * Iterate over the output array and find the nearest point
	 * in the input array.
	 */
	for (i = 0; i < xdim; i++) {
		for (j = 0, k0 = 0; j < youtdim; j++) {
			bin1 = (npy_float *) PyArray_GETPTR1(yout1d, j);

			mindistance = INFINITY;
			for (k = k0; k < yindim; k++) {
				bin2 = (npy_float *)
				    PyArray_GETPTR2(yin2d, i, k);
				dist = *bin1 - *bin2;
				if (dist < 0) dist = -dist;
				if (dist < mindistance) {
					mindistance = dist;
					k0 = k;
				} else break; /* yin2d is monotonically inc. */
			}
			outbin = (npy_float *) PyArray_GETPTR2(out, i, j);
			*outbin = *((npy_float *)
			    PyArray_GETPTR2(data, i, k0));
		}
	}
}

static PyObject *
cctk_lininty2d(PyObject *self, PyObject *args)
{
	PyObject *arg1 = NULL, *arg2 = NULL, *arg3 = NULL;
	PyObject *data = NULL, *yin1or2d = NULL, *yout1d = NULL;
	PyObject *out = NULL;
	npy_intp *dims1 = NULL, *dims2 = NULL, *dims3 = NULL;
	npy_intp dims4[2] = { 0, 0 };

	if (!PyArg_ParseTuple(args, "OOO", &arg1, &arg2, &arg3) ) {
		return NULL;
	}

	data = PyArray_FROM_OTF(arg1, NPY_FLOAT, NPY_IN_ARRAY);
	if (data == NULL) goto fail;
	yin1or2d = PyArray_FROM_OTF(arg2, NPY_FLOAT, NPY_IN_ARRAY);
	if (yin1or2d == NULL) goto fail;
	yout1d = PyArray_FROM_OTF(arg3, NPY_FLOAT, NPY_IN_ARRAY);
	if (yout1d == NULL) goto fail;

	if (PyArray_NDIM(data) != 2 ||
	    (PyArray_NDIM(yin1or2d) != 1 && PyArray_NDIM(yin1or2d) != 2) ||
	    PyArray_NDIM(yout1d) != 1) {
		PyErr_SetString(PyExc_ValueError, "Incorrect dimensions.");
		goto fail;
	}

	dims1 = PyArray_DIMS(data);
	dims2 = PyArray_DIMS(yin1or2d);
	dims3 = PyArray_DIMS(yout1d);

	/* We want to be flexible and support both 1D and 2D Y-coordinate. */
	if (PyArray_NDIM(yin1or2d) == 2) {
		if (	dims1[0] != dims2[0] ||
			dims1[1] != dims2[1]) {
			PyErr_SetString(PyExc_ValueError,
			    "Dimensions do not match");
			goto fail;
		}
	} else { /* PyArray_NDIM(yin1or2d) == 1 */
		if (dims1[1] != dims2[0]) {
			PyErr_SetString(PyExc_ValueError,
			    "Dimensions do not match");
			goto fail;
		}		
	}
	dims4[0] = dims1[0]; dims4[1] = dims3[0];
	out = PyArray_ZEROS(2, dims4, NPY_FLOAT, 0);
	if (out == NULL) goto fail;
	
	/* Core function call. */
	if (PyArray_NDIM(yin1or2d) == 2)
		lininty2d2(data, yin1or2d, yout1d, out);
	else /* PyArray_NDIM(yin1or2d) == 1 */
		lininty2d1(data, yin1or2d, yout1d, out);

	Py_DECREF(data);
	Py_DECREF(yin1or2d);
	Py_DECREF(yout1d);
	return out;
fail:
	Py_XDECREF(data);
	Py_XDECREF(yin1or2d);
	Py_XDECREF(yout1d);
	Py_XDECREF(out);
	return NULL;
}

static void
dimmap2d(PyObject *data, PyObject *out, int off1, int inc1, int off2, int inc2)
{
	npy_intp i = 0, j = 0;
	npy_intp k0 = 0, k1 = 0, l0 = 0, l1 = 0;
	float fk = 0.f, fl = 0.f, dk = 0.f, dl = 0.f;
	npy_intp xdim = 0, ydim = 0, xoutdim = 0, youtdim = 0;
	npy_float *outbin = NULL;
	npy_float *b1 = NULL, *b2 = NULL, *b3 = NULL, *b4 = NULL;

	xdim = PyArray_DIMS(data)[0];
	ydim = PyArray_DIMS(data)[1];
	xoutdim = PyArray_DIMS(out)[0];
	youtdim = PyArray_DIMS(out)[1];

	for (i = 0; i < xoutdim; i++) {
		for (j = 0; j < youtdim; j++) {
			fk = (i - off1)/(float)(inc1);
			fl = (j - off2)/(float)(inc2);

			k0 = (int) fk;
			l0 = (int) fl;

			k1 = k0 + 1;
			l1 = l0 + 1;

			dk = fk - k0;
			dl = fl - l0;

			/* Prevent integer overflow and ensure correct
			 * behavior on boundaries. */
			if (k0 < 0) k0 = 0;
			if (l0 < 0) l0 = 0;
			if (k1 < 0) k1 = 0;
			if (l1 < 0) l1 = 0;
			if (k0 >= xdim) k0 = xdim-1;
			if (l0 >= ydim) l0 = ydim-1;
			if (k1 >= xdim) k1 = xdim-1;
			if (l1 >= ydim) l1 = ydim-1;
			outbin = PyArray_GETPTR2(out, i, j);
			b1 = PyArray_GETPTR2(data, k0, l0);
			b2 = PyArray_GETPTR2(data, k0, l1);
			b3 = PyArray_GETPTR2(data, k1, l0);
			b4 = PyArray_GETPTR2(data, k1, l1);
			*outbin = *b1 * (1-dk)*(1-dl) +
				  *b2 * (1-dk)* dl +
				  *b3 *    dk *(1-dl) +
				  *b4 *    dk * dl; 
		}
	}
}

static PyObject *
cctk_dimmap2d(PyObject *self, PyObject *args)
{
	PyObject *arg1 = NULL;
	PyObject *data = NULL;
	int off1, inc1, off2, inc2;
	PyObject *out = NULL;

	npy_intp *dims;
	npy_intp outdims[2] = { 0, 0 };

	if (!PyArg_ParseTuple(args, "Oiiii", &arg1, &off1, &inc1, &off2,
	    &inc2) ) {
		return NULL;
	}

	data = PyArray_FROM_OTF(arg1, NPY_FLOAT, NPY_IN_ARRAY);
	if (data == NULL) goto fail;
	
	if (PyArray_NDIM(data) != 2) {
		PyErr_SetString(PyExc_ValueError, "Incorrect dimensions");
		goto fail;
	}

	if (inc1 <= 0 || inc2 <= 0) {
		PyErr_SetString(PyExc_ValueError, "Invalid increment");
		goto fail;
	}

	dims = PyArray_DIMS(data);
	/* This can overflow. */
	outdims[0] = dims[0]*inc1;
	outdims[1] = dims[1]*inc2;

	out = PyArray_ZEROS(2, outdims, NPY_FLOAT, 0);
	if (out == NULL) goto fail;
	
	/* Core function call. */
	dimmap2d(data, out, off1, inc1, off2, inc2);

	Py_DECREF(data);
	return out;
fail:
	Py_XDECREF(data);
	Py_XDECREF(out);
	return NULL;	
}

static PyObject *
linint2d(PyObject *data, PyObject *xin2d, PyObject *yin2d, PyObject *out,
    float xout1, float xout2, float yout1, float yout2,
    float fill, int radiusx, int radiusy)
{
	npy_intp i, j, k, l, kp, lq;
	int p, q;
	npy_intp xdim, ydim, xoutn, youtn;
	npy_float x, y;
	float kf, lf;
	npy_float *bin = NULL;
	npy_float *outbin = NULL, *coefbin = NULL;
	PyObject *coefa;
	float coef;
	
	xdim = PyArray_DIMS(data)[0];
	ydim = PyArray_DIMS(data)[1];
	xoutn = PyArray_DIMS(out)[0];
	youtn = PyArray_DIMS(out)[1];

	coefa = PyArray_ZEROS(2, PyArray_DIMS(out), NPY_FLOAT, 0);
	if (coefa == NULL) return NULL;

	for (i = 0; i < xdim; i++) {
		for (j = 0; j < ydim; j++) {
			bin = PyArray_GETPTR2(data, i, j);
			if (isnan(*bin)) continue;
			x = *((npy_float *) PyArray_GETPTR2(xin2d, i, j));
			y = *((npy_float *) PyArray_GETPTR2(yin2d, i, j));
			
			kf = (x - xout1) / (xout2 - xout1) * xoutn;
			lf = (y - yout1) / (yout2 - yout1) * youtn;
			k = kf > 0.f ? kf+0.5 : kf-1.f;
			l = lf > 0.f ? lf+0.5 : lf-1.f;

			for (p = -radiusx; p <= radiusx; p++) {
				for (q = -radiusy; q <= radiusy; q++) {
					kp = k+p, lq = l+q;
					if (kp < 0 || lq < 0 ||
					    kp >= xoutn || lq >= youtn)
						continue;
					outbin = PyArray_GETPTR2(out,kp,lq);
					coefbin= PyArray_GETPTR2(coefa,kp,lq);
					coef= 1.f /
					    ((kp-kf)*(kp-kf)+(lq-lf)*(lq-lf));
					//coef = pow(10, -((kp-kf)*(kp-kf)+(lq-lf)*(lq-lf)));
					*outbin += (*bin)*coef;
					*coefbin += coef;
			
				}
			}
		}
	}

	for (i = 0; i < xoutn; i++) {
		for (j = 0; j < youtn; j++) {
			outbin = PyArray_GETPTR2(out, i, j);
			coefbin = PyArray_GETPTR2(coefa, i, j);
			*outbin = (*coefbin != 0.f) ? *outbin/(*coefbin) : fill;
		}
	}

	Py_DECREF(coefa);

	return out;
}

static PyObject *
cctk_linint2d(PyObject *self, PyObject *args)
{
	PyObject *arg1 = NULL, *arg2 = NULL, *arg3 = NULL;
	PyObject *data = NULL, *xin2d = NULL, *yin2d = NULL;
	float xout1, xout2, yout1, yout2;
	int xoutn, youtn;
	PyObject *out = NULL;
	float fill;
	int radiusx, radiusy;

	npy_intp *dims1 = NULL, *dims2 = NULL, *dims3 = NULL;
	npy_intp outdims[2] = { 0, 0 };

	if (!PyArg_ParseTuple(args, "OOO(ffi)(ffi)fii", &arg1, &arg2, &arg3,
	    &xout1, &xout2, &xoutn, &yout1, &yout2, &youtn, &fill,
	    &radiusx, &radiusy)) {
		return NULL;
	}

	data = PyArray_FROM_OTF(arg1, NPY_FLOAT, NPY_IN_ARRAY);
	if (data == NULL) goto fail;

	xin2d = PyArray_FROM_OTF(arg2, NPY_FLOAT, NPY_IN_ARRAY);
	if (xin2d == NULL) goto fail;

	yin2d = PyArray_FROM_OTF(arg3, NPY_FLOAT, NPY_IN_ARRAY);
	if (yin2d == NULL) goto fail;

	if (PyArray_NDIM(data) != 2 || PyArray_NDIM(xin2d) != 2 ||
	    PyArray_NDIM(yin2d) != 2) {
		PyErr_SetString(PyExc_ValueError, "Incorrect dimensions.");
		goto fail;
	}

	dims1 = PyArray_DIMS(data);
	dims2 = PyArray_DIMS(xin2d);
	dims3 = PyArray_DIMS(yin2d);

	if (dims2[0] != dims1[0] || dims2[1] != dims1[1] ||
	    dims3[0] != dims1[0] || dims3[1] != dims1[1]) {
		PyErr_SetString(PyExc_ValueError, "Dimensions do not match");
		goto fail;
	}

	outdims[0] = xoutn;
	outdims[1] = youtn;

	out = PyArray_ZEROS(2, outdims, NPY_FLOAT, 0);
	if (out == NULL) goto fail;
	
	/* Core function call. */
	out = linint2d(data, xin2d, yin2d, out, xout1, xout2, yout1, yout2,
	    fill, radiusx, radiusy);

	Py_DECREF(data);
	Py_DECREF(xin2d);
	Py_DECREF(yin2d);
	return out;
fail:
	Py_XDECREF(data);
	Py_XDECREF(xin2d);
	Py_XDECREF(yin2d);
	Py_XDECREF(out);
	return NULL;
}

static PyMethodDef CCTKMethods[] = {
	{ "lininty2d", cctk_lininty2d, METH_VARARGS,
	    "Intrapolate y-coordinate values of a 2D array." },
	{ "linint2d", cctk_linint2d, METH_VARARGS,
	    "Linearly interpolate values of a 2D array on a rectilinear grid."},
	{ "dimmap2d", cctk_dimmap2d, METH_VARARGS,
	    "Map dimensions by linear interpolation." },
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initcctk(void)
{
	(void) Py_InitModule("cctk", CCTKMethods);
	import_array();

}

