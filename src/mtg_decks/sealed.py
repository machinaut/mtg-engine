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


@dataclass
class Sealed:
    """Interface for building a sealed deck"""

    cards: Cards
    set_name: str = "neo"

    @classmethod
    def make(cls, set_name: str = "neo", rng: Optional[random.Random] = None):
        """Make a new Sealed card pool"""
        if rng is None:
            rng = random.Random()
        box = BoosterBox(set_name=set_name, rng=rng)
        packs = [box.get_booster() for _ in range(6)]
        cards = sum(packs, Cards())  # Concatenate
        return cls(cards=cards)

    def render(self):
        """Render the cards in the sealed pool"""
        self.cards.render(rowsize=15)


if __name__ == "__main__":
    sealed = Sealed.make(rng=random.Random(0))
    sealed.render()
