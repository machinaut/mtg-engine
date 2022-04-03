#!/usr/bin/env python
""" Object classes and subclasses """
from dataclasses import dataclass


@dataclass
class Object:
    """
    Object:
    An ability on the stack, a card, a copy of a card, an emblem,
    a token, a spell, or a permanent.
    See rule 109, "Objects."
    """


@dataclass
class AbilityOnStack(Object):
    """
    Ability:
    1. Text on an object that explains what that object does or can do.
    2. An activated or triggered ability on the stack.
    This kind of ability is an object.
    See rule 113, "Abilities," and section 6, "Spells, Abilities, and Effects."
    """


@dataclass
class CardObject(Object):
    """
    Card:
    The standard component of the game.
    Magic cards may be traditional or nontraditional.
    Tokens aren't considered cards.
    In the text of spells or abilities, the term "card" is used only to refer to
    a card that's not on the battlefield or on the stack,
    such as a creature card in a player's hand.
    See rule 108, "Cards."
    """


@dataclass
class CopyObject(Object):
    """
    Copy:
    1. To create a new object whose copiable values have been set to those of another object.
    2. An object whose copiable values have been set to those of another object.
    See rule 707, "Copying Objects."
    """


@dataclass
class Emblem(Object):
    """
    Emblem:
    An emblem is a marker used to represent an object that has one or more abilities,
    but no other characteristics.
    See rule 114, "Emblems."
    """


@dataclass
class Token(Object):
    """
    Token:
    A marker used to represent any permanent that isn't represented by a card.
    See rule 111, "Tokens."
    """


@dataclass
class Spell(Object):
    """
    Spell:
    A card on the stack.
    Also a copy (of either a card or another spell) on the stack.
    See rule 112, "Spells."
    """


@dataclass
class Permanent(Object):
    """
    Permanent:
    A card or token on the battlefield.
    See rule 110, "Permanents."
    """
