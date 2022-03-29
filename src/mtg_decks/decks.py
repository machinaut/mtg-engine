#!/usr/bin/env python
"""
`mtg_decks.deck` - Deck class and subclasses (like Limited)
"""
# %% # Limited Deck Building
from dataclasses import dataclass, field

from mtg_cards.cards import Cards
from mtg_cards.sets import get_set


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

    def render(self):
        """Render the cards in the main deck"""
        self.main.render(rowsize=10)

    def render_pool(self):
        """Render the cards in the pool / sideboard"""
        self.pool.render(rowsize=15)

    def sort(self):
        """Sort the main deck and pool"""
        self.pool.sort()
        self.main.sort()


@dataclass
class LimitedDeck(Deck):
    """A deck for the limited formats (Draft, Sealed)"""

    set_name: str = "neo"

    def __post_init__(self):
        """Get a handle to the set object"""
        self.set_ = get_set(self.set_name)

    @property
    def basics(self):
        """Basic lands can always be picked from"""
        return self.set_.basics

    def legal(self) -> bool:
        """Return true if this deck is legal for its format"""
        # Are all the cards in the deck in the set
        if not all(card in self.set_ for card in self.pool):
            return False
        # Is the main deck at least 40 cards
        if len(self.main) < 40:
            return False
        # That's it!
        return True

    def pick(self, card):
        """Pick a card for the main deck"""
        if card in self.pool:
            self.main.append(card)
            self.pool.remove(card)
        elif card in self.basics:
            self.main.append(card)
        else:
            raise ValueError(f"{card} is not in the pool")

    def unpick(self, card):
        """Unpick a card from the main deck"""
        if card in self.main:
            # Only move non basic lands to the pool
            if card not in self.basics:
                self.pool.append(card)
            self.main.remove(card)
        else:
            raise ValueError(f"{card} is not in the main deck")
