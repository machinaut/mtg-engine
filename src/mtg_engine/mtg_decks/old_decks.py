#!/usr/bin/env python
"""
`mtg_decks.deck` - Deck class and subclasses (like Limited)
"""

import random
from dataclasses import dataclass, field
from typing import Optional

from mtg_engine.mtg_decks.decks import Deck


@dataclass
class DeckAgent:
    """Interface for a deck-building agent"""

    deck: Deck

    def act(self):
        """Choose to pick or unpick a card"""
        raise NotImplementedError

    def done(self) -> bool:
        """Return true if the deck is complete"""
        raise NotImplementedError

    def run(self) -> Deck:
        """Run the deck-building agent"""
        while not self.done():
            self.act()
        return self.deck


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
