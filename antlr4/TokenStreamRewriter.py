#
# [The "BSD license"]
#  Copyright (c) 2012 Terence Parr
#  Copyright (c) 2012 Sam Harwell
#  Copyright (c) 2014 Eric Vergnaud
#  Copyright (c) 2014 Edward Hodapp
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#  3. The name of the author may not be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
#  IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
#  OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#/

from antlr4._java import StringBuilder
from antlr4.BufferedTokenStream import BufferedTokenStream
from antlr4.Token import Token
from antlr4.misc.IntervalSet import Interval


class TokenStreamRewriter(object):
    DEFAULT_PROGRAM_NAME = "default"
    PROGRAM_INIT_SIZE = 100
    MIN_TOKEN_INDEX = 0


    class RewriteOperation(object):
        def __init__(self, tsr, index, text=None):
            self._tsr = tsr
            self.instructionIndex = None
            self.text = None
            self.index = index
            if text is not None:
                self.text = text

        def execute(self, buf):
            return self.index

        def toString(self):
            opName = type(self).__name__
            return '<{}@{}:"{}">'.format(
                opName, self._tsr.tokens[self.index], self.text)


    class InsertBeforeOp(RewriteOperation):
        def __init__(self, tsr, index, text):
            super(TokenStreamRewriter.InsertBeforeOp, self).__init__(
                tsr, index, text)

        def execute(self, buf):
            buf.append(self.text)
            if self._tsr.tokens[self.index].type != Token.EOF:
                buf.append(self._tsr.tokens[self.index].getText())
            return self.index+1


    class ReplaceOp(RewriteOperation):
        def __init__(self, tsr, from_, to, text):
            super(TokenStreamWriter.ReplaceOp, self).__init__(
                tsr, from_, to, text)
            self.lastIndex = to

        def execute(self, buf):
            if self.text is not None:
                buf.append(self.text)
            return self.lastIndex+1

        def toString(self):
            if self.text is None:
                return '<DeleteOp@{}..{}>'.format(
                    self._tsr.tokens[self.index],
                    self._tsr.tokens[self.lastIndex])
            return '<ReplaceOp@{}..{}:"{}">'.format(
                self._tsr.tokens[self.index],
                self._tsr.tokens[self.lastIndex],
                self.text)


    def __init__(self, tokens):
        self.tokens = tokens
        self.programs = {self.DEFAULT_PROGRAM_NAME: []}
        self.lastRewriteTokenIndexes = {}

    def getTokenStream(self):
        return self.tokens

    def rollback(self, *args):
        if isinstance(args[0], int):
            # rollback(int instructionIndex)
            instructionIndex, = args
            programName = self.DEFAULT_PROGRAM_NAME
        else:
            # rollback(String programName, int instructionIndex)
            programName, instructionIndex = args
        instr_list = self.programs.get(programName, None)
        if instr_list:
            self.programs[programName] = (
                instr_list[self.MIN_TOKEN_INDEX, instructionIndex])

    def deleteProgram(self, *args):
        if len(args):
            # deleteProgram(String programName)
            programName = args[0]
        else:
            # deleteProgram()
            programName = self.DEFAULT_PROGRAM_NAME
        self.rollback(programName, self.MIN_TOKEN_INDEX)

    def insertAfter(self, *args):
        if isinstance(args[0], Token):
            # insertAfter(Token t, Object text)
            tok, text = args
            programName = self.DEFAULT_PROGRAM_NAME
            index = tok.getTokenIndex()
        elif isinstance(args[0], int):
            # insertAfter(int index, Object text)
            index, text = args
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[1], Token):
            # insertAfter(String programName, Token t, Object text)
            programName, tok, text = args
            index = tok.getTokenIndex()
        else:
            # insertAfter(String programName, int index, Object text)
            programName, index, text = args
        self.insertBefore(programName, index+1, text)

    def insertBefore(self, *args):
        if isinstance(args[0], Token):
            # insertBefore(Token t, Object text)
            tok, text = args
            index = tok.getTokenIndex()
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[0], int):
            # insertBefore(int index, Object text)
            index, text = args
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[1], Token):
            # insertBefore(String programName, Token t, Object text)
            programName, tok, text = args
            index = tok.getTokeIndex()
        else:
            # insertBefore(String programName, int index, Object text)
            programName, index, text = args
        op = self.InsertBeforeOp(self, index, text)
        rewrites = self.getProgram(programName)
        op.instructionIndex = len(rewrites)
        rewrites.append(op)

    def replace(self, *args):
        if isinstance(args[0], int) and len(args) == 2:
            # replace(int index, Object text)
            index, text = args
            programName = self.DEFAULT_PROGRAM_NAME
            from_ = to = index
        elif isinstance(args[0], int) and len(args) == 3:
            # replace(int from, int to, Object text)
            from_, to, text = args
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[0], Token) and len(args) == 2:
            # replace(Token indexT, Object text)
            indexT, text = args
            from_ = to = indexT.getTokenIndex()
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[0], Token) and len(args) == 3:
            # replace(Token from, Token to, Object text)
            from_, to, text = args
            from_ = from_.getTokenIndex()
            to = to.getTokenIndex()
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[1], Token) and len(args) == 4:
            # replace(String programName, Token from, Token to, Object text)
            programName, from_, to, text = args
            from_ = from_.getTokenIndex()
            to = to.getTokenIndex()
        else:
            programName, from_, to, text = args
        if from_ > to or from_ < 0 or to < 0 or to > len(self.tokens):
            raise IndexError('replace: range invalid: {}..{} (size={})'.format(
                from_, to, len(self.tokens)))
        op = ReplaceOp(from_, to, text)
        op.instructionIndex = len(self.rewrites)
        rewrites.append(op)

    def delete(self, *args):
        if isinstance(args[0], int) and len(args) == 1:
            # delete(int index)
            index, = args
            from_ = to = index
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[0], int) and len(args) == 2:
            # delete(int from, int to)
            from_, to = args
            programName = self.DEFAULT_PROGRAM_NAME
        elif isinstance(args[0], Token) and len(args) == 1:
            # delete(Token indexT)
            indexT, = args
            self.replace(self.DEFAULT_PROGRAM_NAME, indexT, indexT, None)
        elif isinstance(args[0], Token) and len(args) == 2:
            # delete(Token from, Token to)
            from_, to = args
            self.replace(self.DEFAULT_PROGRAM_NAME, from_, to, None)
        elif isinstance(args[1], int) and len(args) == 3:
            # delete(String programName, int from, int to)
            programName, from_, to = args
            self.replace(programName, from_, to, None)
        else:
            # delete(String programName, Token from, Token to)
            programName, from_, to = args
            self.replace(programName, from_, to, None)

    def getLastRewriteTokenIndex(self, *args):
        if len(args) == 0:
            # getLastRewriteTokenIndex()
            programName = self.DEFAULT_PROGRAM_NAME
        else:
            # getLastRewriteTokenIndex(String programName)
            programName, = args
        index = self.lastRewriteTokenIndexes[programName]
        if index is None:
            return -1
        return index

    def setLastRewriteTokenIndex(self, programName, i):
        self.lastRewriteTokenIndexes[programName] = i

    def getProgram(self, name):
        instr_list = self.programs.get(name, None)
        if instr_list is None:
            instr_list = self.initializeProgram(name)
        return instr_list

    def initializeProgram(self, name):
        instr_list = []
        self.programs[name] = instr_list
        return instr_list

    def getText(self, *args):
        if len(args) == 0:
            # getText()
            programName = self.DEFAULT_PROGRAM_NAME
            interval = Interval(0, self.tokens.size()-1)
        elif isinstance(args[0], Interval):
            # getText(Interval interval)
            interval, = args
            programName = self.DEFAULT_PROGRAM_NAME
        else:
            # getText(String programName, Interval interval)
            programName, interval = args
        rewrites = self.programs.get(programName, None)
        start = interval.start
        stop = interval.stop
        stop = min(stop, self.tokens.size()-1)
        start = max(0, start)
        if not rewrites:
            return self.tokens.getText((interval.start, interval.stop))
        buf = StringBuilder()
        indexToOp = self.reduceToSingleOperationPerIndex(rewrites)
        i = start
        while i <= stop and i < len(self.tokens):
            op = indexToOp.get(i, None)
            tok = self.tokens.get(i, None)
            if op is None:
                if tok.type != Token.EOF:
                    buf.append(tok.getText())
                    i += 1
            else:
                del indexToOp[i]
                i = op.execute(buf)
        if stop == len(self.tokens)-1:
            for op in indexToOp.values():
                if op.index > len(self.tokens)-1:
                    buf.append(op.text)
        return buf.toString()

    def reduceToSingleOperationPreIndex(rewrites):
        for i in range(len(rewrites)):
            op = rewrites[i]
            if op is None:
                continue
            if not isinstance(op, self.ReplaceOp):
                continue
            rop = op
            inserts = self.getKindOfOps(rewrites, type(self.InsertBeforeOp), i)
            for iop in inserts:
                if iop.index == rop.index:
                    rewrites[iop.instructionIndex] = None
                    rop.text = iop.text.toString() + (
                        '' if rop.text is None else rop.text.toString())
                elif iop.index > rop.index and iop.index <= rop.lastIndex:
                    rewrites[iop.instructionIndex] = None
            prevReplaces = self.getKindOfOps(rewrites, type(self.ReplaceOp), i)
            for prevRop in prevReplaces:
                if (prevRop.index >= rop.index and
                    prevRop.lastIndex <= rop.lastIndex):
                    rewrites[prevRop.instructionIndex] = None
                    continue
                disjoint = (prevRop.lastIndex < rop.index or
                            prevRop.index > rop.lastIndex)
                same = (prevRop.index == rop.index and
                        prevRop.lastIndex == rop.lastIndex)
                if prevRop.text is None and rop.text is None and not disjoint:
                    rewrite[prevRop.instructionIndex] = None
                    rop.index = min(prevRop.index, rop.index)
                    rop.lastIndex = max(prevRop.lastIndex, rop.lastIndex)
                    print('new rop ' + rop)
                elif not disjoint and not same:
                    raise RuntimeError(
                        'replace op boundaries of {} '
                        'overlap with previous {}'.format(rop, prevRop))
        for i in range(len(rewrites)):
            op = rewrites[i]
            if op is None:
                continue
            if not isinstance(op, self.InsertBeforeOp):
                continue
            iop = op
            prevInserts = self.getKindOfOps(
                rewrites, type(self.InsertBeforeOp), i)
            for prevIop in prevInserts:
                if prevIop.index == iop.index:
                    iop.text = self.catOpText(iop.text, prevIop.text)
                    rewrites[prevIop.instructionIndex] = None
            prevReplaces = self.getKindOfOps(rewrites, type(self.ReplaceOp), i)
            for rop in prevReplaces:
                if iop.index == rop.index:
                    rop.text = self.catOpText(iop.text, rop.text)
                    rewrites[i] = None
                    continue
                if iop.index >= rop.index and iop.index <= rop.lastIndex:
                    raise RuntimeError(
                        'insert op {} within boundaries of previous {}'.format(
                            iop, rop))
        map = {}
        for i in range(len(rewrites)):
            op = rewrites[i]
            if op is None:
                continue
            if op.index in map:
                raise RuntimeError(
                    'should only be one op per index')
            map[op.index] = op
        return map

    def catOpText(op1, op2):
        str1 = ''
        str2 = ''
        if op1 is not None:
            str1 = op1.toString()
        if op2 is not None:
            str2 = op2.toString()
        return str1 + str2

    def getKindsOfOps(rewrites, kind, before):
        ops = []
        i = 0
        while i < before and i < len(rewrites):
            op = rewrites[i]
            if op is None:
                continue
            if isinstance(op, kind):
                ops.append(op)
            i += 1
        return ops
