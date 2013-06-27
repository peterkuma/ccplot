from distutils.core import setup, Extension
from Cython.Distutils import build_ext
from glob import glob
import numpy

setup(
    name='ccplot',
    version='1.5-rc5',
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
    scripts=['bin/ccplot'],
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
    data_files=[('share/doc/ccplot/', ['NEWS']),
                ('share/ccplot/cmap/', glob('cmap/*')),
                ('man/man1/', ['man/ccplot.1'])],
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
            libraries=['mfhdf', 'df', 'jpeg', 'z'],
        ),
        Extension(
            'ccplot.hdfeos',
            ['ccplot/hdfeos.pyx'],
            libraries=['hdfeos', 'mfhdf', 'df', 'jpeg', 'z'],
            extra_compile_args=['-I/usr/include/hdf'],
        ),
        Extension(
            'ccplot.algorithms',
            ['ccplot/algorithms.pyx'],
        ),
    ],
)
