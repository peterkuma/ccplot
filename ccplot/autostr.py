import os
import locale


def autostr(arg):
    if type(arg) is bytes:
        return arg.decode(locale.getlocale()[1])
    elif not callable(arg):
        return arg
    f = arg
    def f2(self, *args, **kwargs):
        if f.__name__ == "__init__":
            if hasattr(args[0], "_encoding"):
                self._encoding = args[0]._encoding
            if hasattr(args[0], "_mode"):
                self._mode = args[0]._mode
        args = [x.encode(self._encoding) if type(x) is str else x for x in args]
        kwargs = {k: (v.encode(self._encoding) if type(v) is str else v)
            for k, v in kwargs.items()}
        out = f(self, *args, **kwargs)
        if self._mode == "text":
            if type(out) is bytes:
                return out.decode(self._encoding)
            elif type(out) is list:
                return [x.decode(self._encoding) if type(x) is bytes else x
                    for x in out]
            elif type(out) is dict:
                return { \
                    (k.decode(self._encoding) if type(k) is bytes else k): \
                    (v.decode(self._encoding) if type(v) is bytes else v)
                    for k, v in out.items()}
            else:
                return out
        return out
    return f2


class Autostr(object):
    _encoding = None
    _mode = None
    def _autostr(self, s):
        if self._mode == "binary":
            return s
        if type(s) is bytes and self._encoding is not None:
            return s.decode(self._encoding)
        else:
            return s
