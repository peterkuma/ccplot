import numpy as np
import datetime as dt
import pytz


def calipso_time2dt(time):
    """Convert float in format yymmdd.ffffffff to datetime."""
    d = int(time % 100)
    m = int((time-d) % 10000)
    y = int(time-m-d)
    return dt.datetime(2000 + y//10000, m//100, d, tzinfo=pytz.utc) + dt.timedelta(time % 1)


def cloudsat_time2dt(time, start_time):
    """Convert time in seconds since start_time to datetime."""
    return start_time + dt.timedelta(0, float(time))


def dimmap(x, n, off, inc, axis=0, modulus=None):
    """
    Perform dimension mapping on array `x` along axis `axis`
    with offset `off` and increment `inc`. The axis is extended to the length
    `n`. Intermediate values are interpolated by linear interpolation.
    Values outside of `x` are extrapolated by linear gradient
    at the boundaries.

    Optional argument `modulus` causes dimmap
    to operate in modular arithmetic with the given modulus. In such case
    intermediate values are interpolated over the shortest path between
    the adjacent values in `x`.

    Examples
    --------

    >>> dimmap(np.array([350, 5, 20, 10, 350]), 30, 4, 5, 0, 360)
    array([ 338.,  341.,  344.,  347.,  350.,  353.,  356.,  359.,    2.,
              5.,    8.,   11.,   14.,   17.,   20.,   18.,   16.,   14.,
             12.,   10.,    6.,    2.,  358.,  354.,  350.,  346.,  342.,
            338.,  334.,  330.])

    References
    ----------

    - HDF-EOS Library User's Guide for the ECS Project, Volume 1:
    Overview and Examples
    """
    if modulus is not None:
        diff = np.diff(x, axis=axis) % modulus
        d = np.where(
            np.abs(diff) < modulus - np.abs(diff),
            diff,
            -np.sign(diff)*(modulus - np.abs(diff))
        )
    else:
        d = np.diff(x, axis=axis)
    indices = 1.0*(np.arange(n) - off)/inc
    indices_int = np.minimum(
        x.shape[axis] - 1,
        np.maximum(0, np.floor(indices))
    ).astype(np.int64)
    shape = list(x.shape)
    shape[axis] = n
    d_indices = np.minimum(max(0, x.shape[axis] - 2), indices_int)
    out = np.swapaxes(x, axis, 0)[indices_int] + \
        (np.swapaxes(d, axis, 0)[d_indices].T*(indices - indices_int)).T
    out = np.swapaxes(out, 0, axis)
    if modulus is not None:
        return out % modulus
    else:
        return out


def cmap(filename):
    """Load colormap from file. The expected format of the file is:

        BOUNDS
        from1 to1 step1
        from2 to2 step2
        [...]

        TICKS
        from1 to1 step1
        from2 to2 step2
        [...]

        COLORS
        r1 g1 b1
        r2 g2 b2
        [...]

        UNDER_OVER_BAD_COLORS
        ro go bo
        ru gu bu
        rb gb bb

    where fromn, ton, stepn are floating point numbers as would be supplied
    to numpy.arange, and rn, gn, bn are the color components the n-th color
    stripe. Components are expected to be in base 10 format (0-255).
    UNDER_OVER_BAD_COLORS section specifies colors to be used for
    over, under and bad (masked) values, in that order.
    """
    bounds = []
    ticks = []
    colors = []
    special = []
    mode = "COLORS"
    white = [1, 1, 1, 1]

    try:
        with open(filename) as f:
            for n, s in enumerate(f.readlines()):
                s = s.strip()

                # Skip blank lines.
                if len(s) == 0:
                    continue

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
                    rgba = [int(c) for c in a]
                    if len(rgba) == 3:
                        rgba.append(255)
                    colors.append(rgba)
                elif mode == "UNDER_OVER_BAD_COLORS":
                    rgba = [int(c) for c in a]
                    if len(rgba) == 3:
                        rgba.append(255)
                    special.append(rgba)
    except IOError as e:
        raise e
    except ValueError as e:
        raise ValueError("Error reading `%s' on line %d: %s" %
                         (filename, n+1, e))

    return {
        'colors': np.array(colors),
        'bounds': np.array(bounds),
        'ticks': np.array(ticks),
        'under': np.array(special[0] if len(special) >= 1 else white),
        'over': np.array(special[1] if len(special) >= 2 else white),
        'bad': np.array(special[2] if len(special) >= 3 else white),
    }
