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
