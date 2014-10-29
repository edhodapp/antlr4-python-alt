#[The "BSD license"]
# Copyright (c) 2012 Terence Parr
# Copyright (c) 2012 Sam Harwell
# Copyright (c) 2014 Eric Vergnaud
# Copyright (c) 2014 Brian Kearns
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# A token has properties: text, type, line, character position in the line
# (so we can ignore tabs), token channel, index, and source from which
# we obtained this token.
from antlr4._compat import py2_unicode_compat


class Token (object):

    INVALID_TYPE = 0

    # During lookahead operations, this "token" signifies we hit rule end ATN state
    # and did not follow it despite needing to.
    EPSILON = -2

    MIN_USER_TOKEN_TYPE = 1

    EOF = -1

    # All tokens go to the parser (unless skip() is called in that rule)
    # on a particular "channel".  The parser tunes to a particular channel
    # so that whitespace etc... can go to the parser on a "hidden" channel.

    DEFAULT_CHANNEL = 0

    # Anything on different channel than DEFAULT_CHANNEL is not parsed
    # by parser.

    HIDDEN_CHANNEL = 1


@py2_unicode_compat
class CommonToken(Token):


    # An empty {@link Pair} which is used as the default value of
    # {@link #source} for tokens that do not have a source.
    EMPTY_SOURCE = (None, None)

    def __init__(self, source=EMPTY_SOURCE, type=None,
                 channel=Token.DEFAULT_CHANNEL, start=0, stop=0, text=None):
        assert type is not None
        self.source = source
        self.type = type
        self.channel = channel
        self.start = start
        self.stop = stop
        self._text = text

        self.tokenIndex = -1
        if source[0] is not None:
            self.line = source[0].line
            self.column = source[0].column
        else:
            self.line = 0
            self.column = -1

    # Constructs a new {@link CommonToken} as a copy of another {@link Token}.
    #
    # <p>
    # If {@code oldToken} is also a {@link CommonToken} instance, the newly
    # constructed token will share a reference to the {@link #text} field and
    # the {@link Pair} stored in {@link #source}. Otherwise, {@link #text} will
    # be assigned the result of calling {@link #getText}, and {@link #source}
    # will be constructed from the result of {@link Token#getTokenSource} and
    # {@link Token#getInputStream}.</p>
    #
    # @param oldToken The token to copy.
     #
    def clone(self):
        t = CommonToken(self.source, self.type, self.channel,
                        self.start, self.stop, self.text)
        t.tokenIndex = self.tokenIndex
        t.line = self.line
        t.column = self.column
        return t

    @property
    def text(self):
        if self._text is not None:
            return self._text
        input = self.getInputStream()
        if input is None:
            return None
        n = input.size
        if self.start < n and self.stop < n:
            return input.getText(self.start, self.stop)
        else:
            return u"<EOF>"

    @text.setter
    def text(self, text):
        self._text = text

    def getTokenSource(self):
        return self.source[0]

    def getInputStream(self):
        return self.source[1]

    def __str__(self):
        channel_str = u""
        if self.channel > 0:
            channel_str = u",channel=%d" % self.channel
        txt = self.text
        if txt is not None:
            txt = txt.replace(u"\n", u"\\n")
            txt = txt.replace(u"\r", u"\\r")
            txt = txt.replace(u"\t", u"\\t")
        else:
            txt = u"<no text>"
        return u"[@%d,%d:%d='%s',<%d>%s,%d:%d]" % (
            self.tokenIndex, self.start, self.stop, txt, self.type,
            channel_str, self.line, self.column)
