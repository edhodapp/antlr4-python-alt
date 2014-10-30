import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    unichr = unichr
    xrange = xrange
else:
    text_type = str
    unichr = chr
    xrange = range


def py2_unicode_compat(class_):
    assert '__str__' in class_.__dict__
    assert '__unicode__' not in class_.__dict__
    if PY2:
        class_.__unicode__ = class_.__str__
        class_.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return class_


def add_metaclass(metaclass):
    """Class decorator for creating a class with a metaclass."""
    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)
        slots = orig_vars.get('__slots__')
        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]
            for slots_var in slots:
                orig_vars.pop(slots_var)
        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper
