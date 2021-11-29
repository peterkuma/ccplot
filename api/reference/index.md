---
layout: default
title: API reference
---
API reference
=============

ccplot.hdf
----------

### class HDF(filename, encoding='utf-8', mode=None)

This is a class for reading HDF files. The class supports reading
of:

* datasets (SDS)
* attributes
* VData

The constructor accepts a filename, text encoding and mode. Mode signifies
if the file should be opened in a binary or text mode: None (automatic),
`binary` (binary mode) or `text` (text mode). If mode is None, it is equivalent
to `binary` if the type of filename is bytes and `text` if the type is str.

{% highlight python %}
from ccplot.hdf import HDF
product = HDF('CAL_LID_L1-ValStage1-V3-02.2013-01-01T11-55-23ZN.hdf')
{% endhighlight %}

The file can be closed with **HDF.close()**, or by using the Context Manager
interface:

{% highlight python %}
with HDF('CAL_LID_L1-ValStage1-V3-02.2013-01-01T11-55-23ZN.hdf') as product:
    # Work with the file.
{% endhighlight %}

#### Reading datasets and Vdata

Datasets and Vdata are accessible as dictionary items of the HDF class instance:

{% highlight python %}
lat = product['Latitude']
print(lat[0])
--> [ 72.14601898]
metadata = product['metadata']
print(metadata['Product_ID'])
--> L1_LIDAR_Science
{% endhighlight %}

When accessing datasets, an instance of **Dataset** class is returned.
This instance is turned into a numpy array on index subsetting:

{% highlight python %}
type(lat)
--> <class 'ccplot.hdf.Dataset'>
type(lat[::])
--> <type 'numpy.ndarray'>
{% endhighlight %}

#### Listing datasets

A list of datasets can retrieved with **HDF.keys()**:

{% highlight python %}
print('\n'.join(product.keys()))
--> Profile_Time
    Profile_UTC_Time
    Profile_ID
    Land_Water_Mask
    [...]
    Subsolar_Longitude
    metadata
{% endhighlight %}

#### Attributes

File and dataset attributes are accessible as **HDF.attributes** and
**Dataset.attributes**, respectively:

{% highlight python %}
print(dict(lat.attributes))
--> {'units': 'degrees', 'valid_range': '-90.0 ... 90.0', 'fillvalue': -9999.0, 'format': 'Float_32'}
print(product.attributes.keys())
--> ['coremetadata', 'archivemetadata']
print(product.attributes['coremetadata'])
--> GROUP                  = INVENTORYMETADATA
    [...]
    END_GROUP              = INVENTORYMETADATA

    END
{% endhighlight %}

ccplot.hdfeos
-------------

### class HDFEOS(filename, encoding='utf-8', mode=None)

This is a class for reading HDFEOS-2 files. The class supports reading
of:

* swaths
* datasets
* attributes

The constructor accepts a filename, text encoding and mode. Mode signifies
if the file should be opened in a binary or text mode: None (automatic),
`binary` (binary mode) or `text` (text mode). If mode is None, it is equivalent
to `binary` if the type of filename is bytes and `text` if the type is str.

{% highlight python %}
from ccplot.hdfeos import HDFEOS
product = HDFEOS('2013119200420_37263_CS_2B-GEOPROF_GRANULE_P_R04_E06.hdf')
{% endhighlight %}

The file can be closed with **HDFEOS.close()**, or by using the Context Manager
interface:

{% highlight python %}
with HDFEOS('2013119200420_37263_CS_2B-GEOPROF_GRANULE_P_R04_E06.hdf') as product:
    # Work with the file.
{% endhighlight %}

#### Reading swath and datasets

Swaths are available as dictionary items of the HDFEOS instance:

{% highlight python %}
sw = product['2B-GEOPROF']
{% endhighlight %}

When accessing swaths, an instance of **Swath** class is returned.

Datasets are available as dictionary items of a swath:

{% highlight python %}
lat = sw['Latitude']
print(lat[0])
--> -64.9139
{% endhighlight %}

When accessing datasets, an instance of **Dataset** class is returned.
This instance is turned into a numpy array on index subsetting:

{% highlight python %}
type(lat)
--> <class 'ccplot.hdfeos.Dataset'>
type(lat[::])
--> <type 'numpy.ndarray'>
{% endhighlight %}

#### Listing swaths and datasets

A list of swaths can retrieved with **HDFEOS.keys()**:

{% highlight python %}
print('\n'.join(product.keys()))
--> 2B-GEOPROF
{% endhighlight %}

A list of datasets can be retrieved with **Swath.keys()**:

{% highlight python %}
print('\n'.join(sw.keys()))
--> Profile_time
    UTC_start
    TAI_start
    Latitude
    Longitude
    ...
{% endhighlight %}

#### Attributes

Attributes are accessible as **HDFEOS.attributes**, **Swath.attributes** and
**Dataset.attributes**:

{% highlight python %}
print(product.attributes.keys())
--> ['HDFEOSVersion', 'StructMetadata.0']
print(sw.attributes['start_time'])
--> '20130429203541'
print(sw['Radar_Reflectivity'].attributes['long_name'])
--> 'Radar Reflectivity Factor'
{% endhighlight %}

ccplot.algorithms
-----------------

### interp2d_12(data, X, Z, x1, x2, nx, z1, z2, nz)

Interpolate 2D data array distributed on coordinates
X and Z on a regular grid given by (x1, x2, nx) and (z1, z2, nz).

* `data(N, M)` is a 2D float32 array of data values.
* `X(N)` is a 1D float32 array of x-coorinates of data points.
* `Z(N, M)` is a 2D float32 array of z-coordinates of data points.
* `(x1, x2, nx)` define start, end and spacing of the regular grid
  in the x-direction.
* `(z1, x2, nz)` define start, end and spacing of the regular grid
  in the z-direction.

The interpolation is done by averaging all data points affecting a single
element of the regular grid. When the resolution of the regular grid
is greater than the resolution of data, this is equivalent to
nearest-neighbor interpolation.

ccplot.utils
------------

### calipso_time2dt(time)

Convert float in format `yymmdd.ffffffff` to datetime.

### cloudsat_time2dt(time, start_time)

Convert `time` in seconds since `start_time` (datetime instance) to datetime.

### cmap(filename)

Load ccplot colormap from file `filename`. Return a dictionary with keys:

* `colors(N, 4)` - array of RGBA values of colors
* `bounds(M)` - array of data value boundaries
* `ticks(K)` - array of tick values
* `under(4)` - color of values below low threshold (RGBA)
* `over(4)` - color of values above high threshold (RGBA)
* `bad(4)` - color of missing or bad values (RGBA)

RGBA values are represented as integers between 0 and 255.
