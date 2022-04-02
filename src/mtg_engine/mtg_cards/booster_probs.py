#!/usr/bin/env python
"""
`mtg_cards.booster_probs` MTG card booster probabilities dataclasses

Callers should use mtg_cards.booster to get a BoosterBox, and not this module.
"""
# %% # Sample random booster packs
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List

from mtg_engine.mtg_cards.cards import Card, Cards


@dataclass
class Prob:
    """A probability for a single card in a single slot"""

    card: Card
    prob: float


@dataclass
class SlotProb:
    """Probabilities for a single slot in a booster"""

    probs: List[Prob] = field(default_factory=list)

    @classmethod
    def from_cards_probs(cls, cards: Cards, probs: List[float]):
        """Create a SlotProb from a list of cards and their probabilities"""
        assert len(cards) == len(probs)
        return cls([Prob(card, prob) for card, prob in zip(cards, probs)])

    def __add__(self, other):
        """Combine probabilites of duplicate cards"""
        assert isinstance(other, SlotProb), f"{other} is not a SlotProb"
        combined_probs = defaultdict(float)
        for prob in self.probs + other.probs:
            combined_probs[prob.card] += prob.prob
        return SlotProb([Prob(card, prob) for card, prob in combined_probs.items()])

    def normalize(self):
        """Return normalized probabilities to sum to 1"""
        total = sum(prob.prob for prob in self.probs)
        return SlotProb([Prob(prob.card, prob.prob / total) for prob in self.probs])

    def sort(self):
        """Sort by card name"""
        self.probs.sort(key=lambda prob: prob.card.name)

    def sample(self, rng: random.Random) -> Card:
        """Sample a card from this slot"""
        weights = [prob.prob for prob in self.probs]
        (prob,) = rng.choices(self.probs, weights=weights)
        return prob.card


@dataclass
class BoosterProbs:
    """Singleton class to hold the booster pack probabilities"""

    set_name: str  # 3-letter lowercase code for the set (e.g. "neo")
    probs: List[SlotProb] = field(default_factory=list)

    def __len__(self):
        """Return the number of slots in a booster"""
        return len(self.probs)

    def __iter__(self):
        """Return an iterator over all of the slots"""
        return iter(self.probs)

    def sort(self):
        """Sort all of the slots by card name"""
        for prob in self.probs:
            prob.sort()
