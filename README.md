ccplot
======

ccplot is an open source command-line application for producing
two-dimensinal plots of profile, layer and earth view data
from CloudSat, CALIPSO and Aqua satellites.

The project is hosted at [ccplot.org](http://ccplot.org).

Requirements
------------

Make sure you have the following programs and libraries installed:

  * [Python](http://www.python.org/) >= 2.6
    including development files
  * [cython](http://cython.org/)
  * [numpy](http://www.numpy.org/)
  * [matplotlib](http://matplotlib.org/)
  * [basemap](http://matplotlib.org/basemap/)
  * [libhdf4](http://www.hdfgroup.org/products/hdf4/)
  * [libhdfeos2](http://hdfeos.org/software/library.php#HDF-EOS2)

**Note:** On Debian-based distributions (Ubuntu, Devuan, ...) install
dependencies with:

    # Python 3
    apt-get install --no-install-recommends python3 python3-dev gcc python3-distutils cython3 libhdf4-dev libhdfeos-dev python3-pil python3-numpy python3-matplotlib python3-mpltoolkits.basemap ttf-bitstream-vera

    # Python 2
    apt-get install --no-install-recommends python python-dev gcc cython libhdf4-dev libhdfeos-dev python-pil python-numpy python-matplotlib python-mpltoolkits.basemap ttf-bitstream-vera

Installation
------------

Go to the source distribution directory and perform the following commands:

    # Python 3
    python3 setup.py build
    sudo python3 setup.py install

    # Python 2
    python setup.py build
    sudo python setup.py install

More information
----------------

See the man page ccplot(1) for information about usage, or visit
[ccplot.org](http://ccplot.org).

License
-------

This program can be freely distributed and modified under the terms
of the 2-clause BSD license. You can find the full text in the file LICENSE.

Thanks
------

A number of people helped to make ccplot better for others.
Special thanks goes to:

  * Ryan Scott for helping to port ccplot to Mac OS X.
  * Yin and to Subok Kim for reporting bugs.
