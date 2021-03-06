#
# [The "BSD license"]
#  Copyright (c) 2012 Terence Parr
#  Copyright (c) 2012 Sam Harwell
#  Copyright (c) 2014 Eric Vergnaud
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
from antlr4.atn.ATNConfig import ATNConfig
from antlr4.atn.ATNState import RuleStopState
from antlr4.atn.PredictionContext import (PredictionContext,
                                          PredictionContextFromRuleContext,
                                          SingletonPredictionContext)
from antlr4.atn.Transition import (AbstractPredicateTransition,
                                   NotSetTransition, RuleTransition,
                                   WildcardTransition)
from antlr4.misc.IntervalSet import Interval, IntervalSet
from antlr4.Token import Token


class LL1Analyzer (object):
    
    #* Special value added to the lookahead sets to indicate that we hit
    #  a predicate during analysis if {@code seeThruPreds==false}.
    #/
    HIT_PRED = Token.INVALID_TYPE

    def __init__(self, atn):
        self.atn = atn

    #*
    # Calculates the SLL(1) expected lookahead set for each outgoing transition
    # of an {@link ATNState}. The returned array has one element for each
    # outgoing transition in {@code s}. If the closure from transition
    # <em>i</em> leads to a semantic predicate before matching a symbol, the
    # element at index <em>i</em> of the result will be {@code null}.
    #
    # @param s the ATN state
    # @return the expected symbols for each outgoing transition of {@code s}.
    #/
    def getDecisionLookahead(self, s):
        if s is None:
            return None

        count = len(s.transitions)
        look = [] * count
        for alt in range(0, count):
            look[alt] = set()
            lookBusy = set()
            seeThruPreds = False # fail to get lookahead upon pred
            self._LOOK(s.transition(alt).target, None, PredictionContext.EMPTY, \
                  look[alt], lookBusy, set(), seeThruPreds, False)
            # Wipe out lookahead for this alternative if we found nothing
            # or we had a predicate when we !seeThruPreds
            if len(look[alt])==0 or self.HIT_PRED in look[alt]:
                look[alt] = None
        return look

    #*
    # Compute set of tokens that can follow {@code s} in the ATN in the
    # specified {@code ctx}.
    #
    # <p>If {@code ctx} is {@code null} and the end of the rule containing
    # {@code s} is reached, {@link Token#EPSILON} is added to the result set.
    # If {@code ctx} is not {@code null} and the end of the outermost rule is
    # reached, {@link Token#EOF} is added to the result set.</p>
    #
    # @param s the ATN state
    # @param stopState the ATN state to stop at. This can be a
    # {@link BlockEndState} to detect epsilon paths through a closure.
    # @param ctx the complete parser context, or {@code null} if the context
    # should be ignored
    #
    # @return The set of tokens that can follow {@code s} in the ATN in the
    # specified {@code ctx}.
    #/
    def LOOK(self, s, stopState=None, ctx=None):
        r = IntervalSet()
        seeThruPreds = True # ignore preds; get all lookahead
        lookContext = PredictionContextFromRuleContext(s.atn, ctx) if ctx is not None else None
        self._LOOK(s, stopState, lookContext, r, set(), set(), seeThruPreds, True)
        return r

    #*
    # Compute set of tokens that can follow {@code s} in the ATN in the
    # specified {@code ctx}.
    #
    # <p>If {@code ctx} is {@code null} and {@code stopState} or the end of the
    # rule containing {@code s} is reached, {@link Token#EPSILON} is added to
    # the result set. If {@code ctx} is not {@code null} and {@code addEOF} is
    # {@code true} and {@code stopState} or the end of the outermost rule is
    # reached, {@link Token#EOF} is added to the result set.</p>
    #
    # @param s the ATN state.
    # @param stopState the ATN state to stop at. This can be a
    # {@link BlockEndState} to detect epsilon paths through a closure.
    # @param ctx The outer context, or {@code null} if the outer context should
    # not be used.
    # @param look The result lookahead set.
    # @param lookBusy A set used for preventing epsilon closures in the ATN
    # from causing a stack overflow. Outside code should pass
    # {@code new HashSet<ATNConfig>} for this argument.
    # @param calledRuleStack A set used for preventing left recursion in the
    # ATN from causing a stack overflow. Outside code should pass
    # {@code new BitSet()} for this argument.
    # @param seeThruPreds {@code true} to true semantic predicates as
    # implicitly {@code true} and "see through them", otherwise {@code false}
    # to treat semantic predicates as opaque and add {@link #HIT_PRED} to the
    # result if one is encountered.
    # @param addEOF Add {@link Token#EOF} to the result if the end of the
    # outermost context is reached. This parameter has no effect if {@code ctx}
    # is {@code null}.
    #/
    def _LOOK(self, s, stopState , ctx, look, lookBusy, \
                     calledRuleStack, seeThruPreds, addEOF):
        c = ATNConfig(s, 0, ctx)

        if c in lookBusy:
            return
        lookBusy.add(c)

        if s == stopState:
            if ctx is None:
                look.addOne(Token.EPSILON)
                return
            elif ctx.isEmpty() and addEOF:
                look.addOne(Token.EOF)
                return

        if isinstance(s, RuleStopState ):
            if ctx is None:
                look.addOne(Token.EPSILON)
                return
            elif ctx.isEmpty() and addEOF:
                look.addOne(Token.EOF)
                return

            if ctx != PredictionContext.EMPTY:
                # run thru all possible stack tops in ctx
                for i in range(0, len(ctx)):
                    returnState = self.atn.states[ctx.getReturnState(i)]
                    removed = returnState.ruleIndex in calledRuleStack
                    try:
                        calledRuleStack.discard(returnState.ruleIndex)
                        self._LOOK(returnState, stopState, ctx.getParent(i), look, lookBusy, calledRuleStack, seeThruPreds, addEOF)
                    finally:
                        if removed:
                            calledRuleStack.add(returnState.ruleIndex)
                return

        for t in s.transitions:
            if type(t) == RuleTransition:
                if t.target.ruleIndex in calledRuleStack:
                    continue

                newContext = SingletonPredictionContext.create(ctx, t.followState.stateNumber)

                try:
                    calledRuleStack.add(t.target.ruleIndex)
                    self._LOOK(t.target, stopState, newContext, look, lookBusy, calledRuleStack, seeThruPreds, addEOF)
                finally:
                    calledRuleStack.remove(t.target.ruleIndex)
            elif isinstance(t, AbstractPredicateTransition ):
                if seeThruPreds:
                    self._LOOK(t.target, stopState, ctx, look, lookBusy, calledRuleStack, seeThruPreds, addEOF)
                else:
                    look.addOne(self.HIT_PRED)
            elif t.isEpsilon:
                self._LOOK(t.target, stopState, ctx, look, lookBusy, calledRuleStack, seeThruPreds, addEOF)
            elif type(t) == WildcardTransition:
                look.addRange( Interval(Token.MIN_USER_TOKEN_TYPE, self.atn.maxTokenType + 1) )
            else:
                set = t.label
                if set is not None:
                    if isinstance(t, NotSetTransition):
                        set = set.complement(Token.MIN_USER_TOKEN_TYPE, self.atn.maxTokenType)
                    look.addSet(set)
