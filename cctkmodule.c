/* cctkmodule.c
 * This file is a part of ccplot: a CloudSat and CALIPSO plotting tool.
 *
 * Copyright (c) 2009 Peter Kuma
 *
 * This software is provided under the terms of a 2-clause BSD licence:
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 *  1. Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer
 *     in the documentation and/or other materials provided with
 *     the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE CCPLOT PROJECT ``AS IS'' AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL THE CCPLOT PROJECT OR CONTRIBUTORS BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
 * USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
 */

#include <Python.h>
#include <numpy/arrayobject.h>

static void
dimmap2d(PyObject *data, PyObject *out, int off1, int inc1, int off2, int inc2,
float modulus)
{
	npy_intp i = 0, j = 0;
	npy_intp k0 = 0, k1 = 0, l0 = 0, l1 = 0;
	float fk = 0.f, fl = 0.f, dk = 0.f, dl = 0.f;
	npy_intp xdim = 0, ydim = 0, xoutdim = 0, youtdim = 0;
	npy_float *outbin = NULL;
	npy_float *b1 = NULL, *b2 = NULL, *b3 = NULL, *b4 = NULL;
	float br1, br2, br3, br4;

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
			
			br1 = 0.f;
			br2 = remainderf(*b2 - *b1, modulus);
			br3 = remainderf(*b3 - *b1, modulus);
			br4 = remainderf(*b4 - *b1, modulus);
			
			*outbin = *b1 + (
			    br1 * (1-dk)*(1-dl) +
			    br2 * (1-dk)* dl +
			    br3 *    dk *(1-dl) +
			    br4 *    dk * dl);
		}
	}
}

