#!/usr/bin/env python
""" Zone class and subclasses """
from dataclasses import dataclass, field
from typing import List

from mtg_engine.mtg_game.objects import Object


@dataclass
class Zone:
    """
    Zone:
    A place where objects can be during a game.
    See section 4, "Zones."
    """

    public: bool = True  # hidden zone if false
    objects: List[Object] = field(default_factory=list)

    def append(self, object_):
        """Append an object to the list"""
        assert isinstance(object_, Object)
        self.objects.append(object_)


@dataclass
class Library(Zone):
    """
    Library:
    1. A zone. A player's library is where that player draws cards from.
    2. All the cards in a player's library.
    See rule 401, "Library."
    """

    public: bool = False  # Hidden zone


@dataclass
class Hand(Zone):
    """
    Hand:
    1. A zone. A player's hand is where that player holds cards they have drawn but not played yet.
    2. All the cards in a player's hand.
    See rule 402, "Hand."
    """

    public: bool = False  # Hidden zone


@dataclass
class Battlefield(Zone):
    """
    Battlefield:
    A zone. The battlefield is the zone in which permanents exist.
    It used to be known as the "in-play" zone.
    See rule 403, "Battlefield."
    """


@dataclass
class Graveyard(Zone):
    """
    Graveyard:
    1. A zone. A player's graveyard is their discard pile.
    2. All the cards in a player's graveyard.
    See rule 404, "Graveyard."
    """


@dataclass
class Stack(Zone):
    """
    Stack:
    A zone. The stack is the zone in which spells, activated abilities,
    and triggered abilities wait to resolve.
    See rule 405, "Stack."
    """


@dataclass
class Exile(Zone):
    """
    Exile:
    1. A zone. Exile is essentially a holding area for cards.
    It used to be known as the "removed-from-the-game" zone.
    2. To put an object into the exile zone from whatever zone it's currently in.
    An "exiled" card is one that's been put into the exile zone.
    See rule 406, "Exile."
    """


@dataclass
class Command(Zone):
    """
    Command:
    A zone for certain specialized objects that have an overarching effect on the game,
    yet are not permanents and cannot be destroyed.
    See rule 408, "Command."
    """


@dataclass
class Zones:
    """Container class for all of the zones"""

    # Shared zones
    battlefield: Battlefield = field(default_factory=Battlefield)
    stack: Stack = field(default_factory=Stack)
    exile: Exile = field(default_factory=Exile)
    command: Command = field(default_factory=Command)
    # Zones for each player, indexed by player index
    libraries: List[Library] = field(default_factory=list)
    hands: List[Hand] = field(default_factory=list)
    graveyards: List[Graveyard] = field(default_factory=list)
