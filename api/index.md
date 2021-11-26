---
layout: default
title: API
---
API (beta)
==========

**ccplot >= 1.5-rc5**

If the command-line program does not fulfill your needs,
you can use routines
provided with ccplot to make custom plots in python. These include routines
for reading HDF and HDF-EOS2 files, parsing time values and performing
data interpolation. See [API reference](reference/) for details.

Examples
--------

### Note about examples

The examples below differ from the ccplot program in a number of important
details:

* The aspect ratio is determined by matplotlib. The figure size is fixed
in inches, so the actual aspect ratio depends on the horizontal and
vertical extent. In contrast, the ccplot program sets the figure width
according to a prespecified aspect ratio.

* A new interpolation routine **ccplot.algorithms.interp2d_12** is used,
which performs interpolation by averaging
as opposed to nearest-neighbor interpolation in the ccplot program
(but see [API reference](reference/) for details).

### CALIPSO example

[![CALIPSO example](calipso-plot-small.png)](calipso-plot.png)

**Input file:**
[CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf](https://sourceforge.net/projects/ccplot/files/products/CAL_LID_L1-ValStage1-V3-01.2007-06-12T03-42-18ZN.hdf)

**Source:** [calipso-plot.py](https://raw.github.com/peterkuma/ccplot/gh-pages/_includes/calipso-plot.py)

{% highlight python %}
{% include calipso-plot.py %}
{% endhighlight %}

### CloudSat example

[![CloudSat example](cloudsat-plot-small.png)](cloudsat-plot.png)

**Input file:**
[2013119200420_37263_CS_2B-GEOPROF_GRANULE_P_R04_E06.hdf](https://sourceforge.net/projects/ccplot/files/products/2013119200420_37263_CS_2B-GEOPROF_GRANULE_P_R04_E06.hdf)

**Source:** [cloudsat-plot.py](https://raw.github.com/peterkuma/ccplot/gh-pages/_includes/cloudsat-plot.py)

{% highlight python %}
{% include cloudsat-plot.py %}
{% endhighlight %}
