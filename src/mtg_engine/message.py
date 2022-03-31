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


@dataclass
class Description:
    """Description is the description of a choice to be made,
    but does not contain any options."""

    pass


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

    desc: Description
    options: List[Option]


@dataclass
class Decision(Message):
    """Decision class is a message sent to the engine,
    in response to a choice.
    It just contains the index of the chosen option.
    """

    option: int
