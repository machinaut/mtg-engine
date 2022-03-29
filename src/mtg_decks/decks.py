#!/usr/bin/env python
"""
`mtg_decks.deck` - Deck class and subclasses (like Limited)
"""
import logging

# %% # Limited Deck Building
import random
from dataclasses import dataclass, field
from typing import Optional

from mtg_cards.cards import Cards
from mtg_cards.sets import get_set


@dataclass
class Deck:
    """Interface for building a deck from a pool of cards.

    The pool is fixed and shouldn't change.

    Any number of basic lands may be picked at any time.

    Any not picked cards are in the sideboard.
    """

    pool: Cards
    main: Cards = field(default_factory=Cards)

    @property
    def sideboard(self):
        """Return the sideboard"""
        return self.pool - self.main

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
        if self.pool.count(card) > self.main.count(card):
            self.main.append(card)
        elif card in self.basics:
            self.main.append(card)
        else:
            raise ValueError(f"None left in the pool {card}")

    def unpick(self, card):
        """Unpick a card from the main deck"""
        if card in self.main:
            self.main.remove(card)
        else:
            raise ValueError(f"{card} is not in the main deck")

    @property
    def can_pick(self):
        """Return true if there are any cards in the pool"""
        return len(self.sideboard) > 0

    @property
    def can_unpick(self):
        """Return true if there are any cards in the main deck"""
        return len(self.main) > 0


@dataclass
class DeckAgent:
    """Interface for a deck-building agent"""

    deck: Optional[Deck] = None

    def act(self):
        """Choose to pick or unpick a card"""
        raise NotImplementedError

    def done(self) -> bool:
        """Return true if the deck is complete"""
        raise NotImplementedError

    def run(self) -> bool:
        """Run the deck-building agent"""
        while not self.done():
            self.act()


@dataclass
class RandomDeckAgent(DeckAgent):
    """An agent that picks a random card"""

    rng: Optional[random.Random] = field(default=None, repr=False)

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()

    def pick(self):
        """Pick a random card from the pool"""
        assert self.deck is not None, f"{self}"
        assert self.deck.can_pick
        card = self.rng.choice(self.deck.sideboard)
        self.deck.pick(card)

    def unpick(self):
        """Unpick a random card from the main deck"""
        assert self.deck is not None, f"{self}"
        assert self.deck.can_unpick
        card = self.rng.choice(self.deck.main)
        self.deck.unpick(card)

    def act(self):
        """Choose to pick or unpick a card"""
        assert self.deck is not None, f"{self}"
        assert len(self.deck.pool) > 0
        choices = []
        assert self.deck.can_pick or self.deck.can_unpick
        if not self.deck.can_pick:
            self.unpick()
        elif not self.deck.can_unpick:
            self.pick()
        # Flip a coin, 90% pick, 10% unpick
        else:
            if self.rng.random() < 0.1:
                self.unpick()
            else:
                self.pick()

    def done(self) -> bool:
        """Return true if the deck is legal"""
        return self.deck.legal()
