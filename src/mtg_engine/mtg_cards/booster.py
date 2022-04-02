#!/usr/bin/env python
"""
`mtg_cards.booster` MTG card booster dataclasses

Callers should make BoosterBox objects, and use them to make boosters.
"""
# %% # Sample random booster packs
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from mtg_engine.mtg_cards.booster_probs import BoosterProbs
from mtg_engine.mtg_cards.cards import Cards
from mtg_engine.mtg_cards.neo_booster import get_booster_probs as get_booster_probs_neo


@dataclass
class BoosterProbsCache:
    """Singleton container for booser probabilities"""

    sets: Dict[str, BoosterProbs] = field(default_factory=dict)

    def get_booster_probs(self, set_name: str) -> BoosterProbs:
        """Get the booster pack probs for this set."""
        if set_name not in self.sets:
            logging.debug("Computing booster probs for %s", set_name)
            if set_name == "neo":
                booster_probs = get_booster_probs_neo()
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
