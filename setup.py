from distutils.core import setup, Extension
from glob import glob

module1 = Extension('cctk',
                    sources=['cctkmodule.c'])

setup(name='ccplot',
      version='1.3.1',
      description='CloudSat/CALIPSO data processing helper routines',
      author='Peter Kuma',
      author_email='peterkuma@waveland.org',
      url='',
      ext_modules=[module1],
      scripts=['ccplot'],
      requires=['matplotlib', 'PyNIO', 'basemap'],
      data_files=[('share/doc/ccplot/', ['Changelog', 'NEWS']),
                  ('share/ccplot/cmap/', glob('cmap/*')),
                  ('man/man1/', ['ccplot.1'])])
