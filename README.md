ccplot
======

ccplot is an open source command-line application for producing
two-dimensinal plots of profile, layer and earth view data
from CloudSat, CALIPSO and Aqua satellites.

The project is hosted at [ccplot.org](http://ccplot.org).

Requirements
------------

Make sure you have the following programs and libraries installed:

  * [Python](http://www.python.org/) >= 2.6 and < 3.0,
    including development files
  * [cython](http://cython.org/)
  * [numpy](http://www.numpy.org/)
  * [matplotlib](http://matplotlib.org/)
  * [basemap](http://matplotlib.org/basemap/)
  * [libhdf4](http://www.hdfgroup.org/products/hdf4/)
  * [libhdfeos2](http://hdfeos.org/software/library.php#HDF-EOS2)

**Note:** On Debian and Ubuntu, install dependencies with:

    apt-get install --no-install-recommends cython python-numpy python-imaging python-matplotlib python-mpltoolkits.basemap ttf-bitstream-vera libhdf4-dev libhdfeos-dev

Installation
------------

Go to the source distribution directory and perform the following commands:

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
