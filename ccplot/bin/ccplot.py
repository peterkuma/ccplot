#!/usr/bin/env python3
#
# ccplot
# This file is a part of ccplot: CloudSat and CALIPSO plotting tool.
#
# Copyright (c) 2009-2025 Peter Kuma
#
# This software is provided under the terms of a 2-clause BSD licence:
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with
#      the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE CCPLOT PROJECT ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE CCPLOT PROJECT OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# We don't want the annoying KeyboadInterrupt exception on Control-C.
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

#
# Includes.
#

# Core python includes.
import os
import sys
from math import *
import getopt
import datetime as dt
import re
import copy
import inspect
import warnings
warnings.filterwarnings('ignore')

# Other includes.
import packaging.version
import numpy as np
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import ccplot.config
from ccplot.hdf import HDF
from ccplot.hdfeos import HDFEOS

# CCTK is a helper module that performs various calculations.
from ccplot import cctk

import ccplot.algorithms
import ccplot.utils


# Early global variables.
program_name = os.path.basename(sys.argv[0])
__version__ = "2.1.4"
CCPLOT_CMAP_PATH = os.path.join(ccplot.config.sharepath, 'cmap') \
                 + ":/usr/share/ccplot/cmap:/usr/local/share/ccplot/cmap"

# Early functions.
def fail(s):
    global program_name
    sys.stderr.write("%s: %s\n" % (program_name, s))
    sys.exit(1)

def fsencode(x):
    return x if (sys.version_info[0] == 2 or type(x) is not str) \
        else os.fsencode(x)

def sdecode(x):
    return x if (sys.version_info[0] == 2 or type(x) is not bytes) \
        else x.decode('utf-8')

# Version checking.
if mpl.__version__ < "0.98.1":
    fail("matplotlib 0.98.1 required, %s present" % mpl.__version__)
if cartopy.__version__ < "0.17.0":
    fail("cartopy 0.17.0 required, %s present" % cartopy.__version__)
if np.__version__ < "1.1":
    fail("numpy 1.1 required, %s present" % np.__version__)


#
# Constants.
#

BAND_MODE_RAW = 0
BAND_MODE_REFLECTANCE = 1
BAND_MODE_RADIANCE = 2

PLANCK_C1 = 1.191E-16
PLANCK_C2 = 1.439E-2

ATRAIN_SPEED = 7.0 # km per s.
PROFILE_BINHEIGHT = 800 # Height of a bin in profile products in meters.
                        # This defines the area of influence of a data point.
EV_DATAPOINT_SIZE = 2000 # meters.

PROJECTIONS = (
    ("aea", "AlbersEqualArea", "Albers equal area"),
    ("aeqd", "AzimuthalEquidistant", "Azimuthal equidistant"),
    ("cea", "LambertCylindrical", "Lambert cylindrical"),
    ("cyl", "PlateCarree", "Cylindrical equidistant (Plate Carree)"),
    ("eck1", "EckertI", "Eckert I"),
    ("eck2", "EckertII", "Eckert II"),
    ("eck3", "EckertIII", "Eckert III"),
    ("eck4", "EckertIV", "Eckert IV"),
    ("eck5", "EckertV", "Eckert V"),
    ("eck6", "EckertVI", "Eckert VI"),
    ("eqdc", "EquidistantConic", "Equidistant conic"),
    ("eqearth", "EqualEarth", "Equal Earth"),
    ("europp", "EuroPP", "EuroPP"),
    ("geos", "Geostationary", "Geostationary"),
    ("gnom", "Gnomonic", "Gnomonic"),
    ("igh", "InterruptedGoodeHomolosine", "Interrupted Goode\"s homolosine"),
    ("laea", "LambertAzimuthalEqualArea", "Lambert azimuthal qqual area"),
    ("lcc", "LambertConformal", "Lambert conformal"),
    ("merc", "Mercator", "Mercator"),
    ("mill", "Miller", "Miller cylindrical"),
    ("moll",	"Mollweide", "Mollweide"),
    ("npstere", "NorthPolarStereo", "North-Polar stereographic"),
    ("nsper", "NearsidePerspective", "Nearside perspective"),
    ("ob_tran", "RotatedPole", "Rotated pole"),
    ("ortho", "Orthographic", "Orthographic"),
    ("osgb", "OSGB", "OSGB"),
    ("osni", "OSNI", "OSNI"),
    ("robin", "Robinson", "Robinson"),
    ("sinu", "Sinusoidal", "Sinusoidal"),
    ("spstere", "SouthPolarStereo", "South-Polar stereographic"),
    ("stere", "Stereographic", "Stereographic"),
    ("tmerc", "TransverseMercator", "Transverse Mercator"),
    ("utm", "UTM", "Universal Transverse Mercator (UTM)"),
)

SUPPORTED_PROJECTIONS = [projection[0] for projection in PROJECTIONS]

MODIS_WAVELENGTHS = np.zeros(36)
MODIS_WAVELENGTHS[0:36] = (645,858.500,469,555,1240,1640,2130,412.5,443,488,531,551,
667,678,748,869.500,905,936,940,
3660,3929,3929,4020,4433,4482,1360,6535,7175,8400,9580,10780,11770,13185,13485,
13785,14085)

# Explicitly supported datasets.
DATASETS = {
    "cloudsat-reflec": {
        "datasets": [b"Radar_Reflectivity"],
    },
    "calipso532": {
        "title": "Total Attenuated Backscatter 532nm",
        "units": "km$^{-1}$ sr$^{-1}$",
        "datasets": [b"Total_Attenuated_Backscatter_532"],
    },
    "calipso532p": {
        "title": "Perpendicular Attenuated Backscatter 532nm",
        "units": "km$^{-1}$ sr$^{-1}$",
        "datasets": [b"Perpendicular_Attenuated_Backscatter_532"],
    },
    "calipso1064": {
        "title": "Attenuated Backscatter 1064nm",
        "units": "km$^{-1}$ sr$^{-1}$",
        "datasets": [b"Attenuated_Backscatter_1064"],
    },
    "calipso-cratio": {
        "title": "Attenuated Color Ratio 1064nm/532nm",
        "datasets": [
            b"Total_Attenuated_Backscatter_532",
            b"Attenuated_Backscatter_1064"
        ],
    },
    "calipso-dratio": {
        "title": "Depolarization Ratio",
        "datasets": [
            b"Total_Attenuated_Backscatter_532",
            b"Perpendicular_Attenuated_Backscatter_532"
        ],
    },
    "calipso532-layer": {
        "title": "Integrated Attenuated Backscatter 532nm",
        "units": "sr$^{-1}$",
        "datasets": [b"Integrated_Attenuated_Backscatter_532"],
    },
    "calipso1064-layer": {
        "title": "Integrated Attenuated Backscatter 1064nm",
        "units": "sr$^{-1}$",
        "datasets": [b"Integrated_Attenuated_Backscatter_1064"],
    },
    "calipso-cratio-layer": {
        "title": "Integrated Attenuated Total Color Ratio 1064nm/532nm",
        "datasets": [b"Integrated_Attenuated_Total_Color_Ratio"],
    },
    "calipso-dratio-layer": {
        "title": "Integrated Volume Depolarization Ratio",
        "datasets": [b"Integrated_Volume_Depolarization_Ratio"],
    },
    "calipso-temperature-layer": {
        "title": "Midlayer Temperature",
        "units": "K",
        "offset": -273.15,
        "datasets": [b"Midlayer_Temperature"],
    },
}


#
# Global variables.
#

verbose = False

#
# Classes.
#

class Swath(object):
    name = ""
    lon = np.empty(0, dtype=np.float64)
    lat = np.empty(0, dtype=np.float64)
    data = np.empty(0, dtype=np.float64)


class AutoOpts(object):
    def setint(self, o, v, a=-sys.maxsize-1, b=sys.maxsize):
        i = int(v)
        if i < a or i > b:
            raise ValueError("%s expected between %d and %d" % (o, a, b))
        return i

    def setfloat(self, o, v, a=float("-infinity"), b=float("infinity")):
        f = float(v)
        if f < a or f > b:
            raise ValueError("%s expected between %f and %f" % (o, a, b))
        return f

    def setstr(self, o, v, maxlen=sys.maxsize):
        if len(v) > maxlen:
            raise ValueError("%s can be at most %d characters long" % (o, maxlen))
        return v

    def setcolor(self, o, v):
        if re.match("^#[0-9A-Z]{6}$", v, re.IGNORECASE) == None:
            raise ValueError("%s is not a valid color" % v)
        return v

    def settuple(self, o, v, func, *args, **kwargs):
        parts = v.split(":")
        return [func(o, p, *args, **kwargs) for p in parts]

    def setenum(self, o, v, vals):
        if v not in vals: raise ValueError("%s must be one of: %s" % (v,vals))
        return v

    def setbool(self, o, v):
        if v == "1": return True
        elif v == "0": return False
        else: raise ValueError("%s must be 1 or 0" % o)

    def setlon(self, o, v):
        if v.endswith("W"): lon = -float(v[0:-1])
        elif v.endswith("E"): lon = float(v[0:-1])
        else: raise ValueError("%s must end with W or E" % o)
        if lon < -180 or lon > 180: raise ValueError("%s out of range" % o)
        return lon

    def setlat(self, o, v):
        if v.endswith("S"): lat = -float(v[0:-1])
        elif v.endswith("N"): lat = float(v[0:-1])
        else: raise ValueError("%s must end with S or N" % o)
        if lat < -90 or lat > 90: raise ValueError("%s out of range" % o)
        return lat


