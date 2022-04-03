#!/usr/bin/env python
""" Zone class and subclasses """
from dataclasses import dataclass


@dataclass
class Zone:
    """
    Zone:
    A place where objects can be during a game.
    See section 4, "Zones."
    """


@dataclass
class Library(Zone):
    """
    Library:
    1. A zone. A player's library is where that player draws cards from.
    2. All the cards in a player's library.
    See rule 401, "Library."
    """


@dataclass
class Hand(Zone):
    """
    Hand:
    1. A zone. A player's hand is where that player holds cards they have drawn but not played yet.
    2. All the cards in a player's hand.
    See rule 402, "Hand."
    """


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
