#!/usr/bin/env python
"""
`mtg_decks.sealed` - Interface for building a sealed deck

TODO: inherit / use Deck class
"""
# %%
import random
from dataclasses import dataclass
from typing import Optional

from mtg_cards.booster import BoosterBox
from mtg_cards.cards import Cards
from mtg_decks.decks import LimitedDeck


@dataclass
class Sealed(LimitedDeck):
    """Interface for building a sealed deck"""

    @classmethod
    def make(
        cls,
        set_name: str = "neo",
        rng: Optional[random.Random] = None,
        box: Optional[BoosterBox] = None,
    ):
        """Make a new Sealed card pool"""
        assert (rng is None) or (box is None), "Cannot specify both rng and box"
        if rng is None:
            rng = random.Random()
        if box is None:
            box = BoosterBox(set_name, rng)
        packs = [box.get_booster() for _ in range(6)]
        pool = sum(packs, Cards())  # Concatenate
        return cls(set_name=set_name, pool=pool)


if __name__ == "__main__":
    sealed = Sealed.make(rng=random.Random(0))
    sealed.render_pool()