class PlotOpts(AutoOpts):
    cbfontsize = 8
    cbspacing = 0.4
    coastlinescolor = "#46396D"
    coastlineslw = 0.4
    countriescolor = "#46396D"
    countrieslw = 0.2
    drawcoastlines = True
    drawcountries = True
    drawelev = True
    drawlakes = True
    drawlsmask = True
    drawmeridians = True
    drawminormeridians = True
    drawminorparallels = True
    drawparallels = True
    elevcolor = "#FF0000"
    elevlw = 0.5
    fontsize = 10
    landcolor = "#E9E4F7"
    majormeridianscolor = "#000000"
    majormeridianslw = 0.3
    majorparallelscolor = "#000000"
    majorparallelslw = 0.3
    mapres = None
    meridiansbase = 0
    minormeridianscolor = "#000000"
    minormeridianslw = 0.1
    minorparallelscolor = "#000000"
    minorparallelslw = 0.1
    nminormeridians = 0
    nminorparallels = 0
    padding = 1.0
    parallelsbase = 0
    plotheight = 6.0
    title = None
    trajcolors = ("#FF0000", "#0000FF", "#00FF00")
    trajlws = (0.5,)
    trajticks = -1
    trajnminorticks = -1
    watercolor = "#FFFFFF"

    def setopt(self, o, v):
        if   o == "cbfontsize": q = self.setfloat(o, v, 0)
        elif o == "cbspacing": q = self.setfloat(o, v, 0)
        elif o == "coastlinecolor": q = self.setcolor(o, v)
        elif o == "coastlinelw": q = self.setfloat(o, v, 0)
        elif o == "countriescolor": q = self.setcolor(o, v)
        elif o == "countrieslw": q = self.setfloat(o, v, 0)
        elif o == "drawcoastlines": q = self.setbool(o, v)
        elif o == "drawcountries": q = self.setbool(o, v)
        elif o == "drawelev": q = self.setbool(o, v)
        elif o == "drawlakes": q = self.setbool(o, v)
        elif o == "drawlsmask": q = self.setbool(o, v)
        elif o == "drawmeridians": q = self.setbool(o, v)
        elif o == "drawminormeridians": q = self.setbool(o, v)
        elif o == "drawminorparallels": q = self.setbool(o, v)
        elif o == "elevcolor": q = self.setcolor(o, v)
        elif o == "elevlw": q = self.setfloat(o, v, 0)
        elif o == "fontsize": q = self.setfloat(o, v, 0)
        elif o == "landcolor": q = self.setcolor(o, v)
        elif o == "linewidth": q = self.setfloat(o, v, 0)
        elif o == "majormeridianscolor": q = self.setcolor(o, v)
        elif o == "majormeridianslw": q = self.setfloat(o, v, 0)
        elif o == "majorparallelscolor": q = self.setcolor(o, v)
        elif o == "majorparallelslw": q = self.setfloat(o, v, 0)
        elif o == "mapres": q = self.setenum(o, v, ("auto","10m","50m","110m"))
        elif o == "meridiansbase": q = self.setfloat(o, v, 0)
        elif o == "minormeridianscolor": q = self.setcolor(o, v)
        elif o == "minormeridianslw": q = self.setfloat(o, v, 0)
        elif o == "nminormeridians": q = self.setint(o, v, 0)
        elif o == "nminorparallels": q = self.setint(o, v, 0)
        elif o == "padding": q = self.setfloat(o, v, 0)
        elif o == "parallelsbase": q = self.setfloat(o, v, 0)
        elif o == "plotheight": q = self.setfloat(o, v, 0)
        elif o == "title": q = self.setstr(o, v)
        elif o == "trajcolors": q = self.settuple(o, v, self.setcolor)
        elif o == "trajlws": q = self.settuple(o, v, self.setfloat, 0)
        elif o == "trajticks": q = self.setint(o, v, -1)
        elif o == "trajnminorticks": q = self.setint(o, v, -1)
        elif o == "watercolor": q = self.setcolor(o, v)
        else: raise ValueError("Unrecognized option: %s" % o)
        setattr(self, o, q)


class ProjOpts(AutoOpts):
    lat_0 = None
    lat_1 = None
    lat_2 = None
    lat_ts = None
    lon_0 = None
    cutoff = None
    k_0 = None
    o_lon_p = None
    o_lat_p = None
    h = None
    sweep = None
    zone = None

    def setopt(self, o, v):
        if   o == "lon_0": q = self.setlon(o, v)
        elif o == "lat_0": q = self.setlat(o, v)
        elif o == "lat_1": q = self.setlat(o, v)
        elif o == "lat_2": q = self.setlat(o, v)
        elif o == "lat_ts": q = self.setlat(o, v)
        elif o == "cutoff": q = self.setlat(o, v)
        elif o == "k_0": q = self.setfloat(o, v, 0)
        elif o == "o_lon_p": q = self.setlon(o, v)
        elif o == "o_lat_p": q = self.setlat(o, v)
        elif o == "h": q = self.setfloat(o, v, 0)
        elif o == "sweep": q = self.setenum(o, v, ("x", "y"))
        elif o == "zone": q = self.setint(o, v, 1, 60)

        else: raise ValueError
        setattr(self, o, q)


class TimeLocator(mpl.ticker.Locator):
    def __init__(self, n, time, time2dt, \
                 steps=     [1,     2, 5, 10, 15, 30, 60, 300, 600, 900],
                 minorsteps=[0.2, 0.5, 1,  2,  3,  5, 10,  60, 120, 300]):
        self.n = int(n)
        self.time = time
        self.time2dt = time2dt
        self.steps = np.array(steps, np.float64)
        self.minorsteps = np.array(minorsteps, np.float64)
        self.minorlocs = []

    def __call__(self):
        vmin, vmax = self.axis.get_view_interval()
        vmin, vmax = int(vmin), int(vmax)
        if len(self.time) == 0 or self.n <= 0: return []
        if vmin < 0: vmin = 0
        if vmax >= len(self.time): vmax = len(self.time) - 1
        if vmax < vmin: vmax = vmin = 0
        td = self.time2dt(self.time[vmax]) - self.time2dt(self.time[vmin])
        # Time difference in seconds.
        nseconds = td.days*86400 + td.seconds + td.microseconds*0.000001
        if nseconds == 0: return []
        ratio = 1.0 * (vmax-vmin)/nseconds
        time0 = self.time2dt(self.time[vmin])
        # Adjust to the nearest minute. We introduce a correction of 200ms
        # (1 ray is about 49ms), so that we don't get min:59.
        offset = -ratio * (time0.microsecond * 0.000001 + \
                           time0.second + \
                           time0.minute * 60 - 0.2)
        stepdiffs = self.steps - nseconds/self.n
        np.place(stepdiffs, stepdiffs < 0, float("infinity"))
        i = stepdiffs.argmin()
        base = ratio * self.steps[i]
        minorbase = ratio * self.minorsteps[i]
        offset = offset % base
        self.minorlocs = np.arange(vmin + offset - base, vmax + offset + base,
                                   minorbase)
        return np.arange(vmin + offset, vmax + offset, base)


class TimeMinorLocator(mpl.ticker.Locator):
    def __call__(self):
        locator = self.axis.get_major_locator()
        if isinstance(locator, TimeLocator):
            return locator.minorlocs
        else:
            return []


class TimeFormatter(mpl.ticker.Formatter):
    def __init__(self, time, time2dt):
        self.time = time
        self.time2dt = time2dt

    def __call__(self, x, pos=None):
        i = int(x)
        if i >= len(self.time) or i < 0: return "undef"
        return self.time2dt(self.time[i]).strftime("%H:%M:%S")


class CopyLocator(mpl.ticker.Locator):
    def __init__(self, axis):
        self.model_axis = axis

    def __call__(self):
        return self.model_axis.get_majorticklocs()


class SciFormatter(mpl.ticker.Formatter):
    def __call__(self, x, pos=None):
        if x == 0.0: return "0.0"
        y = log(abs(x), 10)
        n = int(floor(y))
        if n < -1 or n > 2: return "%.1fx10$^{%d}$" % (x/10**n, n)
        else: return "%.1f" % (x,)

class HorizontalExtent(object):
    TYPE_NONE = 0
    TYPE_ALONG_TRACK = 1
    TYPE_ALONG_TRACK_ACROSS_TRACK = 2
    TYPE_ABSOLUTE_TIME = 3
    TYPE_RELATIVE_TIME = 4
    TYPE_LON_LAT = 5

    extent_type = TYPE_NONE

    along_track = [0, -1]
    across_track = [0, -1]
    absolute_time = [None, None] # [dt.time(), dt.time()]
    relative_time = [None, None] # [dt.timedelta(), dt.timedelta()]
    lon = [-180, 180]
    lat = [-90, 90]


class Options(object):
    """This class holds command-line options."""
    hextent = HorizontalExtent()
    fnames = []
    vextent = np.array((float("-infinity"), float("infinity")), dtype=np.float64)
    resolution = None
    aspect = 14.0
    dpi = 300
    outfname = "ccplot.png"
    plot_type = None
    print_info_only = False
    cmapfname = None
    modis_band = 1
    modis_band_mode = BAND_MODE_RADIANCE
    projection = "cyl"
    radius = None
    proj_opts = ProjOpts()
    plot_opts = PlotOpts()


#
# Functions.
#

def report_memory():
    pid = os.getpid()
    a2 = os.popen("ps -p %d -o rss,vsz,%%mem" % pid).readlines()
    print(("MEMORY:", a2[1]))
    return int(a2[1].split()[1])


def warn(s):
    global program_name
    sys.stderr.write("%s: Warning: %s\n" % (program_name, s))


def info(s):
    global verbose
    if verbose: print(s)


def autodetect(product):
    """Autodetect product type. Recognition is done by feature detection.
    Supported types:

        calipso-profile         CALIPSO profile products
        calipso-layer           CALIPSO layer products
        cloudsat-2b-geoprof     CloudSat 2B-GEOPROF
        modis-swath-l1b         MODIS L1B Swath
    """
    # Try CALIPSO.
    if b"Longitude" in product and b"Latitude" in product:
        try:
            product[b"Layer_Base_Altitude"]
            product[b"Layer_Top_Altitude"]
            product[b"Number_Layers_Found"]
            return "calipso-layer"
        except:
            pass
        try:
            product[b"metadata"][b"Lidar_Data_Altitudes"]
            return "calipso-profile"
        except KeyError:
            pass

    # Try CloudSat.
    if b"2B-GEOPROF" in product:
        datasets = (b"Profile_time", b"Latitude", b"Longitude", b"Height")
        if all(ds in product[b"2B-GEOPROF"] for ds in datasets):
            return "cloudsat-2b-geoprof"

    # Try MODIS.
    if b"MODIS_SWATH_Type_L1B" in product:
        try:
            product[b"MODIS_SWATH_Type_L1B"][b"Latitude"]
            product[b"MODIS_SWATH_Type_L1B"][b"Longitude"]
            return "modis-swath-l1b"
        except:
            pass

    return None

def norm_index(x, a, b):
    if x > b: return b
    if x < a: x += b
    if x < a: return a
    return x

def modis_band_wavelength(band):
    global MODIS_WAVELENGTHS
    return MODIS_WAVELENGTHS[int(band)-1]

def radiance2temp(L, lamb):
    """Converts radiace to temperature by inverse Planck's law.

    Arguments:
        L       -- radiance in W m^-2 m^-1
        lamb    -- wavelength in m

    Returns:
        Temerature in K.
    """
    global PLANCK_C1, PLANCK_C2
    return PLANCK_C2 / (lamb * np.log(PLANCK_C1 / (lamb**5 * L * 1E6) + 1))


def version():
    """Prints version information and exits with 0."""
    global __version__
    print("""\
ccplot {version}

Third-party libraries:
matplotlib {mpl_version}
cartopy {cartopy_version}

Copyright (c) 2009-2023 Peter Kuma.
This software is provided under the terms of a 2-clause BSD licence.\
""".format(
        version=__version__,
        mpl_version=mpl.__version__,
        cartopy_version=cartopy.__version__
    ))
    sys.exit(0)


