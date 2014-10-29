#
# [The "BSD license"]
#  Copyright (c) 2012 Terence Parr
#  Copyright (c) 2012 Sam Harwell
#  Copyright (c) 2014 Eric Vergnaud
#  Copyright (c) 2014 Brian Kearns
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
#


#
# This implementation of {@link ANTLRErrorListener} can be used to identify
# certain potential correctness and performance problems in grammars. "Reports"
# are made by calling {@link Parser#notifyErrorListeners} with the appropriate
# message.
#
# <ul>
# <li><b>Ambiguities</b>: These are cases where more than one path through the
# grammar can match the input.</li>
# <li><b>Weak context sensitivity</b>: These are cases where full-context
# prediction resolved an SLL conflict to a unique alternative which equaled the
# minimum alternative of the SLL conflict.</li>
# <li><b>Strong (forced) context sensitivity</b>: These are cases where the
# full-context prediction resolved an SLL conflict to a unique alternative,
# <em>and</em> the minimum alternative of the SLL conflict was found to not be
# a truly viable alternative. Two-stage parsing cannot be used for inputs where
# this situation occurs.</li>
# </ul>

from antlr4._compat import text_type
from antlr4.ErrorListener import ErrorListener
from antlr4.misc.Utils import str_set


class DiagnosticErrorListener(ErrorListener):

    def __init__(self, exactOnly=True):
        # whether all ambiguities or only exact ambiguities are reported.
        self.exactOnly = exactOnly

    def reportAmbiguity(self, recognizer, dfa, startIndex,
                       stopIndex, exact, ambigAlts, configs):
        if self.exactOnly and not exact:
            return

        format = u"reportAmbiguity d=%s: ambigAlts=%s, input='%s'"
        decision = self.getDecisionDescription(recognizer, dfa)
        conflictingAlts = str_set(self.getConflictingAlts(ambigAlts, configs))
        text = recognizer.getTokenStream().getText((startIndex, stopIndex))
        message = format % (decision, conflictingAlts, text)
        recognizer.notifyErrorListeners(message)

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex,
                       stopIndex, conflictingAlts, configs):
        format = u"reportAttemptingFullContext d=%s, input='%s'"
        decision = self.getDecisionDescription(recognizer, dfa)
        text = recognizer.getTokenStream().getText((startIndex, stopIndex))
        message = format % (decision, text)
        recognizer.notifyErrorListeners(message)

    def reportContextSensitivity(self, recognizer, dfa, startIndex,
                       stopIndex, prediction, configs):
        format = u"reportContextSensitivity d=%s, input='%s'"
        decision = self.getDecisionDescription(recognizer, dfa)
        text = recognizer.getTokenStream().getText((startIndex, stopIndex))
        message = format % (decision, text)
        recognizer.notifyErrorListeners(message)

    def getDecisionDescription(self, recognizer, dfa):
        decision = dfa.decision
        ruleIndex = dfa.atnStartState.ruleIndex

        ruleNames = recognizer.ruleNames
        if ruleIndex < 0 or ruleIndex >= len(ruleNames):
            return text_type(decision)

        ruleName = ruleNames[ruleIndex]
        if ruleName is None or len(ruleName)==0:
            return text_type(decision)

        return u"%d (%s)" % (decision, ruleName)

    #
    # Computes the set of conflicting or ambiguous alternatives from a
    # configuration set, if that information was not already provided by the
    # parser.
    #
    # @param reportedAlts The set of conflicting or ambiguous alternatives, as
    # reported by the parser.
    # @param configs The conflicting or ambiguous configuration set.
    # @return Returns {@code reportedAlts} if it is not {@code null}, otherwise
    # returns the set of alternatives represented in {@code configs}.
    #
    def getConflictingAlts(self, reportedAlts, configs):
        if reportedAlts is not None:
            return reportedAlts

        result = set()
        for config in configs:
            result.add(config.alt)

        return result
