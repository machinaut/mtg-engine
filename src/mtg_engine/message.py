#!/usr/bin/env python
"""
mtg_engine.message - Message class and subclasses

The message class is the superclass of View, Choice, and Decision.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Message:
    """Message class is sent between the engine and players."""

    pass


@dataclass
class View(Message):
    """View class is a message sent to a player,
    containing information about what has changed."""

    pass


@dataclass
class Views(Message):
    """Class containing multiple views, one for each player"""

    views: List[View]

    def append(self, view):
        """Append a view to the list"""
        assert isinstance(view, View)
        self.views.append(view)


# @dataclass
# class Description:
#     """Description is the description of a choice to be made,
#     but does not contain any options."""

#     pass


@dataclass
class Option:
    """Option class is a distinct choice in a Choice class."""

    pass


@dataclass
class Choice(Message):
    """Choice class is a message sent to a player,
    asking them to make a decision.

    Choices have a description, which gives the choice to be made.

    Choices have two or more options, and exactly one must be chosen.
    All options must be distinct, and non-distinct options are combined/ignored.
    """

    desc: str
    options: List[Option]

    def __len__(self) -> int:
        return len(self.options)


@dataclass
class Decision(Message):
    """Decision class is a message sent to the engine,
    in response to a choice.
    It just contains the index of the chosen option.
    """

    option: int


@dataclass
class MessageBundle:
    """MessageBundle class is a bunch of Views followed by a single Choice,
    which is how the Game class stacks messages.
    """

    choice: Choice
    choice_player: int  # Which player the choice goes to
    views: List[Views] = field(default_factory=list)
