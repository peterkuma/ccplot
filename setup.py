from distutils.core import setup, Extension
from Cython.Distutils import build_ext
from glob import glob
import sys
import os
import numpy

# Windows build: modify to point to HDF4 and HDF-EOS2 libraries.
WIN_HDF_PATH=r'C:\Program Files (x86)\HDF_Group\HDF\4.2.9'
WIN_HDFEOS_PATH=r'C:\Program Files (x86)\hdfeos2.18'


if sys.platform == 'win32':
    scripts = ['bin/ccplot', 'bin/ccplot.bat']
    hdf_libraries = ['hdf', 'mfhdf', 'libjpeg', 'libzlib', 'libszip', 'xdr', 'Ws2_32']
    hdf_include_dirs = [os.path.join(WIN_HDF_PATH, 'include')]
    hdf_library_dirs = [os.path.join(WIN_HDF_PATH, 'lib')]
    hdfeos_libraries = ['hdfeos']
    hdfeos_include_dirs = [os.path.join(WIN_HDFEOS_PATH, r'hdfeos\include')]
    hdfeos_library_dirs = [os.path.join(WIN_HDFEOS_PATH, r'hdfeos_dev\hdfeos\Release')]
else:
    scripts = ['bin/ccplot']
    hdf_libraries = ['mfhdf', 'df', 'jpeg', 'z']
    hdf_include_dirs = ['/usr/include/hdf', '/usr/local/include/hdf']
    hdf_library_dirs = []
    hdfeos_libraries = ['hdfeos']
    hdfeos_include_dirs = []
    hdfeos_library_dirs = []


setup(
    name='ccplot',
    version='1.5-rc6',
    description='CloudSat and CALIPSO plotting tool',
    long_description="""
    ccplot is a command-line application that reads CloudSat, CALISO
    and Aqua MODIS HDF files, and produces plots of profile, layer and swath
    products.
    """,
    platforms='any',
    author='Peter Kuma',
    author_email='peter.kuma@ccplot.org',
    url='http://www.ccplot.org/',
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Natural Language :: English",
    ],
    scripts=scripts,
    packages=[
        'ccplot',
    ],
    requires=[
        'cython',
        'numpy',
        'scipy',
        'matplotlib',
        'basemap',
    ],
    include_dirs=[numpy.get_include()],
    data_files=[('share/doc/ccplot', ['NEWS']),
                ('share/ccplot/cmap', glob('cmap/*')),
                ('man/man1', ['man/ccplot.1'])],
    cmdclass={
        'build_ext': build_ext,
    },
    ext_modules=[
        Extension(
            'ccplot.cctk',
            ['ccplot/cctk.c']
        ),
        Extension(
            'ccplot.hdf',
            ['ccplot/hdf.pyx'],
            include_dirs=hdf_include_dirs,
            library_dirs=hdf_library_dirs,
            libraries=hdf_libraries,
        ),
        Extension(
            'ccplot.hdfeos',
            ['ccplot/hdfeos.pyx'],
            include_dirs=(hdf_include_dirs + hdfeos_include_dirs),
            library_dirs=(hdf_library_dirs + hdfeos_library_dirs),
            libraries=(hdfeos_libraries + hdf_libraries),
        ),
        Extension(
            'ccplot.algorithms',
            ['ccplot/algorithms.pyx'],
        ),
    ],
)
