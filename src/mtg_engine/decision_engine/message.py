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

    desc: str = "Override Message desc in Message subclass"


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

    option: int = -1000


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

    def is_valid_option(self, chosen: int) -> bool:
        """Return True if the given option is valid"""
        return isinstance(chosen, int) and (0 <= chosen < len(self.options))

    def is_valid_decision(self, decision: Decision) -> bool:
        """Return True if the given decision is valid"""
        return isinstance(decision, Decision) and self.is_valid_option(decision.option)
