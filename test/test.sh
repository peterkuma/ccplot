#!/bin/sh

. ./libtest.sh

mkdir -p work
cd work
export PATH="..:$PATH"

download() {
    FILENAME=${2-"$(basename $1)"}
    [ -e "$FILENAME" ] && return
    wget -c -O "$FILENAME.tmp" "$1"
    mv "$FILENAME.tmp" "$FILENAME"
}

PRODUCTS='http://downloads.sourceforge.net/project/ccplot/products'
IMG="http://ccplot.org/img"

download "$PRODUCTS/2009037050924_14779_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf"
download "$IMG/cloudsat-reflec.png" "cloudsat-reflec-ccplot.org.ref.png"

download "$PRODUCTS/CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf"
download "$IMG/calipso532.png" "calipso532-ccplot.org.ref.png"

download "$PRODUCTS/MYD021KM.A2009037.0515.005.2009332033315.hdf"
download "$IMG/orbit-modis_x31+cloudsat.png" "orbit-modis_x31+cloudsat-ccplot.org.ref.png"

download "$PRODUCTS/MYD021KM.A2007163.0415.005.2009290181256.hdf"
download "$IMG/orbit-modis_x31+calipso_spstere.png" "orbit-modis_x31+calipso_spstere-ccplot.org.ref.png"

download "$PRODUCTS/CAL_LID_L2_01kmCLay-Prov-V1-20.2007-06-12T03-42-18ZN.hdf"
download "$IMG/calipso532-layer.png" "calipso532-layer.ref.png"

testing "print version information"
check ccplot -V

testing "list of available projections"
check ccplot -p help
expect <<EOF
aea	Albers equal area
aeqd	Azimuthal equidistant
cea	Lambert cylindrical
cyl	Cylindrical equidistant (Plate Carree)
eck1	Eckert I
eck2	Eckert II
eck3	Eckert III
eck4	Eckert IV
eck5	Eckert V
eck6	Eckert VI
eqdc	Equidistant conic
eqearth	Equal Earth
europp	EuroPP
geos	Geostationary
gnom	Gnomonic
igh	Interrupted Goode"s homolosine
laea	Lambert azimuthal qqual area
lcc	Lambert conformal
merc	Mercator
mill	Miller cylindrical
moll	Mollweide
npstere	North-Polar stereographic
nsper	Nearside perspective
ob_tran	Rotated pole
ortho	Orthographic
osgb	OSGB
osni	OSNI
robin	Robinson
sinu	Sinusoidal
spstere	South-Polar stereographic
stere	Stereographic
tmerc	Transverse Mercator
utm	Universal Transverse Mercator (UTM)
EOF

testing "list of available options"
check ccplot -z help
expect <<EOF
cbspacing
coastlinescolor
coastlineslw
countriescolor
countrieslw
drawcoastlines
drawcountries
drawlakes
drawlsmask
drawmeridians
drawminormeridians
drawminorparallels
drawparallels
fontsize
landcolor
majormeridianscolor
majormeridianslw
majorparallelscolor
majorparallelslw
mapres
meridiansbase
minormeridianscolor
minormeridianslw
minorparallelscolor
minorparallelslw
nminormeridians
nminorparallels
padding
parallelsbase
plotheight
trajcolors
title
trajlws
trajnminorticks
trajticks
watercolor
EOF

testing "print info on CALIPSO"
check ccplot -i CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf
expect <<EOF
Type: CALIPSO
Subtype: profile
Time: 2007-06-12 03:42:14, 2007-06-12 04:28:47
Height: -1815m, 39855m
nray: 56310
nbin: 583
Longitude: 179.99W, 180.00E
Latitude: 81.85S, 55.50N
EOF

testing "print info on CALIPSO layer products"
check ccplot -i CAL_LID_L2_01kmCLay-Prov-V1-20.2007-06-12T03-42-18ZN.hdf
expect <<EOF
Type: CALIPSO
Subtype: layer
Time: 2007-06-12 03:42:14, 2007-06-12 04:28:39
nray: 18720
nlayers: 4
Longitude: 179.97W, 179.98E
Latitude: 81.85S, 55.50N
EOF

testing "print info on CloudSat 2B-GEOPROF"
check ccplot -i 2009037050924_14779_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf
expect <<EOF
Type: CloudSat
Subtype: 2B-GEOPROF
Time: 2009-02-06 05:09:24, 2009-02-06 06:48:16
Height: -4819m, 24920m
nray: 37082
nbin: 125
Longitude: 179.98W, 179.97E
Latitude: 81.79S, 81.79N
EOF

testing "print info on MODIS"
check ccplot -i MYD021KM.A2007163.0415.005.2009290181256.hdf
expect <<EOF
Type: MODIS
Subtype: Swath L1B
Longitude: 119.66W, 80.45W
Latitude: 70.71S, 61.17S
EOF

testing "CALIPSO example from ccplot.org"
check ccplot -o calipso532-ccplot.org.png -c calipso-backscatter.cmap -a 30 -x 4:16:20..4:21:50 -y 0..30000 calipso532 CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf
expect ""
check imgcompare calipso532-ccplot.org.png calipso532-ccplot.org.ref.png

testing "CloudSat example from ccplot.org"
check ccplot -o cloudsat-reflec-ccplot.org.png -c cloudsat-reflectivity.cmap -a 15 -x 24.60S..31S,50W..60W -y -1000..18000 cloudsat-reflec 2009037050924_14779_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf
expect ""
check imgcompare cloudsat-reflec-ccplot.org.png cloudsat-reflec-ccplot.org.ref.png

testing "first MODIS example from ccplot.org"
check ccplot -o orbit-modis_x31+cloudsat-ccplot.org.png -m x31 -c modis-temperature.cmap -p tmerc orbit-clipped MYD021KM.A2009037.0515.005.2009332033315.hdf 2009037050924_14779_CS_2B-GEOPROF_GRANULE_P_R04_E02.hdf
expect ""
check imgcompare orbit-modis_x31+cloudsat-ccplot.org.png orbit-modis_x31+cloudsat-ccplot.org.ref.png

testing "second MODIS example from ccplot.org"
check ccplot -o orbit-modis_x31+calipso_spstere-ccplot.org.png -m x31 -c modis-temperature.cmap -p spstere orbit MYD021KM.A2007163.0415.005.2009290181256.hdf CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf
expect ""
check imgcompare orbit-modis_x31+calipso_spstere-ccplot.org.png orbit-modis_x31+calipso_spstere-ccplot.org.ref.png

testing "CALIPSO 532nm layer plot"
check ccplot -o calipso532-layer.png -c calipso-backscatter.cmap -a 30 -x 68S..81S,40W..140W -y 0..25000 calipso532-layer CAL_LID_L2_01kmCLay-Prov-V1-20.2007-06-12T03-42-18ZN.hdf
expect ""
check imgcompare calipso532-layer.png calipso532-layer.ref.png

complete
