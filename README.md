ccplot
======

ccplot is an open source command-line application for producing two-dimensinal
plots of profile, layer and earth view data from CloudSat, CALIPSO and Aqua
satellites.

The project is hosted at [ccplot.org](https://ccplot.org).

Installation
------------

The installation instructions below are general instructions for Linux
distributions. For more detailed instructions and other operating systems
please see [ccplot.org/download](https://ccplot.org/download).

Requirements:

* Python 3
* Cython
* HDF4
* HDF-EOS2

Install the above from a Linux distribution package repositories. Python 3
and Cython are also included with [Anaconda](https://anaconda.org).

Python packages:

* numpy
* matplotlib
* cartopy
* packaging
* pytz

The Python packages are installed automatically by pip together with ccplot:

    # To install from a local directory:
    pip3 install .

    # To install from PyPI:
    pip3 install ccplot

More information
----------------

See the man page ccplot(1) for information about usage, or visit
[ccplot.org](https://ccplot.org).

License
-------

This program can be freely distributed and modified under the terms
of the 2-clause BSD license. You can find the full text in the file LICENSE.

Thanks
------

A number of people have helped to make ccplot better. Special thanks to:

  * Ryan Scott for helping to port ccplot to Mac OS X.
  * Many others for reporting bugs.
