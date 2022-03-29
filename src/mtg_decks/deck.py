#!/usr/bin/env python
# %% # Limited Deck Building

from dataclasses import dataclass, field

from mtg_cards.cards import Card, Cards


@dataclass
class Deck:
    """Interface for building a deck from a pool of cards.

    Any number of basic lands may be added at any time.

    Individual cards should be moved from the pool to the main deck.

    The remaining cards in the pool will be the sideboard.
    """

    pool: Cards
    main: Cards = field(default_factory=Cards)

    def legal(self) -> bool:
        """Return true if this deck is legal for its format"""
        raise NotImplementedError


@dataclass
class LimitedDeck(Deck):
    """A deck for the limited formats (Draft, Sealed)"""

    set_name: str = "neo"

    def legal(self) -> bool:
        """Return true if this deck is legal for its format"""
        pass
