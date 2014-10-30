#
 #[The "BSD license"]
 # Copyright (c) 2013 Terence Parr
 # Copyright (c) 2013 Sam Harwell
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
from abc import ABCMeta, abstractmethod, abstractproperty

from antlr4._compat import add_metaclass, py2_unicode_compat, text_type


class LexerActionType(object):

    CHANNEL = 0     #The type of a {@link LexerChannelAction} action.
    CUSTOM = 1      #The type of a {@link LexerCustomAction} action.
    MODE = 2        #The type of a {@link LexerModeAction} action.
    MORE = 3        #The type of a {@link LexerMoreAction} action.
    POP_MODE = 4    #The type of a {@link LexerPopModeAction} action.
    PUSH_MODE = 5   #The type of a {@link LexerPushModeAction} action.
    SKIP = 6        #The type of a {@link LexerSkipAction} action.
    TYPE = 7        #The type of a {@link LexerTypeAction} action.


@add_metaclass(ABCMeta)
class LexerAction(object):
    @abstractproperty
    def actionType(self):
        pass

    @abstractproperty
    def isPositionDependent(self):
        pass

    @abstractmethod
    def execute(self, lexer):
        pass

#
# Implements the {@code skip} lexer action by calling {@link Lexer#skip}.
#
# <p>The {@code skip} command does not have any parameters, so this action is
# implemented as a singleton instance exposed by {@link #INSTANCE}.</p>
@py2_unicode_compat
class LexerSkipAction(LexerAction ):
    actionType = LexerActionType.SKIP
    isPositionDependent = False

    # Provides a singleton instance of this parameterless lexer action.
    INSTANCE = None

    def execute(self, lexer):
        lexer.skip()

    def __str__(self):
        return u"skip"

LexerSkipAction.INSTANCE = LexerSkipAction()

#  Implements the {@code type} lexer action by calling {@link Lexer#setType}
# with the assigned type.
@py2_unicode_compat
class LexerTypeAction(LexerAction):
    actionType = LexerActionType.TYPE
    isPositionDependent = False

    def __init__(self, type):
        self.type = type

    def execute(self, lexer):
        lexer.type = self.type

    def __hash__(self):
        return hash((self.actionType, self.type))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerTypeAction):
            return False
        else:
            return self.type == other.type

    def __str__(self):
        return u"type(" + text_type(self.type) + u")"


# Implements the {@code pushMode} lexer action by calling
# {@link Lexer#pushMode} with the assigned mode.
@py2_unicode_compat
class LexerPushModeAction(LexerAction):
    actionType = LexerActionType.PUSH_MODE
    isPositionDependent = False

    def __init__(self, mode):
        self.mode = mode

    # <p>This action is implemented by calling {@link Lexer#pushMode} with the
    # value provided by {@link #getMode}.</p>
    def execute(self, lexer):
        lexer.pushMode(self.mode)

    def __hash__(self):
        return hash((self.actionType, self.mode))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerPushModeAction):
            return False
        else:
            return self.mode == other.mode

    def __str__(self):
        return u"pushMode(" + text_type(self.mode) + u")"


# Implements the {@code popMode} lexer action by calling {@link Lexer#popMode}.
#
# <p>The {@code popMode} command does not have any parameters, so this action is
# implemented as a singleton instance exposed by {@link #INSTANCE}.</p>
@py2_unicode_compat
class LexerPopModeAction(LexerAction):
    actionType = LexerActionType.POP_MODE
    isPositionDependent = False

    INSTANCE = None

    # <p>This action is implemented by calling {@link Lexer#popMode}.</p>
    def execute(self, lexer):
        lexer.popMode()

    def __str__(self):
        return u"popMode"

LexerPopModeAction.INSTANCE = LexerPopModeAction()

# Implements the {@code more} lexer action by calling {@link Lexer#more}.
#
# <p>The {@code more} command does not have any parameters, so this action is
# implemented as a singleton instance exposed by {@link #INSTANCE}.</p>
@py2_unicode_compat
class LexerMoreAction(LexerAction):
    actionType = LexerActionType.MORE
    isPositionDependent = False

    INSTANCE = None

    # <p>This action is implemented by calling {@link Lexer#popMode}.</p>
    def execute(self, lexer):
        lexer.more()

    def __str__(self):
        return u"more"

LexerMoreAction.INSTANCE = LexerMoreAction()

