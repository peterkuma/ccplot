from distutils.core import setup, Extension
from glob import glob
import numpy

module1 = Extension('cctk',
                    sources=['cctkmodule.c'])

setup(name='ccplot',
      version='1.4.7',
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
      ext_modules=[module1],
      scripts=['ccplot'],
      requires=['basemap', 'matplotlib', 'numpy', 'PyNIO'],
      include_dirs=[numpy.get_include()],
      data_files=[('share/doc/ccplot/', ['Changelog', 'NEWS']),
                  ('share/ccplot/cmap/', glob('cmap/*')),
                  ('man/man1/', ['ccplot.1'])])
