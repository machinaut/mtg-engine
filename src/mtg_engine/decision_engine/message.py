#!/usr/bin/env python
"""
Message class and subclasses

The message class is the superclass of View, Choice, and Decision.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Message:
    """Message class is sent between the engine and players."""


@dataclass
class View(Message):
    """View class is a message sent to a player,
    containing information about what has changed."""

    desc: str = "Override View desc in View subclass"


@dataclass
class Views:  # Does not subclass Message
    """Class containing multiple views, one for each player"""

    views: List[View] = field(default_factory=list)

    def __len__(self):
        return len(self.views)

    def __iter__(self):
        return iter(self.views)

    def append(self, view):
        """Append a view to the list"""
        assert isinstance(view, View)
        self.views.append(view)


@dataclass
class Option:
    """Option class is a distinct choice in a Choice class."""

    desc: str = "Override Option desc in Option subclass"


@dataclass
class Decision(Message):
    """Decision class is a message sent to the engine,
    in response to a choice.
    It just contains the index of the chosen option.
    """

    index: int = -1000
    option: Option = field(default_factory=Option)


@dataclass
class Choice(Message):
    """Choice class is a message sent to a player,
    asking them to make a decision.

    Choices have a description, which gives the choice to be made.

    Choices have two or more options, and exactly one must be chosen.
    All options must be distinct, and non-distinct options are combined/ignored.
    """

    desc: str = "Override Choice description in Choice subclass"
    player: int = -1000
    options: List[Option] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.options)

    def __contains__(self, option: Option) -> bool:
        """Return True if the given option is valid"""
        assert isinstance(option, Option)
        # Check if the exact object is in the list, not just an equal object
        return any(option is o for o in self.options)

    def is_valid_index(self, index: int) -> bool:
        """Return True if the given index is valid"""
        assert isinstance(index, int)
        return 0 <= index < len(self)

    def is_valid_option(self, option: Option) -> bool:
        """Return True if the given option is valid"""
        return isinstance(option, Option) and option in self

    def is_valid_decision(self, decision: Decision) -> bool:
        """Return True if the given decision is valid"""
        return (
            isinstance(decision, Decision)
            and decision.option is self.options[decision.index]
        )
