---
layout: default
title: Getting Started
---
ccplot < 1.5.0 (Python 2)
=========================

Linux
-----

The following programs and libraries are required:

* [Python](http://www.python.org) >= 2.5, < 3.0, including development files
* [numpy](http://www.numpy.org) >= 1.1
* [matplotlib](http://matplotlib.org) >= 0.98.1
* [basemap](http://matplotlib.org/basemap/) >= 0.99.4 and the GEOS library (shipped with basemap)
* [PyNIO](http://www.pyngl.ucar.edu/Nio.shtml) >= 1.3.0b1

To install the required libraries and ccplot:

1. Make sure you have all dependencies installed.

   On Debian-based distributions (Ubuntu, Devuan, ...) you can install
   dependencies with:

       sudo apt install python python-dev python-numpy python-matplotlib python-mpltoolkits.basemap

   On Ubuntu 20.10 (use `lsb_release -a` to find the
   version number if unsure), the system basemap library version (1.2.1) is
   incompatible with the system matplotlib library version. Install basemap
   from the upstream repository instead:

       sudo apt purge python3-mpltoolkits.basemap
       sudo apt install python3-pip git libgeos-dev
       sudo pip3 install git+https://github.com/matplotlib/basemap.git

2. Install PyNIO. PyNIO can be downloaded upon free registration from
[EOS](http://www.earthsystemgrid.org). However, to make your life
easier, you can also download [PyNIO precompiled binaries](../pynio/) without
registration from this website (recommended). If you need to build PyNIO
from source, follow the [instructions](http://www.pyngl.ucar.edu/Download/build_pynio_from_src.shtml)
on the PyNIO website.

    To install PyNIO from a binary distribution on Ubuntu/Debian, do:

        # Substitute the right name of the binary archive and Python version.

        mkdir pynio
        tar -C pynio -xzf PyNIO-1.4.0.linux-debian-x86_64-gcc432-py265-numpy141-nodap.tar.gz

        sudo cp -r pynio/lib/python2.6/site-packages/* /usr/local/lib/python2.6/dist-packages/

    On other systems:

        # Substitute the right name of the binary archive.

        tar -C /usr/local -xzf PyNIO-1.4.0.linux-debian-x86_64-gcc432-py265-numpy141-nodap.tar.gz

    Test installation (optional):

        python -c "import Nio; print Nio.__version__"
        --> 1.4.0

2. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z

       # Python 3, ccplot >= 1.5.4:
       sudo python3 setup.py install

       # Python 2, ccplot < 2.0.0:
       sudo python setup.py install

You should now be able to run ccplot in the terminal:

    ccplot -V