def usage():
    """Prints usage information and exits the program with return value of 1."""
    global program_name
    sys.stderr.write("Usage: %s [OPTION]... TYPE FILE...\n" % program_name)
    sys.stderr.write("       %s -i FILE\n" % program_name)
    sys.stderr.write("       %s -V\n" % program_name)
    sys.stderr.write("Try `%s -h' for more information.\n" % program_name)
    sys.exit(1)


def help_and_exit():
    """Prints help and exits the program with return value of 0."""
    global program_name

    sys.stderr.write("\
%s: [OPTION]... TYPE FILE...\n\
%s: -i FILE\n\
%s: -V\n\
\n\
Plot data from CloudSat, CALIPSO and Aqua MODIS product files.\n\
Example: %s -c calipso.cmap -x 11000..13000 -y 0..25000 -o out.png calipso532 \
CAL_LID_L1-Prov-V2-01.2006-08-12T19-15-34ZD.hdf\n\
\n\
Where OPTION is one of:\n\
  -a RATIO                      aspect ratio of profile and layer plots in\n\
                                km horizontal per km vertical\n\
  -c FILE                       colormap file\n\
  -d DPI                        DPI of the output file\n\
  -h                            print help information and exit\n\
  -i FILE                       print information about FILE\n\
  -m BAND                       MODIS band (e.g. r1 for reflectance band 1,\n\
                                x31 for radiance band 31)\n\
  -o OUTFILE                    output file, type is determined by extension\n\
  -p PROJECTION[:PROJOPTS]      projection type and options\n\
  -r RADIUS                     interpolation radius\n\
  -v                            verbose mode\n\
  -V                            print version information and exit\n\
  -x FROM..TO[,FROM..TO]        horizontal extent\n\
  -y FROM..TO                   vertical extent in meters\n\
  -z OPTION=VAL[,OPTION=VAL]    list of option-value pairs\n\
\n\
OPTION is one of:\n\
  Use -z help for a list of available options. \n\
\n\
PROJECTION is one of:\n\
  Use -p help for a list of available projections.\n\
\n\
PROJOPTS is a list of option value pairs, where option is one of:\n\
  boudinglat\n\
  lat_0\n\
  lat_1\n\
  lat_2\n\
  lat_ts\n\
  lon_0\n\
\n\
TYPE is one of:\n\
  cloudsat-reflec\n\
  calipso532\n\
  calipso532p\n\
  calipso1064\n\
  calipso-cratio\n\
  calipso-dratio\n\
  calipso532-layer\n\
  calipso1064-layer\n\
  calipso-cratio-layer\n\
  calipso-dratio-layer\n\
  calipso-temperature-layer\n\
  orbit\n\
  orbit-clipped\n\
\n\
FILE is a CloudSat or Aqua MODIS HDF-EOS2 file, or a CALIPSO HDF4 file.\n\
\n\
Report bugs to <ccplot-general@lists.sourceforge.net>.\n" % \
    (program_name, program_name, program_name, program_name))

    sys.exit(0)


def help_options():
    print("\
cbspacing\n\
coastlinescolor\n\
coastlineslw\n\
countriescolor\n\
countrieslw\n\
drawcoastlines\n\
drawcountries\n\
drawlakes\n\
drawlsmask\n\
drawmeridians\n\
drawminormeridians\n\
drawminorparallels\n\
drawparallels\n\
fontsize\n\
landcolor\n\
majormeridianscolor\n\
majormeridianslw\n\
majorparallelscolor\n\
majorparallelslw\n\
mapres\n\
meridiansbase\n\
minormeridianscolor\n\
minormeridianslw\n\
minorparallelscolor\n\
minorparallelslw\n\
nminormeridians\n\
nminorparallels\n\
padding\n\
parallelsbase\n\
plotheight\n\
trajcolors\n\
title\n\
trajlws\n\
trajnminorticks\n\
trajticks\n\
watercolor")
    sys.exit(0)


def help_projections():
    print("\n".join(["%s\t%s" % (p[0], p[2]) for p in PROJECTIONS]))
    sys.exit(0)


