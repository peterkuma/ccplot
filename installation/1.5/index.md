---
layout: default
title: Getting Started
---
ccplot >= 1.5, < 2.0.0 (Python 2 & 3)
=====================================

Linux with native Python
------------------------

The following programs and libraries are required:

* [Python](http://www.python.org) >= 2.5, including development files
* [numpy](http://www.numpy.org) >= 1.1
* [matplotlib](http://matplotlib.org) >= 0.98.1
* [basemap](http://matplotlib.org/basemap/) >= 0.99.4 and the GEOS library (shipped with basemap)
* [cython](http://cython.org)
* [libhdf4](http://www.hdfgroup.org/products/hdf4/)
* [libhdfeos2](http://hdfeos.org/software/library.php#HDF-EOS2)

To install the required libraries and ccplot:

1. Make sure you have all dependencies installed.

   On Debian-based distributions (Ubuntu, Devuan, ...) you can install
   dependencies with:

       # Python 3, ccplot >= 1.5.4
       sudo apt install --no-install-recommends python3 python3-dev gcc python3-distutils cython3 libhdf4-dev libhdfeos-dev python3-pil python3-numpy python3-matplotlib python3-mpltoolkits.basemap ttf-bitstream-vera

       # Python 2, ccplot >= 1.5
       sudo apt install --no-install-recommends python python-dev gcc cython libhdf4-dev libhdfeos-dev python-pil python-numpy python-matplotlib python-mpltoolkits.basemap ttf-bitstream-vera

   On Fedora, download `szip-2.1.1.tar.gz` and `HDF-EOS2.20v1.00.tar.Z` from
   [Earthdata Wiki](https://wiki.earthdata.nasa.gov/display/DAS/Toolkit+Downloads),
   and install dependencies with:

       # ccplot >= 1.5.4
       sudo yum install g++ make python3-devel python3-Cython python3-numpy python3-matplotlib python3-basemap hdf-devel zlib-devel

       tar xf szip-2.1.1.tar.gz
       cd szip-2.1.1
       configure --prefix=/usr/local
       make
       sudo make install
       cd ..
       tar xf HDF-EOS2.20v1.00.tar.Z
       cd hdfeos
       ./configure CFLAGS=-I/usr/include/hdf --prefix=/usr/local --enable-install-include --with-pic
       make
       sudo make install
       cd ..

   On Ubuntu 20.10 (use `lsb_release -a` to find the
   version number if unsure), the system basemap library version (1.2.1) is
   incompatible with the system matplotlib library version. Install basemap
   from the upstream repository instead:

       sudo apt purge python3-mpltoolkits.basemap
       sudo apt install python3-pip git libgeos-dev
       sudo pip3 install git+https://github.com/matplotlib/basemap.git

2. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z

       # Python 3
       sudo python3 setup.py install

       # Python 2
       sudo python setup.py install

You should now be able to run ccplot in the terminal:

    ccplot -V

Linux with Anaconda 3
---------------------

ccplot can also be installed under the [Anaconda 3](https://anaconda.org)
Python distribution instead of the native Python distribution of a Linux
distribution. The instructions below are for ccplot >= 1.5.4. It is assumed
that you have already installed Anaconda 3 and activated the Anaconda environment
(the command `python` starts the Anaconda 3 version of Python).

1. Make sure you have all dependencies installed.

   On Debian-based Linux distributions (Ubuntu, Devuan, ...) you can install
   dependencies with:

       sudo apt install --no-install-recommends gcc libhdf4-dev libhdfeos-dev ttf-bitstream-vera git libgeos-dev

   On Fedora, download `szip-2.1.1.tar.gz` and `HDF-EOS2.20v1.00.tar.Z` from
   [Earthdata Wiki](https://wiki.earthdata.nasa.gov/display/DAS/Toolkit+Downloads),
   and install dependencies with:

       sudo yum install g++ make python3-devel python3-Cython python3-numpy python3-matplotlib python3-basemap hdf-devel zlib-devel

       tar xf szip-2.1.1.tar.gz
       cd szip-2.1.1
       configure --prefix=/usr/local
       make
       sudo make install
       cd ..
       tar xf HDF-EOS2.20v1.00.tar.Z
       cd hdfeos
       ./configure CFLAGS=-I/usr/include/hdf --prefix=/usr/local --enable-install-include --with-pic
       make
       sudo make install
       cd ..

2. Install basemap from the upstream repository:

       pip install git+https://github.com/matplotlib/basemap.git

3. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z
       python setup.py install

You should now be able to run ccplot in the terminal:

    ccplot -V

Windows (native)
----------------

ccplot can be installed from a binary distribution (Python wheel) in the
Python distribution Anaconda 3.8.

To install ccplot on Windows:

1. Install [Anaconda Python 3.8](https://www.anaconda.com) (later versions are
currently not supported).

2. Open the `Anaconda Prompt` from the Windows Start Menu.
   Install basemap:

       pip install https://github.com/peterkuma/basemap/releases/download/v1.2.2%2Bdev.1/basemap-1.2.2dev-cp38-cp38-win_amd64.whl

   Install ccplot:

       pip install ccplot==1.5.6

You should now be able to run ccplot in the terminal:

    ccplot -V

Windows (Windows Subsystem for Linux)
-------------------------------------

On Windows, it is possiblle to install ccplot under the "Windows Subsystem
for Linux" (WSL), which is a full-featured Linux distribution running on
Windows. Unlike the native installation described above, ccplot can only be run
in the WSL environment, and the ccplot API is only available in Python programs
run within this environemnt.

1. Install the "Windows Subsystem for Linux" (found under Settings → Optional
features → More Windows features).

2. Open Microsoft Store and install "Ubuntu".

3. Open "Ubuntu" in the Start Menu.

4. In the console, type:

       sudo apt update
       sudo apt upgrade

   and then follow the instructions above for installing ccplot on Ubuntu Linux.
   Use `cd /mnt/c/Users/<user>` to change the current directory to the Windows
   user's home directory, where `<user>` is the name of your Windows user
   account, and `ls` to list the content of a directory.

You should now be able to run ccplot in the Anaconda Prompt:

    ccplot -V

Windows (building from source code)
-----------------------------------

Follow these instructions if you want to build ccplot and the dependent
libraries from source code. This is the most difficult installation method,
but it can theoretically work with future versions of Python.

1. Install:
   - [Anaconda 3](https://www.anaconda.com)
   - [Visual Studio 2019](https://visualstudio.microsoft.com/downloads/)
   - [cmake](https://cmake.org)
   - [HDF4](https://portal.hdfgroup.org/display/HDF4/HDF4) binary distribution
     for Windows (`hdf-4.2.15-win10_64-vs15.zip` or later)
   - [7-zip](https://www.7-zip.org)

5. Download and unpack:
   - [HDF-EOS2](https://wiki.earthdata.nasa.gov/display/DAS/Toolkit+Downloads) source code (`hdf-eos2-3.0-src.tar.gz`)
   - [GEOS](https://trac.osgeo.org/geos/) (`geos-3.9.1.tar.bz2` or later) source code
   - [basemap](https://github.com/peterkuma/basemap/) source code
     (fixed to support building on Windows)
   - [ccplot](https://ccplot.org/download/) source code

7. Open the `Developer Command Prompt for VS 2019` from the Windows Start Menu
   and run:

       cd <geos-dir>
       mkdir build build
       cmake ..

   where `<geos-dir>` is the directory where you unpacked GEOS.
   Open `GEOS.sln` located in the GEOS `build` directory in Visual Studio 2019,
   set solution configuration to `Release` and perform `Build -> Build solution`.

8. Open `HDFEOS2.sln` located in the HDF-EOS2 `vs2019\HDF-EOS2` directory in
   Visual Studio 2019, set solution configuration to `Release` and perform
   `Build -> Build solution`.

9. Open the `Anaconda Prompt` from the Windows Start Menu and run:

       cd <basemap-dir>
       set GEOS_DIR=<geos-dir>
       python setup.py bdist_wheel
       pip install dist\basemap-1.2.2+dev-cp38-cp38-win_amd64.whl

       cd <ccplot-dir>
       set HDF_DIR=<hdf-dir>
       set HDFEOS_DIR=<hdfeos-dir>
       python setup.py bdist_wheel
       pip install dist\ccplot-1.5.6-cp38-cp38-win_amd64.whl

where `<basemap-dir>`, `<geos-dir>`, `<ccplot-dir>`, `<hdf-dir>` and
`<hdfeos-dir>` are the directories where you unpacked the respective packages.

You should now be able to run ccplot in the Anaconda Prompt:

    ccplot -V

macOS
-----

This installation has been tested on macOS Catalania.

1. Install [Anaconda 64-bit](https://www.anaconda.com/download/).

2. Install [MacPorts](https://www.macports.org).

3. Install required MacPorts packages. In the macOS Terminal:

        sudo port install jpeg hdf4 hdfeos geos

4. Install basemap:

       pip3 install git+https://github.com/peterkuma/basemap.git

5. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z
       python3 setup.py install

You should now be able to run ccplot in the macOS Terminal:

    ccplot -V
