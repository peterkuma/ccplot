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
    except IOError, e:
        raise e
    except ValueError, e:
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