# Implements the {@code mode} lexer action by calling {@link Lexer#mode} with
# the assigned mode.
@py2_unicode_compat
class LexerModeAction(LexerAction):
    actionType = LexerActionType.MODE
    isPositionDependent = False

    def __init__(self, mode):
        self.mode = mode

    # <p>This action is implemented by calling {@link Lexer#mode} with the
    # value provided by {@link #getMode}.</p>
    def execute(self, lexer):
        lexer.mode(self.mode)

    def __hash__(self):
        return hash((self.actionType, self.mode))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerModeAction):
            return False
        else:
            return self.mode == other.mode

    def __str__(self):
        return u"mode(" + text_type(self.mode) + u")"

# Executes a custom lexer action by calling {@link Recognizer#action} with the
# rule and action indexes assigned to the custom action. The implementation of
# a custom action is added to the generated code for the lexer in an override
# of {@link Recognizer#action} when the grammar is compiled.
#
# <p>This class may represent embedded actions created with the <code>{...}</code>
# syntax in ANTLR 4, as well as actions created for lexer commands where the
# command argument could not be evaluated when the grammar was compiled.</p>

class LexerCustomAction(LexerAction):
    actionType = LexerActionType.CUSTOM
    isPositionDependent = True

    # Constructs a custom lexer action with the specified rule and action
    # indexes.
    #
    # @param ruleIndex The rule index to use for calls to
    # {@link Recognizer#action}.
    # @param actionIndex The action index to use for calls to
    # {@link Recognizer#action}.
    #/
    def __init__(self, ruleIndex, actionIndex):
        self.ruleIndex = ruleIndex
        self.actionIndex = actionIndex

    # <p>Custom actions are implemented by calling {@link Lexer#action} with the
    # appropriate rule and action indexes.</p>
    def execute(self, lexer):
        lexer.action(None, self.ruleIndex, self.actionIndex)

    def __hash__(self):
        return hash((self.actionType, self.ruleIndex, self.actionIndex))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerCustomAction):
            return False
        else:
            return self.ruleIndex == other.ruleIndex and self.actionIndex == other.actionIndex

# Implements the {@code channel} lexer action by calling
# {@link Lexer#setChannel} with the assigned channel.
@py2_unicode_compat
class LexerChannelAction(LexerAction):
    actionType = LexerActionType.CHANNEL
    isPositionDependent = False

    # Constructs a new {@code channel} action with the specified channel value.
    # @param channel The channel value to pass to {@link Lexer#setChannel}.
    def __init__(self, channel):
        self.channel = channel

    # <p>This action is implemented by calling {@link Lexer#setChannel} with the
    # value provided by {@link #getChannel}.</p>
    def execute(self, lexer):
        lexer._channel = self.channel

    def __hash__(self):
        return hash((self.actionType, self.channel))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerChannelAction):
            return False
        else:
            return self.channel == other.channel

    def __str__(self):
        return u"channel(" + text_type(self.channel) + u")"

# This implementation of {@link LexerAction} is used for tracking input offsets
# for position-dependent actions within a {@link LexerActionExecutor}.
#
# <p>This action is not serialized as part of the ATN, and is only required for
# position-dependent lexer actions which appear at a location other than the
# end of a rule. For more information about DFA optimizations employed for
# lexer actions, see {@link LexerActionExecutor#append} and
# {@link LexerActionExecutor#fixOffsetBeforeMatch}.</p>
class LexerIndexedCustomAction(LexerAction):
    isPositionDependent = True

    # Constructs a new indexed custom action by associating a character offset
    # with a {@link LexerAction}.
    #
    # <p>Note: This class is only required for lexer actions for which
    # {@link LexerAction#isPositionDependent} returns {@code true}.</p>
    #
    # @param offset The offset into the input {@link CharStream}, relative to
    # the token start index, at which the specified lexer action should be
    # executed.
    # @param action The lexer action to execute at a particular offset in the
    # input {@link CharStream}.
    def __init__(self, offset, action):
        self._actionType = action.actionType
        self.offset = offset
        self.action = action

    @property
    def actionType(self):
        return self._actionType

    # <p>This method calls {@link #execute} on the result of {@link #getAction}
    # using the provided {@code lexer}.</p>
    def execute(self, lexer):
        # assume the input stream position was properly set by the calling code
        self.action.execute(lexer)

    def __hash__(self):
        return hash((self.offset, self.action))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, LexerIndexedCustomAction):
            return False
        else:
            return self.offset == other.offset and self.action == other.action
