#!/usr/bin/env python
"""
Core Deck class and subclasses
"""

from dataclasses import dataclass, field

from mtg_engine.mtg_cards.cards import Cards
from mtg_engine.mtg_cards.sets import get_basics, get_set


@dataclass
class Deck:
    """Interface for building a deck from a pool of cards.

    The pool is fixed and shouldn't change.

    Any number of basic lands may be picked at any time.

    Any not picked cards are in the sideboard.
    """

    main: Cards = field(default_factory=Cards)
    sideboard: Cards = field(default_factory=Cards)
    basics: Cards = field(default_factory=lambda: get_basics("neo").unique())

    @property
    def pool(self) -> Cards:
        """Return the whole pool"""
        return self.main + self.sideboard

    def legal(self) -> bool:
        """Return true if this deck is legal for its format.
        Must be implemented in subclasses"""
        raise NotImplementedError

    def render(self):
        """Render the cards in the main deck"""
        self.main.render(rowsize=10)

    def render_pool(self):
        """Render the cards in the pool / sideboard"""
        self.pool.render(rowsize=15)

    def sort(self):
        """Sort the main deck and sideboard"""
        self.main.sort()
        self.sideboard.sort()

    @property
    def can_pick(self):
        """Return true if there are any cards in the pool"""
        return len(self.sideboard) > 0

    @property
    def can_unpick(self):
        """Return true if there are any cards in the main deck"""
        return len(self.main) > 0

    def pick(self, card):
        """Pick a card for the main deck from the sideboard"""
        if card in self.sideboard:
            self.sideboard.remove(card)
            self.main.append(card)
        elif card in self.basics:
            self.main.append(card)
        else:
            raise ValueError(f"None left in the sideboard {card}")

    def unpick(self, card):
        """Unpick a card from the main deck to the sideboard"""
        if card in self.main:
            self.main.remove(card)
            if card not in self.basics:
                self.sideboard.append(card)
        else:
            raise ValueError(f"{card} is not in the main deck")

    def unify_basics(self):
        """Ensure all basics have the same art in the main deck"""
        assert len(self.basics) == 5, f"{self.basics}"
        for basic in self.basics:
            for card in self.main.get_by_name(basic.name):
                self.unpick(card)
                self.pick(basic)


@dataclass
class LimitedDeck(Deck):
    """A deck for the limited formats (Draft, Sealed)"""

    set_name: str = "neo"

    def __post_init__(self):
        """Get a handle to the set object"""
        self.set_ = get_set(self.set_name)
        self.basics = self.set_.basics.unique()

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
