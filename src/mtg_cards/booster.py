#!/usr/bin/env python
"""
`mtg_cards.booster` MTG card booster dataclasses

Callers should make BoosterBox objects, and use them to make boosters.
"""
# %% # Sample random booster packs
import logging
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from mtg_cards.cards import Card, Cards


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


@dataclass
class BoosterProbsCache:
    """Singleton container for booser probabilities"""

    sets: Dict[str, BoosterProbs] = field(default_factory=dict)

    def get_booster_probs(self, set_name: str) -> BoosterProbs:
        """Get the booster pack probs for this set."""
        if set_name not in self.sets:
            logging.debug("Computing booster probs for %s", set_name)
            if set_name == "neo":
                import mtg_cards.neo_booster

                booster_probs = mtg_cards.neo_booster.get_booster_probs()
            else:
                raise ValueError(f"Unknown set {set_name}")
            # Check we got all 15 slots
            assert len(booster_probs) == 15, f"{len(booster_probs)}"
            # Sort them by card name for easier debugging
            booster_probs.sort()
            # Add to cache
            self.sets[set_name] = booster_probs
        return self.sets[set_name]


booster_probs_cache = BoosterProbsCache()
get_booster_probs = booster_probs_cache.get_booster_probs


@dataclass
class BoosterBox:
    """A booster pack factory"""

    set_name: str  # 3-letter lowercase code for the set (e.g. "neo")
    rng: Optional[random.Random] = None

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()
        self.booster_probs = get_booster_probs(self.set_name)

    def get_booster(self) -> Cards:
        """Return a booster pack"""
        # Pick the cards
        cards = []
        for slot_probs in self.booster_probs:
            cards.append(slot_probs.sample(rng=self.rng))
        return Cards(cards)


if __name__ == "__main__":
    # set to debug level
    logging.basicConfig(level=logging.DEBUG)
    # Render a booster pack
    for i in range(10):
        box = BoosterBox("neo", rng=random.Random(i))
        box.get_booster().render(rowsize=15)
