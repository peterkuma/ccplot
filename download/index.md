---
layout: default
title: Getting Started
---
Getting Started
===============

Download
--------

<div class="table">
    <table>
        <thead><tr><th>Release Date</th><th>Download</th></tr></thead>
        <tbody>
            <tr>
                <td>2 August 2020</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.4.tar.gz">ccplot 1.5.4 (Linux &amp; macOS)</a>
                </td>
            </tr>
            <tr>
                <td>18 October 2015</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.2.win32-py2.7.exe">ccplot-1.5.2.win32-py2.7 (Windows)</a>
                </td>
            </tr>
        </tbody>
        <tbody id="archive" style="display: none">
            <tr>
                <td>18 October 2015</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.2.tar.gz">ccplot 1.5.2 (Linux &amp; macOS)</a>
                </td>
            </tr>
            <tr>
                <td>1 September 2015</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.1.tar.gz">ccplot 1.5.1</a>
                </td>
            </tr>
            <tr>
                <td>21 March 2015</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.tar.gz">ccplot 1.5</a>
                </td>
            </tr>
            <tr>
                <td>21 March 2015</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5.win32-py2.7.exe">ccplot 1.5.win32-py2.7</a>
                </td>
            </tr>
            <tr>
                <td>1 December 2013</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5-rc8.tar.gz">ccplot 1.5-rc8</a>
                </td>
            </tr>
            <tr>
                <td>20 November 2013</td>
                <td>
                    <a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.5-rc7.win32-py2.7.exe">ccplot 1.5-rc7.win32-py2.7</a>
                </td>
            </tr>
            <tr>
                <td>16 June 2013</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.4.7.tar.gz">ccplot 1.4.7</a></td>
            </tr>
            <tr>
                <td>4 June 2013</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.4.6.tar.gz">ccplot 1.4.6</a></td>
            </tr>
            <tr>
                <td>31 May 2013</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.4.5.tar.gz">ccplot 1.4.5</a></td>
            </tr>
            <tr>
                <td>2 September 2010</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.44.tar.gz">ccplot 1.44</a></td>
            </tr>
            <tr>
                <td>18 August 2010</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.43.tar.gz">ccplot 1.43</a></td>
            </tr>
            <tr>
                <td>11 June 2010</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.42.tar.gz">ccplot 1.42</a></td>
            </tr>
            <tr>
                <td>13 May 2010</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.41.tar.gz">ccplot 1.41</a></td>
            </tr>
            <tr>
                <td>7 May 2010</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.4.tar.gz">ccplot 1.4</a></td>
            </tr>
            <tr>
                <td>21 September 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.31.tar.gz">ccplot 1.31</a></td>
            </tr>
            <tr>
                <td>20 September 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.3.tar.gz">ccplot 1.3</a></td>
            </tr>
            <tr>
                <td>20 August 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.21.tar.gz">ccplot 1.21</a></td>
            </tr>
            <tr>
                <td>19 August 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.2.tar.gz">ccplot 1.2</a></td>
            </tr>
            <tr>
                <td>18 August 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.1.tar.gz">ccplot 1.1</a></td>
            </tr>
            <tr>
                <td>10 August 2009</td>
                <td><a href="https://sourceforge.net/projects/ccplot/files/ccplot/ccplot-1.0.tar.gz">ccplot 1.0</a></td>
            </tr>
        </tbody>
     </table>
     <a href="releasenotes/">Release Notes</a> |
     <a href="#" id="showall">Show All</a>
     <a href="#" id="hidearchived" style="display: none">Hide Archived</a>
</div>

<script>
document.getElementById('showall').onclick = function() {
    document.getElementById('archive').style.display = 'table-row-group';
    document.getElementById('hidearchived').style.display = 'inline';
    this.style.display = 'none';
    return false;
};
document.getElementById('hidearchived').onclick = function() {
    document.getElementById('archive').style.display = 'none';
    document.getElementById('showall').style.display = 'inline';
    this.style.display = 'none';
    return false;
};
</script>

Supported Operating Systems
---------------------------

ccplot works on unix-like operating systems (Linux, macOS, ...) and Windows.
For best experience, it is recommended to install ccplot on Linux.

Linux & Unix-like OS other than macOS
-------------------------------------

The following programs and libraries are required:

