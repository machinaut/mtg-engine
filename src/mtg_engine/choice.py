#!/usr/bin/env python
"""
mtg_engine.choice - Choice subclasses

Choice is a subclass of message, and defined in the message module.

This module is for specific choices that can be made.
"""
from dataclasses import dataclass, field

from mtg_cards.cards import Cards
from mtg_engine.message import Choice, Option


@dataclass
class FirstPlayerChoice(Choice):
    """Choice class for choosing who goes first"""

    @classmethod
    def make(cls, n_players: int):
        """Make a new choice, for the first player"""
        return cls(desc="Choose who goes first", options=list(range(n_players)))
