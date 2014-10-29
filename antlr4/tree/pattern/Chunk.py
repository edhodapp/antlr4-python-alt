from antlr4._compat import py2_unicode_compat


class Chunk(object):
    pass


@py2_unicode_compat
class TagChunk(Chunk):
    def __init__(self, tag, label=None):
        self.tag = tag
        self.label = label

    def __str__(self):
        if self.label is not None:
            return self.label + u":" + self.tag
        return self.tag


@py2_unicode_compat
class TextChunk(Chunk):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return u"'" + self.text + u"'"