def parse_extent(text):
    """"Parses extent in format from..to or from..to,from..to and returns
    an instance of class HorizontalExtent. Raises ValueError on parsing
    error.

    Arguments:
        text -- text to be parsed

    Returns:
        Instance of HorizontalExtent.
    """
    e = HorizontalExtent()

    # Match longitude/latitude in the form
    # lon{E|W}..lon{E|W},lat{S|N}..lat{S|N}
    r1 = re.compile(r"^(\d+(?:\.\d+)?)(E|W)\.\.(\d+(?:\.\d+)?)(E|W),(\d+(?:\.\d+)?)(S|N)\.\.(\d+(?:\.\d+)?)(S|N)$")
    m1 = r1.match(text)

    # Match longitude/latitude in the form
    # lat{S|N}..lat{S|N},lon{E|W}..lon{E|W}
    r1_rev = re.compile(r"^(\d+(?:\.\d+)?)(S|N)\.\.(\d+(?:\.\d+)?)(S|N),(\d+(?:\.\d+)?)(E|W)\.\.(\d+(?:\.\d+)?)(E|W)$")
    m1_rev = r1_rev.match(text)

    # Match absolute time in format hour:min[:sec]..hour:min[:sec].
    r2 = re.compile(r"^(\d?\d):(\d\d)(?::(\d\d))?\.\.(\d?\d):(\d\d)(?::(\d\d))?$")
    m2 = r2.match(text)

    # Match relative time in format +/-[hour:]min:sec..+/-[hour:]min:sec.
    r3 = re.compile(r"^(\+|-)(?:(\d+):)?(\d?\d):(\d\d)\.\.(\+|-)(?:(\d+):)?(\d?\d):(\d\d)$")
    m3 = r3.match(text)

    # Match along_track,across_track, i.e NUM..NUM,NUM..NUM.
    r4 = re.compile(r"^((?:\+|-)?\d+)\.\.((?:\+|-)?\d+),((?:\+|-)?\d+)\.\.((?:\+|-)?\d+)$")
    m4 = r4.match(text)

    # Match along_track, i.e NUM..NUM.
    r5 = re.compile(r"^((?:\+|-)?\d+)\.\.((?:\+|-)?\d+)$")
    m5 = r5.match(text)

    if m1 != None: # Match longitude,latitude.
        gs = m1.groups()
        e.extent_type = HorizontalExtent.TYPE_LON_LAT
        e.lon = [float(gs[0])*(int(gs[1]=="E")*2-1),
                 float(gs[2])*(int(gs[3]=="E")*2-1)]
        e.lat = [float(gs[4])*(int(gs[5]=="N")*2-1),
                 float(gs[6])*(int(gs[7]=="N")*2-1)]

    elif m1_rev != None: # Match latitude,longitude.
        gs = m1_rev.groups()
        e.extent_type = HorizontalExtent.TYPE_LON_LAT
        e.lat = [float(gs[0])*(int(gs[1]=="N")*2-1),
                 float(gs[2])*(int(gs[3]=="N")*2-1)]
        e.lon = [float(gs[4])*(int(gs[5]=="E")*2-1),
                 float(gs[6])*(int(gs[7]=="E")*2-1)]

    elif m2 != None: # Match absolute time.
        gs = m2.groups()
        e.extent_type = HorizontalExtent.TYPE_ABSOLUTE_TIME
        for k in (0, 3):
            hours = int(gs[k]) if gs[k] != None else 0
            minutes = int(gs[k+1]) if gs[k+1] != None else 0
            seconds = int(gs[k+2]) if gs[k+2] != None else 0
            if hours > 23 or minutes > 59 or seconds > 59:
                raise ValueError
            e.absolute_time[int(k//3)] = dt.time(hours, minutes, seconds)

    elif m3 != None: # Match relative time.
        gs = m3.groups()
        e.extent_type = HorizontalExtent.TYPE_RELATIVE_TIME
        for k in (0, 4):
            sign = -1 if gs[k] == "-" else 1
            hours = int(gs[k+1]) if gs[k+1] != None else 0
            minutes = int(gs[k+2]) if gs[k+2] != None else 0
            seconds = int(gs[k+3]) if gs[k+3] != None else 0
            if minutes > 59 or seconds > 59: raise ValueError
            e.relative_time[k//4] = sign*dt.timedelta(0, seconds,
                                                     0, 0, minutes, hours)

    elif m4 != None: # Match along_track,across_track.
        gs = m4.groups()
        e.extent_type = HorizontalExtent.TYPE_ALONG_TRACK_ACROSS_TRACK
        e.along_track = [int(gs[0]), int(gs[1])]
        e.across_track = [int(gs[2]), int(gs[3])]

    elif m5 != None: # Match along_track.
        gs = m5.groups()
        e.extent_type = HorizontalExtent.TYPE_ALONG_TRACK
        e.along_track = [int(gs[0]), int(gs[1])]

    else:
        raise ValueError

    if e.lon[0] < -180.0: e.lon[0] = -180.0
    if e.lon[0] > 180.0: e.lon[0] = 180.0

    if e.lon[1] < -180.0: e.lon[1] = -180.0
    if e.lon[1] > 180.0: e.lon[1] = 180.0

    if e.lat[0] < -90.0: e.lat[0] = -90.0
    if e.lat[0] > 90.0: e.lat[0] = 90.0

    if e.lat[1] < -90.0: e.lat[1] = -90.0
    if e.lat[1] > 90.0: e.lat[1] = 90.0

    if e.lon[0] >= e.lon[1]: e.lon.reverse()
    if e.lat[0] >= e.lat[1]: e.lat.reverse()

    return e


def parse_options(argv):
    """Parses command-line arguments.

    Arguments:
        argv -- array of command-line arguments

    Returns:
        instance of Options
    """
    opts = Options()

    if len(argv) < 2: usage()
    if argv[1] == "-h" and len(argv) == 2: help_and_exit()
    if argv[1] == "-V" and len(argv) == 2: version()

    if argv[1] == "-i" and len(argv) > 2:
        opts.fnames = argv[2:]
        opts.print_info_only = True
        return opts

    try: cmdopts, args = getopt.getopt(argv[1:], "a:c:d:m:o:p:r:vx:y:z:")
    except getopt.error: usage()

    for o, a in cmdopts:
        try:
            if o == "-a":
                opts.aspect = float(a)
                if opts.aspect <= 0.0: raise ValueError
            elif o == "-c": opts.cmapfname = a
            elif o == "-d":
                opts.dpi = int(a)
                if opts.dpi <= 0: raise ValueError
            elif o == "-m":
                if a[0] == "r": opts.modis_band_mode = BAND_MODE_REFLECTANCE
                elif a[0] == "x": opts.modis_band_mode = BAND_MODE_RADIANCE
                else: raise ValueError
                if a[-2:] == "hi":
                    opts.modis_band = int(a[1:-2]) + 0.5
                elif a[-2:] == "lo":
                    opts.modis_band = int(a[1:-2])
                else:
                    opts.modis_band = int(a[1:])
            elif o == "-o": opts.outfname = a
            elif o == "-p":
                if a == "help": help_projections()

                opts.projection,s,opts_str  = a.partition(":")

                parts = opts_str.split(",")
                for p in parts:
                    if p == "": continue
                    opt,s,val = p.partition("=")
                    opts.proj_opts.setopt(opt, val)

                if opts.projection not in SUPPORTED_PROJECTIONS:
                    raise ValueError
            elif o == "-r":
                opts.radius = int(a)
                if opts.radius < 0: raise ValueError
            elif o == "-v":
                global verbose
                verbose = True
                warnings.filterwarnings("default")
            elif o == "-y":
                parts = a.partition("..")
                if parts[0] != "": opts.vextent[0] = int(parts[0])
                if parts[2] != "": opts.vextent[1] = int(parts[2])
            elif o == "-x":
                opts.hextent = parse_extent(a)
            elif o == "-z":
                if a == "help": help_options()
                parts = a.split(",")
                for p in parts:
                    opt,s,val = p.partition("=")
                    opts.plot_opts.setopt(opt, val)
        except ValueError as err:
            if err != None:
                fail("Invalid argument passed to %s: %s" % (o, err))
            else:
                fail("Invalid argument passed to %s" % o)
        except KeyError:
            fail("Invalid argument passed to %s" % o)

    if len(args) < 2: usage()
    opts.plot_type = args[0]
    opts.fnames = args[1:]

    return opts


def loadcolormap(filename, name):
    """"Returns a tuple of matplotlib colormap, matplotlib norm,
    and a list of ticks loaded from the file filename in format:

    BOUNDS
    from1 to1 step1
    from2 to2 step2
    ...

    TICKS
    from1 to1 step1
    from2 to2 step2

    COLORS
    r1 g1 b1
    r2 g2 b2
    ...

    UNDER_OVER_BAD_COLORS
    ro go bo
    ru gu bu
    rb gb bb

    Where fromn, ton, stepn are floating point numbers as would be supplied
    to numpy.arange, and rn, gn, bn are the color components the n-th color
    stripe. Components are expected to be in base10 format (0-255).
    UNDER_OVER_BAD_COLORS section specifies colors to be used for
    over, under and bad (masked) values in that order.

    Arguments:
        filename    -- name of the colormap file
        name        -- name for the matplotlib colormap object

    Returns:
        A tuple of: instance of ListedColormap, instance of BoundaryNorm, ticks.
    """
    global CCPLOT_CMAP_PATH

    bounds = []
    ticks = []
    rgbarray = []
    specials = []
    mode = "COLORS"

    fp = None
    if filename.startswith("/") or \
       filename.startswith("./") or \
       filename.startswith("../"):
        try:
            fp = open(filename, "r")
        except IOError as err: fail(err)
    else:
        for path in CCPLOT_CMAP_PATH.split(":"):
            try:
                fp = open(os.path.join(path, filename), "r")
            except IOError as err: continue
            break
    if fp == None: fail("%s: File not found" % filename)

    try:
        lines = fp.readlines()
        for n, s in enumerate(lines):
            s = s.strip()
            if len(s) == 0: continue
            if s in ("BOUNDS", "TICKS", "COLORS", "UNDER_OVER_BAD_COLORS"):
                mode = s
                continue

            a = s.split()
            if len(a) not in (3, 4):
                raise ValueError("Invalid number of fields")

            if mode == "BOUNDS":
                bounds += list(np.arange(float(a[0]), float(a[1]), float(a[2])))
            elif mode == "TICKS":
                ticks += list(np.arange(float(a[0]), float(a[1]), float(a[2])))
            elif mode == "COLORS":
                rgba = [int(c)/256.0 for c in a]
                if len(rgba) == 3: rgba.append(1)
                rgbarray.append(rgba)
            elif mode == "UNDER_OVER_BAD_COLORS":
                rgba = [int(c)/256.0 for c in a]
                if len(rgba) == 3: rgba.append(1)
                specials.append(rgba)

    except IOError as err:
        fail(err)
    except ValueError as err:
        fail("Error reading `%s' on line %d: %s" % (filename, n+1, err))

    if (len(rgbarray) > 0):
        colormap = mpl.colors.ListedColormap(rgbarray, name)
        try:
            colormap.set_under(specials[0][:3], specials[0][3])
            colormap.set_over(specials[1][:3], specials[1][3])
            colormap.set_bad(specials[2][:3], specials[2][3])
        except IndexError: pass
    else:
        colormap = None

    if len(bounds) == 0:
        norm = None
    else:
        norm = mpl.colors.BoundaryNorm(bounds, colormap.N)
    if len(ticks) == 0: ticks = None
    return (colormap, norm, ticks)


def print_info(product):
    """Print information about a product."""
    filetype = autodetect(product)
    name = None
    subtype = None
    time = None
    height = None
    nray = None
    nbin = None
    nlayers = None
    lon = None
    lat = None

    # CloudSat.
    if filetype == "cloudsat-2b-geoprof":
        name = "CloudSat"
        subtype = "2B-GEOPROF"
        group = product[b"2B-GEOPROF"]
        time = group[b"Profile_time"]
        lat = group[b"Latitude"][:]
        lon = group[b"Longitude"][:]
        height = group[b"Height"][0][::-1]
        st = group.attributes[b"start_time"]
        start_time = dt.datetime.strptime(sdecode(st), "%Y%m%d%H%M%S")
        time2dt = lambda t: cloudsat_time2dt(t, start_time)
        nray = time.shape[0]
        nbin = height.shape[0]
    # CALIPSO common.
    elif filetype in ("calipso-profile", "calipso-layer"):
        name = "CALIPSO"
        lat = product[b"Latitude"][:, 0]
        lon = product[b"Longitude"][:, 0]
        time = product[b"Profile_UTC_Time"][:, 0]
        time2dt = calipso_time2dt
        nray = len(time)
        # CALIPSO profile.
        if filetype == "calipso-profile":
            subtype = "profile"
            height = product[b"metadata"][b"Lidar_Data_Altitudes"][::-1]*1000
            nbin = len(height)
        # CALIPSO layer.
        if filetype == "calipso-layer":
            subtype = "layer"
            nlayers = product[b"Number_Layers_Found"][:].max()
    # MODIS.
    elif filetype == "modis-swath-l1b":
        name = "MODIS"
        subtype = "Swath L1B"
        lon = product[b"MODIS_SWATH_Type_L1B"][b"Longitude"][:, 0]
        lat = product[b"MODIS_SWATH_Type_L1B"][b"Latitude"][:, 0]
    else:
        fail("Unsupported product file")

    # Print information.
    if name is not None:
        print("Type: %s" % name)
    if subtype is not None:
        print("Subtype: %s" % subtype)
    if time is not None:
        t1 = time2dt(time[0]).strftime("%Y-%m-%d %H:%M:%S")
        t2 = time2dt(time[-1]).strftime("%Y-%m-%d %H:%M:%S")
        print("Time: %s, %s" % (t1, t2))
    if height is not None:
        print("Height: %dm, %dm" % (height[0], height[-1]))
    if nray is not None:
        print("nray: %d" % nray)
    if nbin is not None:
        print("nbin: %d" % nbin)
    if nlayers is not None:
        print("nlayers: %d" % nlayers)
    if lon is not None and lat is not None:
        print("Longitude: %s, %s" % (lon2str(np.min(lon)), lon2str(np.max(lon))))
        print("Latitude: %s, %s" % (lat2str(np.min(lat)), lat2str(np.max(lat))))


def calipso_time2dt(time, start_time=None):
    """Converts a float in format yymmdd.ffffffff to a instance of python
    datetime class.

    Arguments:
        time        -- float in format yymmdd.ffffffff
        start_time  -- ignored

    Returns:
        An instance of datetime.
    """
    d = int(time % 100)
    m = int((time-d) % 10000)
    y = int(time-m-d)
    return dt.datetime(2000 + y//10000, m//100, d) + dt.timedelta(time % 1)


def cloudsat_time2dt(time, start_time):
    """Converts time in seconds to a instance of python datetime class.

    Arguments:
        time        -- seconds from start_time
        start_time  -- python datetime

    Returns:
        An instance of datetime.
    """
    return start_time + dt.timedelta(0, float(time))


def fit_colorbar(fig, axes, aspect=0.03, space=0.4, padding=0.0):
    """Creates new axes for a colorbar at the expense of main axes.

    Arguments:
        fig     -- an instance of mpl.Figure
        axes    -- an instance of mpl.Axes
        aspect  -- colorbar axes aspect ratio

    Returns:
        An instance of mpl.Axes.
    """
    x, y, width, height = get_axes_bounds(fig, axes)
    return new_axes(fig, x + width + space, y, aspect*height, height,
                    padding=padding)


def stripstr(s1, s2):
    i = s1.rfind(s2)
    if i == -1: return s1
    else: return s1[:i]


def lon2str(lonf, degree=""):
    if lonf >= 0.0: return "%.2f%sE" % (lonf, degree)
    else: return "%.2f%sW" % (-lonf, degree)


def lat2str(latf, degree=""):
    if latf >= 0.0: return "%.2f%sN" % (latf, degree)
    else: return "%.2f%sS" % (-latf, degree)


def setup_lonlat_axes(fig, axes, lon, lat):
    @mpl.ticker.FuncFormatter
    def lonlat_formatter(x, pos=None):
        i = int(x)
        if x < 0 or x >= len(lon): return ""
        return "%s\n%s" % (lon2str(lon[i], "$\degree$"), \
                           lat2str(lat[i], "$\degree$"))

    llaxes = axes.twiny()
    llaxes.set_xlim(axes.get_xlim())
    llaxes.xaxis.set_major_locator(CopyLocator(axes.xaxis))

    for tick in llaxes.xaxis.get_major_ticks():
        tick.tick1line.set_visible(False)
        tick.label1.set_visible(False)
        tick.tick2line.set_visible(True)
        tick.label2.set_visible(True)

    for line in llaxes.xaxis.get_ticklines():
        line.set_marker(mpl.lines.TICKUP)

    for label in llaxes.xaxis.get_ticklabels():
        label.set_y(label.get_position()[1] + 0.005)

    llaxes.xaxis.set_major_formatter(lonlat_formatter)


def get_axes_bounds(fig, axes):
    figw, figh = fig.get_size_inches()
    xrel, yrel, wrel, hrel = axes.get_position(True).bounds
    return figw*xrel, figh*(1-yrel-hrel), figw*wrel, figh*hrel


def resize_figure(fig, figw, figh):
    figw_old, figh_old = fig.get_size_inches()

    fig.set_size_inches(figw, figh)

    xratio = figw_old/figw
    yratio = figh_old/figh

    for ax in fig.axes:
        xrel, yrel, wrel, hrel = ax.get_position(True).bounds
        yrel = 1-yrel
        ax.set_position([xrel*xratio, 1-yrel*yratio, wrel*xratio, hrel*yratio])


def expand_axes(fig, axes, width, height, padding):
    figw_old, figh_old = fig.get_size_inches()
    x, y, w, h = get_axes_bounds(fig, axes)

    figw = max(figw_old, x + width + padding)
    figh = max(figh_old, y + height + padding)

    resize_figure(fig, figw, figh)
    x, y, w, h = get_axes_bounds(fig, axes)
    axes.set_position([x/figw, 1-(y+height)/figh, width/figw, height/figh])


def new_axes(fig, x, y, width, height, padding=1.0):
    figw_old, figh_old = fig.get_size_inches()

    figw = max(figw_old, x + width + padding)
    figh = max(figh_old, y + height + padding)

    resize_figure(fig, figw, figh)
    return fig.add_axes([x/figw, 1-(y+height)/figh, width/figw, height/figh])


def time2ray(t, time, time2dt):
    """Returns index i of 1-dimensional array time whose value of
    time2dt(time[i]) best matches dt.time instance t. Returns -1 if time
    is empty.
    """

    a = 0
    b = time.shape[0]-1
    i = 0

    if time.shape[0] == 0: return -1

    if isinstance(t, dt.timedelta):
        if t < dt.timedelta(0): ref_dt = time2dt(time[-1]) + t
        else: ref_dt = time2dt(time[0]) + t
    else: # dt.time expected.
        date0 = time2dt(time[0]).date()
        time0 = time2dt(time[0]).time()
        if t < time0: ref_dt = dt.datetime.combine(date0 + dt.timedelta(1), t)
        else: ref_dt = dt.datetime.combine(date0, t)

    # Simple binary search.
    # TODO: Search by taking differentials would be much faster.
    while a < b:
        i = int((a + b)/2)
        dti = time2dt(time[i])
        if ref_dt < dti:
            b = i
        else:
            a = i+1
    try:
        if abs(ref_dt - time2dt(time[i-1])) < abs(ref_dt-dti): return i - 1
        if abs(ref_dt - time2dt(time[i+1])) < abs(ref_dt-dti): return i + 1
    except KeyError: pass
    return i


def lonlat2ray(lonextent, latextent, lon, lat):
    mask = (lon > lonextent[0]) & (lon < lonextent[1]) & \
           (lat > latextent[0]) & (lat < latextent[1])

    e1 = e2 = 0

    i = 0
    n = len(mask)
    while i < n and not mask[i]:
        e1 = i
        i = i + 1
    while i < n and mask[i]:
        e2 = i
        i = i + 1

    return e1, e2


def figure_title(fig, opts, title):
    if opts.title != None:
        title = opts.title
    figw, figh = fig.get_size_inches()
    fig.text(opts.padding/figw, 1-opts.padding/figh/3.0, title, weight="bold")


def plot_profile(what, fname, product, fig, axes, hextent=HorizontalExtent(),
              vextent=np.array((float("-infinity"), float("infinity"))),
              aspect=1410.0, colormap=None, norm=None, ticks=None, radius=None,
              opts=PlotOpts()):
    """Plot profile or layer as specified by argument what.

    Arguments:
        what            -- plot type string
        fname           -- file name
        product         -- product file to read data from
        fig             -- matplotlib Figure instance to draw onto
        axes            -- matplotlib Axes instance to draw onto
        hextent         -- an instance of HorizontalExtent
        vextent         -- vertical extent, a pair of low and high boundary
                           in meters
        aspect          -- aspect ratio in s per km
        colormap        -- matplotlib Colormap instance
        norm            -- matplotlib Normalize instance
        ticks           -- a list of ticks to be drawn on colorbar
    """
    global ATRAIN_SPEED, PROFILE_BINHEIGHT

    info = DATASETS.get(what, {
        "datasets": [what.encode('utf-8')],
    })
    filetype = autodetect(product)
    product_name = None
    units = None
    title = None
    name = None
    elevation = None

    # CloudSat.
    if filetype == "cloudsat-2b-geoprof":
        product_name = "CloudSat Profile"
        try:
            group = product[b"2B-GEOPROF"]
            start_time = group.attributes[b"start_time"]
            time = group[b"Profile_time"]
            lat = group[b"Latitude"]
            lon = group[b"Longitude"]
            height = group[b"Height"]
            datasets = [group[name] for name in info["datasets"]]
        except KeyError as e:
            fail("Field \"%s\" not found" % e.args)
        nray = time.shape[0]
        nbin = height.shape[1]
        # If we have single dataset, adopt its title and units.
        if len(datasets) == 1:
            title = sdecode(datasets[0].attributes.get(b"long_name"))
            units = sdecode(datasets[0].attributes.get(b"units"))
        for (key, ds) in enumerate(datasets):
            data = ds[::].astype('float32')
            if b"_FillValue" in ds.attributes:
                data = np.ma.masked_equal(data, ds.attributes[b"_FillValue"])
            if b"missing" in ds.attributes:
                data = np.ma.masked_equal(data, ds.attributes[b"missing"])
            factor = ds.attributes.get(b"factor", 1)
            offset = ds.attributes.get(b"offset", 0)
            data -= offset
            data *= 1.0/factor
            datasets[key] = data

    # CALIPSO.
    if filetype in ("calipso-profile", "calipso-layer"):
        try:
            time = product[b"Profile_UTC_Time"][:, 0]
            lat = product[b"Latitude"][:, 0]
            lon = product[b"Longitude"][:, 0]
            datasets = [product[name] for name in info["datasets"]]
        except KeyError as e:
            fail("Field \"%s\" not found" % e.args)
        start_time = None
        nray = time.shape[0]
        # If we have single dataset, adopt its title and units.
        if len(datasets) == 1:
            title = sdecode(info["datasets"][0]).replace("_", " ")
            units = datasets[0].attributes.get(b"units")
        for (key, ds) in enumerate(datasets):
            data = ds[::]
            data = np.ma.masked_equal(data, -9999)
            if b"fillvalue" in ds.attributes:
                data = np.ma.masked_equal(data, ds.attributes[b"fillvalue"])
            datasets[key] = data

    # CALIPSO profile.
    if filetype == "calipso-profile":
        product_name = "CALIPSO Profile"
        try:
            height = product[b"metadata"][b"Lidar_Data_Altitudes"]*1000
        except KeyError as e:
            fail("Field \"%s\" not found" % e.args)
        try:
            elevation = product[b"Surface_Elevation"]
        except KeyError as e:
            elevation = None
        nbin = len(height)

    # CALIPSO layer.
    if filetype == "calipso-layer":
        product_name = "CALIPSO Layer"
        try:
            topalt = product[b"Layer_Top_Altitude"]
            basealt = product[b"Layer_Base_Altitude"]
            nlayer = product[b"Number_Layers_Found"]
        except KeyError as e:
            fail("Field \"%s\" not found" % e.args)
        topalt = np.ma.masked_equal(topalt[::], -9999)
        basealt = np.ma.masked_equal(basealt[::], -9999)
        try:
            valid_range = nlayer.attributes[b"valid_range"]
            try:
                nbin = int(valid_range.split(b"...")[1])
            except IndexError as ValueError:
                warn("Invalid valid_range attribute \"%s\", assuming maximum number of layers 10" % valid_range)
                nbin = 10  # Fall back to 10.
        except KeyError:
            nbin = 10  # Fall back to 10.

    # Override title and units if in info.
    if "title" in info:
        title = info["title"]
    if "units" in info:
        units = info["units"]

    # Make plot name from title and units.
    if title is not None:
        if units is not None:
            name = "%s (%s)" % (title, units)
        else:
            name = title

    # Apply common factor and offset.
    for (key, ds) in enumerate(datasets):
        if "offset" in info:
            ds -= info["offset"]
        if "factor" in info:
            ds *= 1.0/info["factor"]
        datasets[key] = ds

    # Check size of datasets.
    for ds in datasets:
        if ds.shape != (nray, nbin):
            fail("Dataset has shape %s, expected (%d, %d)" %
                 (ds.shape, nray, nbin))

    # Determine what time conversion function to apply. We need this now
    # in order to convert time extent (if set) to extent in rays.
    if what.startswith("cloudsat"):
        start_time_dt = dt.datetime.strptime(sdecode(start_time), "%Y%m%d%H%M%S")
        time2dt = lambda t: cloudsat_time2dt(t, start_time_dt)
    else: time2dt = calipso_time2dt

    if hextent.extent_type == HorizontalExtent.TYPE_ABSOLUTE_TIME:
        time_temp = time[:, 0] if len(time.shape) == 2 else time
        e1 = time2ray(hextent.absolute_time[0], time_temp, time2dt)
        e2 = time2ray(hextent.absolute_time[1], time_temp, time2dt)
        del time_temp
    elif hextent.extent_type == HorizontalExtent.TYPE_RELATIVE_TIME:
        time_temp = time[:, 0] if len(time.shape) == 2 else time
        e1 = time2ray(hextent.relative_time[0], time_temp, time2dt)
        e2 = time2ray(hextent.relative_time[1], time_temp, time2dt)
        del time_temp
    elif hextent.extent_type == HorizontalExtent.TYPE_LON_LAT:
        lon_temp = lon[:, 0] if len(lon.shape) == 2 else lon[:]
        lat_temp = lat[:, 0] if len(lat.shape) == 2 else lat[:]
        e1, e2 = lonlat2ray(hextent.lon, hextent.lat, lon_temp, lat_temp)
        del lon_temp, lat_temp
    elif hextent.extent_type == HorizontalExtent.TYPE_ALONG_TRACK:
        e1, e2 = hextent.along_track
    elif hextent.extent_type == HorizontalExtent.TYPE_NONE:
        e1 = 0
        e2 = -1
    else: fail("Extent type not supported by profile plots")

    e1 = norm_index(e1, 0, nray)
    e2 = norm_index(e2, 0, nray)
    e3 = 0
    e4 = -1
    if e1 >= e2: fail("Invalid extent")

    ve1, ve2 = vextent

    # Subsetting by extent.
    try:
        if what in ("calipso-cratio", "calipso-dratio"):
            data = datasets[1][e1:e2, e3:e4] / datasets[0][e1:e2, e3:e4]
        else:
            if filetype == "calipso-layer":
                data = datasets[0][e1:e2, :]
            else:
                data = datasets[0][e1:e2, e3:e4]

        if elevation is not None:
            elevation = elevation[e1:e2]

        time = time[e1:e2]
        lon = lon[e1:e2]
        lat = lat[e1:e2]

        if filetype == "calipso-layer":
            nlayer = nlayer[e1:e2, 0]
            basealt = basealt[e1:e2, :]
            topalt = topalt[e1:e2, :]
            if not np.isfinite(ve1):
                ve1 = np.min(basealt)*1000
            if not np.isfinite(ve2):
                ve2 = np.max(topalt)*1000
        else:
            if len(height.shape) == 2:
                height = height[e1:e2, e3:e4]
            else:
                height = height[e3:e4]
            if not np.isfinite(ve1):
                ve1 = np.min(height)
            if not np.isfinite(ve2):
                ve2 = np.max(height)

        # Fall back to default values.
        if not np.isfinite(ve1):
            ve1 = 0
        if not np.isfinite(ve2):
            ve2 = 20000

    except IndexError:
        fail("Invalid extent")

    if ve1 >= ve2: fail("Invalid vertical extent")
    if norm == None: norm = mpl.colors.Normalize(data.min(), data.max())

    #
    # Core data processing and plotting.
    #
    resolution = int(get_axes_bounds(fig, axes)[3]*fig.get_dpi())
    if filetype == "calipso-layer":
        data = cctk.layermap(
            data,
            nlayer.astype(np.uint8),
            basealt, topalt,
            (ve1*0.001, ve2*0.001, resolution),
            float("nan")
        )[:,::-1]
    else:
        # Profile products.
        X = np.arange(e1, e2, dtype=np.float32)
        if height.ndim == 1:
            Y = np.meshgrid(height, X)[0]
        else:
            Y = height
        if radius == None: radius = int(PROFILE_BINHEIGHT*resolution/(ve2-ve1))

        # Currently, only float32 is supported by interpolation routines.
        data = data.astype(np.float32)
        X = X.astype(np.float32)
        Y = Y.astype(np.float32)

        # Deprecated interpolation algorithm.
        # data = cctk.interpolate2d(data, X, Y,
        #     (0, e2 - e1, e2 - e1),
        #     (ve1, ve2, resolution),
        #     float("nan"), 0, radius
        # )

        data = ccplot.algorithms.interp2d_12(data, X, Y,
            e1, e2, e2 - e1,
            ve2, ve1, resolution
        )
    # Plot data.
    data = np.ma.masked_invalid(data)
    im = axes.imshow(data.T,
                     extent=(0, e2-e1, ve1*0.001, ve2*0.001),
                     cmap=colormap,
                     norm=norm,
                     interpolation='nearest',
    )
    axes.set_aspect("auto")

    if elevation is not None and opts.drawelev:
        line = mpl.lines.Line2D(np.arange(0, e2-e1), elevation,
                                color=opts.elevcolor, lw=opts.elevlw)
        axes.add_line(line)


    td = time2dt(time[-1]) - time2dt(time[0])
    nseconds = td.days*86400 + td.seconds
    if nseconds == 0: return
    x, y, width, height = get_axes_bounds(fig, axes)
    width = height/(aspect/(nseconds*ATRAIN_SPEED)*(ve2-ve1)*0.001)
    expand_axes(fig, axes, width, height, padding=opts.padding)
    figw, figh = fig.get_size_inches()
    #nlocs = int(width*1.5)

    # Time axis.
    axes.set_xlabel("Time (UTC)")
    axes.xaxis.set_minor_locator(TimeMinorLocator())
    axes.xaxis.set_major_locator(TimeLocator(width/(opts.fontsize/72.0*5), time, time2dt))
    axes.xaxis.set_major_formatter(TimeFormatter(time, time2dt))

    for line in axes.xaxis.get_ticklines() + axes.xaxis.get_minorticklines():
        line.set_marker(mpl.lines.TICKDOWN)

    for label in axes.xaxis.get_ticklabels():
        label.set_y(-0.05/figh)

    # Height axis.
    axes.set_ylabel("Altitude (km)")

    majorticksbases = np.array([0.5,   1,   2, 5])
    minorticksbases = np.array([0.1, 0.2, 0.5, 1])
    height_per_tick = (ve2-ve1)*0.001/(height/(opts.fontsize*2/72.0))
    i = np.argmin(np.abs(majorticksbases - height_per_tick))
    axes.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(minorticksbases[i]))
    axes.yaxis.set_major_locator(mpl.ticker.MultipleLocator(majorticksbases[i]))

    for label in axes.yaxis.get_ticklabels():
        label.set_x(-0.05/figw)

    for line in axes.yaxis.get_ticklines()+axes.yaxis.get_minorticklines():
        line.set_marker(mpl.lines.TICKLEFT)

    # Hide ticks on the top and right-hand side.
    for tick in axes.xaxis.get_major_ticks() + \
                axes.yaxis.get_major_ticks() + \
                axes.xaxis.get_minor_ticks() + \
                axes.yaxis.get_minor_ticks():
        tick.tick1line.set_visible(True)
        tick.label1.set_visible(True)
        tick.tick2line.set_visible(False)
        tick.label2.set_visible(False)

    # Colorbar.
    cbaxes = fit_colorbar(fig, axes, space=opts.cbspacing, padding=opts.padding)
    cb = fig.colorbar(im, ax=axes, cax=cbaxes, orientation="vertical",
                      extend="both", ticks=ticks, format=SciFormatter())

    cb.set_label(name)
    cb.ax.tick_params(direction="in")

    for label in cb.ax.get_yticklabels():
        label.set_fontsize(opts.cbfontsize)

    # Longitude/latitude.
    setup_lonlat_axes(fig, axes, lon, lat)


    title = "%s %s/%s" % (product_name,
                          time2dt(time[0]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                          time2dt(time[-1]).strftime("%Y-%m-%dT%H:%M:%SZ"))
    figure_title(fig, opts, title)


def plot_orbit(fnames, products, fig, axes,
    hextent=HorizontalExtent(),
    band=1, band_mode=BAND_MODE_RADIANCE, proj="cyl", proj_opts=ProjOpts(),
    clipped=False,
    colormap=None, norm=None,
    ticks=None, radius=None, opts=PlotOpts()):
    """Draws a map plot of a CloudSat and CALIPSO trajectories and MODIS swath.

    Arguments:
        products    -- a list of products
        fig         -- matplotlib Figure instance
        axes        -- matplotlib Axes instance
        hextent     -- an instance of HorizontalExtent
        band        -- band to plot (integer or 13.5 or 14.5 for high bands)
        band_mode   -- any of BAND_MODE_* constants
        proj        -- projection name
        clipped     -- clip map to MODIS swath
        colormap    -- matplotlib Colormap instance
        norm        -- matplotlib Normalize instance
        ticks       -- a list of ticks to be drawn on colorbar
    """

    info("Plotting orbit")

    titlea = []

    along_track_ext = (0, -1)
    across_track_ext = (0, -1)
    if hextent.extent_type == HorizontalExtent.TYPE_ALONG_TRACK:
        along_track_ext = hextent.along_track
    elif hextent.extent_type == HorizontalExtent.TYPE_ALONG_TRACK_ACROSS_TRACK:
        along_track_ext = hextent.along_track
        across_track_ext = hextent.across_track
    elif hextent.extent_type == HorizontalExtent.TYPE_LON_LAT:
        pass # Handled later.
    elif hextent.extent_type == HorizontalExtent.TYPE_NONE:
        pass
    else: fail("Extent type not supported by swath plots")

    # Search for a MODIS data file.
    modis_swath = None
    for fname, product in zip(fnames, products):
        info("Attempting to read MODIS swath from %s" % fname)
        if b"MODIS_SWATH_Type_L1B" in product:
            modis_swath = read_modis_swath(product, band, band_mode,
                                           along_track_ext, across_track_ext)
            break

    extent = None
    lon_0 = None
    lat_0 = None

    if hextent.extent_type == HorizontalExtent.TYPE_LON_LAT:
        lon_0 = np.average(hextent.lon)
        lat_0 = np.average(hextent.lat)
    elif modis_swath is not None and clipped:
        shape = modis_swath.lon.shape
        lon_0 = modis_swath.lon[int(shape[0]/2),int(shape[1]/2)]
        lat_0 = modis_swath.lat[int(shape[0]/2),int(shape[1]/2)]

    if proj_opts.lon_0 != None:
        lon_0 = proj_opts.lon_0

    if proj_opts.lat_0 != None:
        lat_0 = proj_opts.lat_0

    proj_name = PROJECTIONS[SUPPORTED_PROJECTIONS.index(proj)][1]
    proj_cls = getattr(ccrs, proj_name)
    proj_args = {}
    if lon_0 is not None:
        proj_args["central_longitude"] = lon_0
    if lat_0 is not None:
        proj_args["central_latitude"] = lat_0
    if proj_opts.lat_1 is not None and proj_opts.lat_2 is not None:
        proj_args["standard_parallels"] = (proj_opts.lat_1, proj_opts.lat_2)
    for key, arg in (
        ("lat_ts", "latitude_true_scale"),
        ("lat_ts", "true_scale_latitude"),
        ("cutoff", "cutoff"),
        ("k_0", "scale_factor"),
        ("h", "satellite_height"),
        ("sweep", "sweep_axis"),
        ("o_lon_p", "central_rotated_longitude"),
        ("o_lat_p", "pole_latitude"),
        ("zone", "zone"),
    ):
        if getattr(proj_opts, key) is not None:
            proj_args[arg] = getattr(proj_opts, key)
    if lon_0 is not None and proj == "ob_tran":
        proj_args["pole_longitude"] = lon_0 - 180 # See RotatedPole __init__.
    proj_args_allow = inspect.getfullargspec(proj_cls).args
    proj_args_deny = ["self", "globe"]
    proj_args = {k: v for k, v in proj_args.items()
        if k in proj_args_allow and k not in proj_args_deny}

    if proj == "utm" and "zone" not in proj_args:
        fail("UTM \"zone\" projection option is required")

    info("Initialising Cartopy")
    for k, v in proj_args.items():
        info("  %s = %s" % (k, str(v)))

    crs = proj_cls(**proj_args)
    geoaxes = fig.add_subplot(1, 1, 1, projection=crs)
    geoaxes.set_position(axes.get_position())
    fig.delaxes(axes)
    axes = geoaxes

    extent_xy = None
    extent_lonlat = None

    if modis_swath is not None and clipped:
        minorticks_base = 10000
        majorticks_base = 60000
        minorparallels = np.arange(-90, 90, 1)
        majorparallels = np.arange(-90, 90, 5)
        minormeridians = np.arange(-180, 180, 1)
        majormeridians = np.arange(-180, 180, 5)
        res = axes.projection.transform_points(ccrs.PlateCarree(),
            modis_swath.lon, modis_swath.lat)
        X, Y = res[:,:,0], res[:,:,1]
        extent_lonlat = None
        extent_xy = [X.min(), X.max(), Y.min(), Y.max()]

    else:
        minorticks_base = 60000
        majorticks_base = 300000
        minorparallels = np.arange(-90, 90, 10)
        majorparallels = np.arange(-90, 90, 30)
        minormeridians = np.arange(-180, 180, 10)
        majormeridians = np.arange(-180, 180, 30)
        extent_lonlat = {
            "merc": [-180, 180, -80, 80],
            "tmerc": [-80, 80, -90, 90],
            "npstere": [-180, 180, 60, 90],
            "spstere": [-180, 180, -90, -60],
        }.get(proj, None)
        extent_xy = None

    if proj == "npstere":
        minorparallels = np.arange(0, 80, 5)
        majorparallels = np.arange(0, 80, 10)
        minormeridians = np.arange(-180, 180, 10)
        majormeridians = np.arange(-180, 180, 30)
    if proj == "spstere":
        minorparallels = np.arange(-80, 0, 5)
        majorparallels = np.arange(-80, 0, 10)
        minormeridians = np.arange(-180, 180, 10)
        majormeridians = np.arange(-180, 180, 30)

    if opts.parallelsbase > 0:
        majorparallels = np.arange(-90, 90, opts.parallelsbase)
        if opts.nminorparallels > 0:
            minorparallels = np.arange(-90, 90,
                                       opts.parallelsbase/opts.nminorparallels)
        else:
            minorparallels = np.arange(-90, 90, opts.parallelsbase/2.0)

    if opts.meridiansbase > 0:
        majormeridians = np.arange(-180, 180, opts.meridiansbase)
        if opts.nminormeridians > 0:
            minormeridians = np.arange(-180, 180,
                                       opts.meridiansbase/opts.nminormeridians)
        else:
            minormeridians = np.arange(-180, 180, opts.meridiansbase/2.0)

    if hextent.extent_type == HorizontalExtent.TYPE_LON_LAT:
        # Determine projection parameters from the horizontal extent given.
        extent_lonlat = [
            min(hextent.lon), max(hextent.lon),
            min(hextent.lat), max(hextent.lat)
        ]
        extent_xy = None

    if opts.trajticks > 0:
        majorticks_base = opts.trajticks * 1000

    if opts.trajnminorticks == 0:
        minorticks_base = 0
    elif opts.trajnminorticks > 0:
        minorticks_base = int(majorticks_base / opts.trajnminorticks)

    # Plot map.
    if extent_xy is not None:
        axes.set_extent(extent_xy, crs=crs)
    elif extent_lonlat is not None:
        axes.set_extent(extent_lonlat, crs=ccrs.PlateCarree())
    else:
        axes.set_global()

    extent = axes.get_extent()
    aspect = (extent[1] - extent[0])/(extent[3] - extent[2])
    x, y, width, height = get_axes_bounds(fig, axes)
    expand_axes(fig, axes, height*aspect, height, \
        padding=opts.padding)

    coastline = cfeature.COASTLINE
    borders = cfeature.BORDERS
    land = cfeature.LAND
    ocean = cfeature.OCEAN
    lakes = cfeature.LAKES
    if opts.mapres is not None and opts.mapres != "auto":
        coastline = coastline.with_scale(opts.mapres)
        borders = borders.with_scale(opts.mapres)
        land = land.with_scale(opts.mapres)
        ocean = ocean.with_scale(opts.mapres)
        lakes = lakes.with_scale(opts.mapres)

    if opts.drawcoastlines:
        axes.add_feature(coastline,
            linewidth=opts.coastlineslw, edgecolor=opts.coastlinescolor)

    if opts.drawcountries:
        axes.add_feature(borders,
            linewidth=opts.countrieslw, edgecolor=opts.countriescolor)
    if opts.drawlsmask:
        axes.add_feature(land, color=opts.landcolor)
        axes.add_feature(ocean, color=opts.watercolor)
        if opts.drawlakes:
            axes.add_feature(lakes, color=opts.watercolor, zorder=-1)

    if packaging.version.parse(cartopy.__version__) >= \
       packaging.version.parse('0.18.0'):
        if opts.drawminorparallels:
             axes.gridlines(xlocs=[], ylocs=minorparallels,
                            linewidth=opts.minorparallelslw,
                            color=opts.minorparallelscolor)
        if opts.drawparallels:
            gl = axes.gridlines(xlocs=[], ylocs=majorparallels,
                            linewidth=opts.majorparallelslw,
                            color=opts.majorparallelscolor,
                            draw_labels=True)
            gl.left_labels = True
            gl.bottom_labels = True
            gl.right_labels = False
            gl.top_labels = False
        if opts.drawminormeridians:
             axes.gridlines(xlocs=minormeridians, ylocs=[],
                            linewidth=opts.minormeridianslw,
                            color=opts.minormeridianscolor)
        if opts.drawmeridians:
            gl = axes.gridlines(xlocs=majormeridians, ylocs=[],
                            linewidth=opts.majormeridianslw,
                            color=opts.majormeridianscolor,
                            draw_labels=True)
            gl.left_labels = True
            gl.bottom_labels = True
            gl.right_labels = False
            gl.top_labels = False
    else:
        if opts.drawminorparallels or opts.drawminormeridians:
             axes.gridlines(xlocs=minormeridians, ylocs=minorparallels,
                            linewidth=opts.minorparallelslw,
                            color=opts.minorparallelscolor)
        if opts.drawparallels or opts.drawmeridians:
            gl = axes.gridlines(xlocs=majormeridians, ylocs=majorparallels,
                            linewidth=opts.majorparallelslw,
                            color=opts.majorparallelscolor,
                            draw_labels=(proj in ("cyl", "merc")))
            gl.left_labels = True
            gl.bottom_labels = True
            gl.right_labels = False
            gl.top_labels = False

    # Plot swath.
    if modis_swath != None:
        info("Plotting swath")
        plot_swath(modis_swath, fig, axes, proj, colormap=colormap, norm=norm,
                   ticks=ticks, radius=radius, opts=opts)
        titlea += ["MODIS Swath"]

    info("Plotting trajectories")

    # Plot trajectories.
    j = 0
    for product in products:
        if b"MODIS_SWATH_Type_L1B" in product: continue
        hit = False
        try: # Try CALIPSO names.
            time = product[b"Profile_UTC_Time"][:, 0]
            lon = product[b"Longitude"][:, 0]
            lat = product[b"Latitude"][:, 0]
            time2dt = calipso_time2dt
            satellite = "CALIPSO"
            hit = True
        except (KeyError, IndexError): pass
        try: # Try CloudSat names.
            sw = product[b"2B-GEOPROF"]
            time = sw[b"Profile_time"][:]
            lon = sw[b"Longitude"][:]
            lat = sw[b"Latitude"][:]
            start_time = sw.attributes[b"start_time"]
            start_time_dt = dt.datetime.strptime(sdecode(start_time), "%Y%m%d%H%M%S")
            time2dt = lambda t: cloudsat_time2dt(t, start_time_dt)
            satellite = "CloudSat"
            hit = True
        except (AttributeError, KeyError, IndexError): pass

        if hit:
            lw = opts.trajlws[j % len(opts.trajlws)]
            color = opts.trajcolors[j % len(opts.trajcolors)]
            mask = plot_trajectory(fig, axes, lon, lat, time,
                time2dt, minorticks_base,
                majorticks_base, lw=lw, color=color)
            time_min = time_max = None
            for i in range(0, len(mask)):
                if mask[i]:
                    time_min = time2dt(time[i])
                    break
            for i in reversed(list(range(0, len(mask)))):
                if mask[i]:
                    time_max = time2dt(time[i])
                    break
            if time_min is not None and time_max is not None and \
                time_min < time_max:
                titlea += ["%s Trajectory %s/%s" % \
                           (satellite,
                            time_min.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            time_max.strftime("%Y-%m-%dT%H:%M:%SZ"))]
            j = j+1
        else: warn("%s: Unrecognized file, skipping" % fnames[i])

    # Plot title.
    title = ", ".join(titlea)
    figure_title(fig, opts, title)


def plot_trajectory(fig, axes, lon, lat, time, time2dt,
    minorticks_base, majorticks_base, lw=1.0, color="#000000"):

    #
    # Helper functions.
    #
    def drawtick(i, ticksize, tickwidth, text=None):
        ticksize_in = ticksize/72.0
        w_in, h_in = fig.get_size_inches()

        def t(x, y):
            return fig.transFigure.inverted().transform(
                axes.transData.transform((x, y)))*(w_in, h_in)

        if i == 0:
            dx, dy = t(X[1], Y[1]) - t(X[0], Y[0])
        elif i == nray-1:
            dx, dy = t(X[i], Y[i-1]) - t(X[i], Y[i-1])
        else:
            dx, dy = t(X[i+1], Y[i+1]) - t(X[i-1], Y[i-1])

        l = sqrt(dx**2 + dy**2)
        if (l == 0): v = np.array((ticksize_in, 0))
        else: v = np.array((dy, -dx))/l

        x, y = t(X[i], Y[i])

        trans = mpl.transforms.Affine2D().scale(1.0/w_in, 1.0/h_in) + \
            fig.transFigure

        line = mpl.lines.Line2D((x, x + v[0]*ticksize_in),
                                (y, y + v[1]*ticksize_in), transform=trans,
                                color="black", lw=tickwidth)
        axes.add_line(line)

        if text != None:
            doty = np.dot(v, (0, 1))
            dotx = np.dot(v, (1, 0))
            if dotx < -0.3: halign = "right"
            elif dotx > 0.3: halign = "left"
            else: halign = "center"

            if doty < -0.3: valign = "top"
            elif doty > 0.3: valign = "bottom"
            else: valign = "center"

            axes.text(x + v[0]*(ticksize_in*2),
                      y + v[1]*(ticksize_in*2),
                      text,
                      horizontalalignment=halign,
                      verticalalignment=valign,
                      transform=trans,
                      clip_on=True)

    nray = time.shape[0]
    time_from = time2dt(time[0])
    time_to = time2dt(time[-1])
    d = time_to - time_from
    # Delta time in milliseconds.
    time_delta = d.days*86400000 + d.seconds*1000 + d.microseconds/1000
    del d

    res = axes.projection.transform_points(ccrs.PlateCarree(), lon, lat)
    X, Y = res[:,0], res[:,1]
    xmin, xmax, ymin, ymax = axes.get_extent()
    mask = (X > xmin) & (X < xmax) & (Y > ymin) & (Y < ymax)

    if not mask.max(): return mask # Nothing to plot.

    # Plot trajectory ticks.
    ratio = 1.0*nray/time_delta if time_delta != 0 else 0
    offset = int(ratio*(-time_from.microsecond/1000.0-time_from.second*1000+100))
    if offset == 0: offset = -1 # For safety reasons.
    minorticks = np.empty(0, np.int64)
    majorticks = np.empty(0, np.int64)
    if minorticks_base > 0:
        minorticks = np.arange(offset,nray-1,ratio*minorticks_base).astype(int)
    if majorticks_base > 0:
        majorticks = np.arange(offset,nray-1,ratio*majorticks_base).astype(int)

    # We need to fix the aspect ratio before drawing ticks.
    axes.apply_aspect()

    for i in minorticks:
        if i < 0 or not mask[i]: continue
        drawtick(i, 1.0, lw*0.5)

    for i in majorticks:
        if i < 0 or not mask[i]: continue
        timestr = time2dt(time[i]).strftime("%H:%M:%S")
        drawtick(i, 1.5, lw, timestr)

    trajectory = mpl.lines.Line2D(X[mask], Y[mask], color=color, lw=lw)
    axes.add_line(trajectory)

    return mask

#    indices = np.flatnonzero(abs(X-np.roll(X, -1)) + \
#              abs(Y-np.roll(Y, -1)) > 1) + 1
#    Xsplit = np.array_split(X, indices)
#    Ysplit = np.array_split(Y, indices)
#    for i in range(len(indices)):
#        m.plot(Xsplit[i], Ysplit[i], color=color, lw=lw)


def read_modis_swath(product, band, band_mode,
                     along_track_ext=(0,-1), across_track_ext=(0,-1)):

    sw = product[b"MODIS_SWATH_Type_L1B"]

    try:
        lon = sw[b"Longitude"]
        lat = sw[b"Latitude"]
    except KeyError as err:
        return None

    data = None
    if band in (1, 2):
        data = sw.get(b"EV_250_RefSB", data)
        data = sw.get(b"EV_250_Aggr500_RefSB", data)
        data = sw.get(b"EV_250_Aggr1km_RefSB", data)
        band_offset = -1
    elif band in (3, 4, 5, 6, 7):
        data = sw.get(b"EV_500_RefSB", data)
        data = sw.get(b"EV_500_Aggr1km", data)
        band_offset = -3
    elif band in range(8, 20) or band in (13.5, 14.5):
        data = sw.get(b"EV_1KM_RefSB", data)
        if band <= 13: band_offset = -8
        elif band == 13.5: band_offset = -7
        elif band == 14.0: band_offset = -7
        else: band_offset = -6
    elif band in range(20, 26):
        data = sw.get(b"EV_1KM_Emissive", data)
        band_offset = -20
    # TODO: Add support for band 26.
    elif band == 26: fail("Band 26 is not supported")
    elif band in range(27, 37):
        data = sw.get(b"EV_1KM_Emissive", data)
        band_offset = -21

    band_index = band + band_offset

    if data == None or data.shape[0] <= band_index:
        fail("%d: Band not present in the data file" % band)

    off1, inc1 = sw.maps[(lon.dims[0], data.dims[1])]
    off2, inc2 = sw.maps[(lon.dims[1], data.dims[2])]

    if band_mode == BAND_MODE_REFLECTANCE and band >= 20 and band != 26:
        fail("Invalid band")

    if band_mode == BAND_MODE_REFLECTANCE:
        try:
            si_scale = data.attributes[b"reflectance_scales"][band_index]
            si_offset = data.attributes[b"reflectance_offsets"][band_index]
        except KeyError: fail("Reflectance parameters not present")
    elif band_mode == BAND_MODE_RADIANCE:
        try:
            si_scale = data.attributes[b"radiance_scales"][band_index]
            si_offset = data.attributes[b"radiance_offsets"][band_index]
        except KeyError: fail("Radiance parameters not present")
    else: fail("Assertion error: Invalid ref/rad switch")

    nscan_ndet = data.shape[1]
    nfram_nsam = data.shape[2]

    e1, e2 = along_track_ext
    e3, e4 = across_track_ext

    e1 = norm_index(e1, 0, nscan_ndet)
    e2 = norm_index(e2, 0, nscan_ndet)
    e3 = norm_index(e3, 0, nfram_nsam)
    e4 = norm_index(e4, 0, nfram_nsam)

    if e1 >= e2 or e3 >= e4: return None

    # Perform dimension mapping on lon/lat.
    lat = ccplot.utils.dimmap(
        ccplot.utils.dimmap(lat[:,:], e2 - e1, off1, inc1, 0, 360),
        e4 - e3, off2, inc2, 1, 360
    )
    lon = ccplot.utils.dimmap(
        ccplot.utils.dimmap(lon[:,:], e2 - e1, off1, inc1, 0, 360),
        e4 - e3, off2, inc2, 1, 360
    )
    lon = (lon + 180.0) % 360.0 - 180.0
    lat = (lat + 90.0) % 180.0 - 90.0

    # Choose band and crop data.
    data = data[band_index, e1:e2, e3:e4].astype(np.float32)
    # Set invalid data elements to NaN.
    np.place(data, data < 0.0, float("nan"))
    # Peform dimension mapping.
    data = np.float32(si_scale) * (data - np.float32(si_offset))
    # Radiance to temperature conversion.
    if band_mode == BAND_MODE_RADIANCE:
        data = radiance2temp(data, modis_band_wavelength(band) * 1E-9)
        name = "Band %2.1f Black Body Temperature (K)" % band
    elif band_mode == BAND_MODE_REFLECTANCE:
        data *= 100 # In per cent.
        name = "Band %2.1f Albedo (%%)" % band

    swath = Swath()
    swath.lon = lon
    swath.lat = lat
    swath.data = data
    swath.name = name
    return swath


def plot_swath(swath, fig, axes, proj, colormap=None, norm=None, ticks=None,
               radius=None, name=None, opts=PlotOpts()):

    global EV_DATAPOINT_SIZE

    # lon/lat to X/Y conversion.
    res = axes.projection.transform_points(ccrs.PlateCarree(),
        swath.lon, swath.lat)
    X, Y = res[:,:,0], res[:,:,1]
    if X.dtype != np.float32: X = np.asarray(X, dtype=np.float32)
    if Y.dtype != np.float32: Y = np.asarray(Y, dtype=np.float32)

    # Interpolate data on X/Y grid.
    x, y, width, height = get_axes_bounds(fig, axes)
    nx = int(width * fig.get_dpi())
    ny = int(height * fig.get_dpi())
    x0, x1, y0, y1 = axes.get_extent()
    if radius == None:
        if proj in ("cyl", "ob_tran"):
            xfactor = 20037508.34/180.0
            yfactor = 10018754.17/90.0
        else:
            xfactor = yfactor = 1.0
        radius_x = int(EV_DATAPOINT_SIZE/((x1 - x0)*xfactor)*nx+0.5)
        radius_y = int(EV_DATAPOINT_SIZE/((y1 - y0)*yfactor)*ny+0.5)
        info("Interpolation radius: rx=%d, ry=%d" % (radius_x, radius_y))
    else:
        radius_x = radius_y = radius
    radius_x = max(1, radius_x)
    radius_y = max(1, radius_y)

    data = cctk.interpolate2d(swath.data, X, Y, (x0, x1, nx),
                              (y0, y1, ny), float("nan"),
                              radius_x, radius_y)
    del X, Y

    # Mask invalid values.
    data = np.ma.masked_invalid(data)

    # Plotting.
    im = axes.imshow(data.T, cmap=colormap, norm=norm, interpolation="none",
        extent=(x0, x1, y0, y1), origin="lower", transform=axes.projection)

    cbaxes = fit_colorbar(fig, axes, space=opts.cbspacing, padding=opts.padding)
    cb = fig.colorbar(im, ax=axes, cax=cbaxes, orientation="vertical",
                      extend="both", ticks=ticks)
    cb.set_label(swath.name)
    cb.ax.tick_params(direction="in")

    for label in cb.ax.get_yticklabels():
        label.set_fontsize(opts.cbfontsize)


#
# The program starts here.
#
def main(argv):
    global CCPLOT_CMAP_PATH
    CCPLOT_CMAP_PATH = os.getenv("CCPLOT_CMAP_PATH", CCPLOT_CMAP_PATH)

    opts = parse_options(argv)

    # Open each file as HDF and HDF-EOS if possible.
    products = []
    for fname in opts.fnames:
        try: product = HDF(fsencode(fname))
        except IOError as e: fail("%s: %s" % (fname, e.strerror))

        try: hdfeosversion = product.attributes[b'HDFEOSVersion']
        except KeyError: hdfeosversion = None

        if hdfeosversion is not None:
            # Reopen with HDFEOS.
            product.close()
            try: product = HDFEOS(fsencode(fname))
            except IOError as e: fail("%s: %s" % (fname, e.strerror))

        products.append(product)

    if opts.print_info_only:
        # Print information about the file and exit.
        print_info(products[0])
        sys.exit(0)

    mpl.rcParams["font.size"] = opts.plot_opts.fontsize

    fig = plt.figure(figsize=(1, 1), dpi=opts.dpi)
    axes = new_axes(fig, opts.plot_opts.padding,
                         opts.plot_opts.padding,
                         0,
                         opts.plot_opts.plotheight,
                         padding=opts.plot_opts.padding)

    # Determine colormap, norm and ticks.
    colormap = copy.copy(mpl.cm.Greys)
    colormap.set_bad("k", 0.0)
    norm = None
    ticks = None
    if opts.cmapfname != None:
        (colormap, norm, ticks) = loadcolormap(opts.cmapfname, "colormap")

    if len(products) == 0:
        usage()

    filetype = autodetect(products[0])

    #
    # Main switch.

    # Profile products.
    if opts.plot_type in ("orbit", "orbit-clipped"):
        plot_orbit(
            opts.fnames,
            products,
            fig,
            axes,
            band=opts.modis_band,
            band_mode=opts.modis_band_mode,
            hextent=opts.hextent,
            proj=opts.projection,
            colormap=colormap,
            norm=norm,
            ticks=ticks,
            clipped=(opts.plot_type == "orbit-clipped"),
            radius=opts.radius,
            proj_opts=opts.proj_opts,
            opts=opts.plot_opts
        )
    elif filetype in ("cloudsat-2b-geoprof", "calipso-profile"):
        if len(products) > 1:
            fail("Single file expected")
        plot_profile(
            opts.plot_type,
            opts.fnames[0],
            products[0],
            fig,
            axes,
            hextent=opts.hextent,
            vextent=opts.vextent,
            aspect=opts.aspect,
            colormap=colormap,
            norm=norm,
            ticks=ticks,
            radius=opts.radius,
            opts=opts.plot_opts
        )
    # Layer products.
    elif filetype == "calipso-layer":
        if len(products) > 1:
            fail("Single file expected")
        plot_profile(
            opts.plot_type,
            opts.fnames[0],
            products[0],
            fig,
            axes,
            hextent=opts.hextent,
            vextent=opts.vextent,
            aspect=opts.aspect,
            colormap=colormap,
            norm=norm,
            ticks=ticks,
            radius=opts.radius,
            opts=opts.plot_opts
        )
    else:
        fail("Unknown product type")

    #report_memory()

    figw_px, figh_px = fig.get_size_inches()*opts.dpi
    if figw_px >= 32768 or figh_px >= 32768:
        fail("Figure size exceeds 32767 pixels, please specify a smaller region")

    info("Saving plot")

    try: plt.savefig(opts.outfname, dpi=opts.dpi)
    except IOError as err: fail("Write error: %s" % err)

    #report_memory()


def main_wrapper():
    try:
        main(sys.argv)
    except MemoryError:
        fail("Insufficient memory")
    except np.linalg.linalg.LinAlgError as err:
        fail("Linear algebra error: %s" % err)


if __name__ == "__main__":
	main()