static PyObject *
cctk_dimmap2d(PyObject *self, PyObject *args)
{
	PyObject *arg1 = NULL;
	PyObject *data = NULL;
	int off1, inc1, off2, inc2;
	float modulus;
	PyObject *out = NULL;

	npy_intp *dims;
	npy_intp outdims[2] = { 0, 0 };

	if (!PyArg_ParseTuple(args, "Oiiiif", &arg1, &off1, &inc1, &off2,
	    &inc2, &modulus) ) {
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

	if (outdims[0] < 0 || outdims[1] < 0) {
		PyErr_SetString(PyExc_ValueError, "Negative output size");
		goto fail;
	}

	out = PyArray_ZEROS(2, outdims, NPY_FLOAT, 0);
	if (out == NULL) goto fail;
	
	/* Core function call. */
	dimmap2d(data, out, off1, inc1, off2, inc2, modulus);

	Py_DECREF(data);
	return out;
fail:
	Py_XDECREF(data);
	Py_XDECREF(out);
	return NULL;	
}

static PyObject *
interpolate2d(PyObject *data, PyObject *xin2d, PyObject *yin2d, PyObject *out,
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
	
	for (i = 0; i < xoutn; i++) {
		for (j = 0; j < youtn; j++) {
			bin = PyArray_GETPTR2(coefa, i, j);
			*bin = INFINITY;
			outbin = PyArray_GETPTR2(out, i, j);
			*outbin = fill;
		}
	}
	
	for (i = 0; i < xdim; i++) {
		for (j = 0; j < ydim; j++) {
			bin = PyArray_GETPTR2(data, i, j);
			if (isnan(*bin)) continue;
			x = *((npy_float *) PyArray_GETPTR2(xin2d, i, j));
			y = *((npy_float *) PyArray_GETPTR2(yin2d, i, j));
			
			kf = (x - xout1) / (xout2 - xout1) * xoutn;
			lf = (y - yout1) / (yout2 - yout1) * youtn;
			k = lroundf(kf);
			l = lroundf(lf);

			for (p = -radiusx; p <= radiusx; p++) {
				for (q = -radiusy; q <= radiusy; q++) {
					kp = k+p, lq = l+q;
					if (kp < 0 || lq < 0 ||
					    kp >= xoutn || lq >= youtn)
						continue;
					outbin = PyArray_GETPTR2(out,kp,lq);
					coefbin= PyArray_GETPTR2(coefa,kp,lq);
					/*
					coef = 1.f /
					    ((kp-kf)*(kp-kf)+(lq-lf)*(lq-lf));
					coef = pow(10, -((kp-kf)*(kp-kf)+(lq-lf)*(lq-lf)));
					*outbin += (*bin)*coef;
					*coefbin += coef;
					*/
					coef = (kp-kf)*(kp-kf)+(lq-lf)*(lq-lf);
					if (coef < *coefbin) {
						*coefbin = coef;
						*outbin = *bin;
					}
				}
			}
		}
	}

	/*
	for (i = 0; i < xoutn; i++) {
		for (j = 0; j < youtn; j++) {
			outbin = PyArray_GETPTR2(out, i, j);
			coefbin = PyArray_GETPTR2(coefa, i, j);
			*outbin = (*coefbin != 0.f) ? *outbin/(*coefbin) : fill;
		}
	}
	*/

	Py_DECREF(coefa);

	return out;
}

static PyObject *
cctk_interpolate2d(PyObject *self, PyObject *args)
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

	if (outdims[0] < 0 || outdims[1] < 0) {
		PyErr_SetString(PyExc_ValueError, "Negative output size");
		goto fail;
	}

	out = PyArray_ZEROS(2, outdims, NPY_FLOAT, 0);
	if (out == NULL) goto fail;
	
	/* Core function call. */
	out = interpolate2d(data, xin2d, yin2d, out, xout1, xout2, yout1, yout2,
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

/*
 * Performs mapping of CALIPSO layer data onto a regular grid.
 *
 * Arguments:
 *	PyObject *data		-- 2D numpy float array
 *	PyObject *nlayer	-- 1D numpy uint8 array storing number of layers
 *				   for each ray
 *	PyObject *basealt	-- 2D numpy float array storing base altitude
 *				   for earch ray and layer
 *	PyObject *topalt	-- 2D numpy float array storing top altitude
 *				   for earch ray and layer
 *	PyObject *out		-- output grid; 2D numpy float array
 *	float y0		-- altitude corresponding to the bottom of out
 *	float ym		-- altitude corresponding to the top of out
 *	float fill		-- background fill value
 *
 * Returns:
 * 	Returns a 2D numpy array, the same as out.
 */
static PyObject *
layermap(PyObject *data, PyObject *nlayer, PyObject *basealt,
    PyObject *topalt, PyObject *out, float y0, float ym, float fill)
{
	npy_intp i, j, k;
	npy_intp n, m, nlayer_max;
	npy_float *bin = NULL, *outbin = NULL;
	npy_uint8 nlayer_i;
	npy_float yb, yt;
	npy_float alt2y_ratio;
	npy_float pf, qf;
	npy_intp p, q;
	
	n = PyArray_DIMS(out)[0];
	m = PyArray_DIMS(out)[1];
	nlayer_max = PyArray_DIMS(data)[1];

	alt2y_ratio = m/(ym - y0);

	/* Fill output with a value of fill. */
	for (i = 0; i < n; i++) {
		for (j = 0; j < m; j++) {
			bin = PyArray_GETPTR2(out, i, j);
			*bin = fill;
		}
	}

	/* Iterate over layers and fill out. */
	for (i = 0; i < n; i++) {
		nlayer_i = *((npy_uint8 *) PyArray_GETPTR1(nlayer, i));
		for (j = 0; j < nlayer_i && j < nlayer_max; j++) {
			bin = PyArray_GETPTR2(basealt, i, j);
			yb = *bin;
			bin = PyArray_GETPTR2(topalt, i, j);
			yt = *bin;
			pf = (yb - y0) * alt2y_ratio;
			qf = (yt - y0) * alt2y_ratio;
			p = lroundf(pf);
			q = lroundf(qf);
			if (p < 0) p = 0;
			if (q > m) q = m;
			for (k = p; k < q; k++) {
				bin = PyArray_GETPTR2(data, i, j);
				outbin = PyArray_GETPTR2(out, i, k);
				*outbin = *bin;
			}
		}
	}
	
	return out;
}

static PyObject *
cctk_layermap(PyObject *self, PyObject *args)
{
	PyObject *arg1 = NULL, *arg2 = NULL, *arg3 = NULL, *arg4 = NULL;
	PyObject *data = NULL, *nlayer = NULL, *basealt = NULL, *topalt = NULL;
	PyObject *out = NULL;
	float yout1, yout2;
	int youtn;
	float fill;

	npy_intp *dims1 = NULL, *dims2 = NULL, *dims3 = NULL, *dims4 = NULL;
	npy_intp outdims[2] = { 0, 0 };

	if (!PyArg_ParseTuple(args, "OOOO(ffi)f", &arg1, &arg2, &arg3, &arg4,
	    &yout1, &yout2, &youtn, &fill)) {
		return NULL;
	}

	data = PyArray_FROM_OTF(arg1, NPY_FLOAT, NPY_IN_ARRAY);
	if (data == NULL) goto fail;

	nlayer = PyArray_FROM_OTF(arg2, NPY_UINT8, NPY_IN_ARRAY);
	if (nlayer == NULL) goto fail;

	basealt = PyArray_FROM_OTF(arg3, NPY_FLOAT, NPY_IN_ARRAY);
	if (basealt == NULL) goto fail;

	topalt = PyArray_FROM_OTF(arg4, NPY_FLOAT, NPY_IN_ARRAY);
	if (topalt == NULL) goto fail;

	if (PyArray_NDIM(data) != 2 || PyArray_NDIM(nlayer) != 1 ||
	    PyArray_NDIM(basealt) != 2 || PyArray_NDIM(topalt) != 2) {
		PyErr_SetString(PyExc_ValueError, "Incorrect dimensions.");
		goto fail;
	}

	dims1 = PyArray_DIMS(data);
	dims2 = PyArray_DIMS(nlayer);
	dims3 = PyArray_DIMS(basealt);
	dims4 = PyArray_DIMS(topalt);

	if (dims3[0] != dims1[0] || dims3[1] != dims1[1] ||
	    dims4[0] != dims1[0] || dims4[1] != dims1[1] ||
	    dims2[0] != dims1[0]) {
		PyErr_SetString(PyExc_ValueError, "Dimensions do not match");
		goto fail;
	}

	outdims[0] = dims1[0];
	outdims[1] = youtn;

	if (outdims[0] < 0 || outdims[1] < 0) {
		PyErr_SetString(PyExc_ValueError, "Negative output size");
		goto fail;
	}

	out = PyArray_ZEROS(2, outdims, NPY_FLOAT, 0);
	if (out == NULL) goto fail;

	/* Core function call. */
	out = layermap(data, nlayer, basealt, topalt, out, yout1, yout2, fill);

	Py_DECREF(data);
	Py_DECREF(nlayer);
	Py_DECREF(basealt);
	Py_DECREF(topalt);
	return out;
fail:
	Py_XDECREF(data);
	Py_XDECREF(nlayer);
	Py_XDECREF(basealt);
	Py_XDECREF(topalt);
	Py_XDECREF(out);
	return NULL;
}

static PyMethodDef CCTKMethods[] = {
	{ "interpolate2d", cctk_interpolate2d, METH_VARARGS,
	    "Linearly interpolate values of a 2D array on a regular grid."},
	{ "dimmap2d", cctk_dimmap2d, METH_VARARGS,
	    "Map dimensions by linear interpolation." },
	{ "layermap", cctk_layermap, METH_VARARGS,
	    "Map a layer product onto a two-dimensional regular grid." },
	{ NULL, NULL, 0, NULL }
};

PyMODINIT_FUNC
initcctk(void)
{
	(void) Py_InitModule("cctk", CCTKMethods);
	import_array();

}