* [Python](http://www.python.org) >= 2.5, including development files
* [numpy](http://www.numpy.org) >= 1.1
* [matplotlib](http://matplotlib.org) >= 0.98.1
* [basemap](http://matplotlib.org/basemap/) >= 0.99.4 and the GEOS library (shipped with basemap)

**ccplot >= 1.5:**
* [cython](http://cython.org)
* [libhdf4](http://www.hdfgroup.org/products/hdf4/)
* [libhdfeos2](http://hdfeos.org/software/library.php#HDF-EOS2)

**ccplot < 1.5:**
* [PyNIO](http://www.pyngl.ucar.edu/Nio.shtml) >= 1.3.0b1

To install the required libraries and ccplot:

1. Make sure you have all dependencies installed.
   On Debian-based distributions (Ubuntu, Devuan, ...) you can install dependencies with:

       # Python 3, ccplot >= 1.5.4
       sudo apt-get install --no-install-recommends python3 python3-dev gcc python3-distutils cython3 libhdf4-dev libhdfeos-dev python3-pil python3-numpy python3-matplotlib python3-mpltoolkits.basemap ttf-bitstream-vera

       # Python 2, ccplot >= 1.5
       sudo apt-get install --no-install-recommends python python-dev gcc cython libhdf4-dev libhdfeos-dev python-pil python-numpy python-matplotlib python-mpltoolkits.basemap ttf-bitstream-vera

       # Python 2, ccplot < 1.5
       sudo apt-get install python python-dev python-numpy python-matplotlib python-mpltoolkits.basemap

   On Fedora, download `szip-2.1.1.tar.gz` and `HDF-EOS2.20v1.00.tar.Z` from
   [Earthdata Wiki](https://wiki.earthdata.nasa.gov/display/DAS/Toolkit+Downloads),
   and install dependencies with:

       # Python 3, ccplot >= 1.5.4
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

   **ccplot < 1.5:** PyNIO needs to be installed independently
   (see instructions below).

2. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z
       # Python 3, ccplot >= 1.5.4:
       sudo python3 setup.py install
       # Python 2:
       sudo python setup.py install

You should now be able to run ccplot in the terminal:

    ccplot -V

Windows
-------

To install ccplot on Windows:

1. Install [Anaconda 32-bit (Python 2.7 version)](https://repo.anaconda.com/archive/) (`Anaconda2-<version>-Windows-x86.exe`)

    **Note:** Anaconda 64-bit or Python 3 will not work.

2. Install the **basemap** package in the `Anaconda Prompt (Anaconda2)` (you can
it in the Start Menu):

        conda install basemap
	conda install basemap-data-hires

    You might have to run the above command twice. The first time it fails
    to find compatible versions of packages and the second time it succeeds.

    If you chose to install Anaconda for all users, you should run the Anaconda
    2 Prompt as Administrator to be allowed to install basemap.

3. Install ccplot using the supplied Windows installer
(ccplot-x.y.z.win32-py2.7.exe).

You should now be able to run ccplot in the Anaconda Prompt (Anaconda2):

    ccplot -V

macOS
-----

1. Install [Anaconda 64-bit](https://www.anaconda.com/download/).

2. Install [MacPorts](https://www.macports.org).

3. Install required MacPorts packages. In the macOS Terminal:

        sudo port install hdf4 hdfeos

4. Build and install ccplot:

       tar xzf ccplot-x.y.z.tar.gz
       cd ccplot-x.y.z
       python setup.py install

You should now be able to run ccplot in the macOS Terminal:

    ccplot -V

Installing PyNIO (ccplot < 1.5)
-------------------------------

PyNIO can be downloaded upon free registration from
[EOS](http://www.earthsystemgrid.org/home.htm). However, to make your life
easier, you can also download [PyNIO precompiled binaries](pynio/) without
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

Your Experience
---------------

If you have any difficulty with the installation, or if you find a bug,
please write to the mailing list at
[ccplot-general@lists.sourceforge.net](mailto:ccplot-general@lists.sourceforge.net)
or submit an issue on [GitHub](https://github.com/peterkuma/ccplot).

Tutorial
--------

Please continue with ccplot manual (Chapter 6) in
[Visualising Data from CloudSat and CALIPSO Satellites](/pub/doc/pdf/Visualising_Data_from_CloudSat_and_CALIPSO_Satellites.pdf)
and [ccplot man page](/doc/ccplot.1.html).

License
-------

ccplot is provided under the terms of a
[BSD license](https://github.com/peterkuma/ccplot/blob/master/LICENSE),
allowing you to redistribute, modify and use the software in free and
commercial products without restrictions.

Known Issues
------------

### 10 October 2015

A bug in matplotlib 1.4.3 causes a warning to be printed:

    matplotlib/collections.py:590: FutureWarning: elementwise comparison failed; returning scalar instead, but in the future will perform elementwise comparison

It should be fixed in matplotlib 1.5.0 (issue [#5209](https://github.com/matplotlib/matplotlib/issues/5209)).

### 4 June 2013

There is a bug with python-dap which causes a warning to be printed:

    /usr/lib/pymodules/python2.7/mpl_toolkits/__init__.py:2: UserWarning: Module dap was already imported from None, but /usr/lib/python2.7/dist-packages is being added to sys.path
    __import__('pkg_resources').declare_namespace(__name__)

Package python-dap is installed on Ubuntu and Debian as
"recommended" by python-mpltoolkits.basemap. It can be removed
(as it is not required), and the warning will not appear any more.

The bug has already been [reported](http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=709376)
to the Debian bug reporting system.

### 12 June 2013

**ccplot < 1.5**
There is a bug in NetCDF compatibility layer of libhdf4 (used by PyNIO)
which causes wrong size of datasets to be reported. As a result, the
data may be trimmed by a relatively small amount of rays at the end
of a granule. The bug has been confirmed by the HDF Group, and is being
solved.

### 16 June 2013

**ccplot <= 1.4.6**
There was a serious bug in the visualization of CALIPSO profiles,
whereby the altitude of data points
was shifted by one element, resulting in a difference of as much as 300m
relative to their true location. The difference in the highest-resolution
regions was 60m.
