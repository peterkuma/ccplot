#!/usr/bin/env python3

import setuptools
from distutils.core import setup, Extension
from Cython.Distutils import build_ext
from glob import glob
import shutil
import sys
import os
import numpy

# Windows build: modify to point to HDF4 and HDF-EOS2 libraries.
WIN_HDF_DIR=r'C:\Program Files\HDF_Group\HDF\4.2.15'
WIN_HDFEOS_DIR=r'C:\Program Files\hdf-eos2-3.0'


if sys.platform == 'win32':
    HDF_DIR = os.environ.get('HDF_DIR', WIN_HDF_DIR)
    HDFEOS_DIR = os.environ.get('HDFEOS_DIR', WIN_HDFEOS_DIR)
    scripts = ['bin/ccplot', 'bin/ccplot.bat']
    hdf_libraries = ['hdf', 'mfhdf', 'libjpeg', 'libzlib', 'libszip', 'xdr', 'Ws2_32']
    hdf_include_dirs = [os.path.join(HDF_DIR, 'include')]
    hdf_library_dirs = [os.path.join(HDF_DIR, 'lib')]
    hdfeos_libraries = ['hdf-eos2']
    hdfeos_include_dirs = [os.path.join(HDFEOS_DIR, r'include')]
    hdfeos_library_dirs = [os.path.join(HDFEOS_DIR, r'vs2019\HDF-EOS2\x64\Release')]
    dlls = [
        os.path.join(HDF_DIR, 'bin', x)
        for x in ['hdf.dll', 'mfhdf.dll', 'xdr.dll']
    ]
    for filename in dlls:
        shutil.copy(filename, '.')
    package_data = {'ccplot': ['hdf.dll', 'mfhdf.dll', 'xdr.dll']}
else:
    scripts = ['bin/ccplot']
    hdf_libraries = ['mfhdf', 'df', 'jpeg', 'z']
    hdf_include_dirs = [
        '/usr/include/hdf',
        '/usr/local/include/hdf',
        '/usr/include/x86_64-linux-gnu/hdf',
        '/opt/local/include',
    ]
    hdf_library_dirs = ['/opt/local/lib']
    hdfeos_libraries = ['hdfeos']
    hdfeos_include_dirs = []
    hdfeos_library_dirs = []
    package_data = {}

if sys.platform == 'darwin':
    hdfeos_libraries += ['Gctp']


setup(
    name='ccplot',
    version='2.1.0',
    description='CloudSat and CALIPSO plotting tool',
    long_description="""ccplot is an open source command-line program for
    plotting profile, layer and earth view data sets from CloudSat, CALIPSO
    and Aqua MODIS products.""",
    platforms='any',
    author='Peter Kuma',
    author_email='peter@peterkuma.net',
    url='http://www.ccplot.org/',
    license='BSD',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: C",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    scripts=scripts,
    packages=[
        'ccplot',
    ],
    install_requires=[
        'numpy>=1.1',
        'matplotlib>=0.98.1',
        'cartopy>=0.17.0',
        'packaging>=20.03',
        'pytz',
    ],
    setup_requires=[
        'cython'
    ],
    include_dirs=[numpy.get_include()],
    data_files=[('share/doc/ccplot', ['NEWS']),
                ('share/ccplot/cmap', glob('cmap/*')),
                ('man/man1', ['man/ccplot.1'])],
    include_package_data=True,
    package_data=package_data,
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
