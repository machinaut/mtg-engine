#!/usr/bin/env python
"""
mtg_engine.view - View subclasses

View is a subclass of message, and defined in the message module.

This module is for specific views that provide specific information.
"""
from dataclasses import dataclass, field

from mtg_cards.cards import Cards

from mtg_engine.message import View


@dataclass
class DeckView(View):
    """View class for the player's deck"""

    deck: Cards  # list of cards


@dataclass
class DeckSizeView(View):
    """View class for the opponent's deck size"""

    size: int
