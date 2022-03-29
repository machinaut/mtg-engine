#!/usr/bin/env python
# %%
import random
from dataclasses import dataclass, field
from typing import Optional

from mtg_cards.booster import get_booster
from mtg_cards.cards import Card, Cards


@dataclass
class Sealed:
    cards: Cards
    set_name: str = "neo"

    @classmethod
    def make(cls, set_name: str = "neo", rng: Optional[random.Random] = None):
        if rng is None:
            rng = random.Random()
        packs = [get_booster(set_name=set_name, rng=rng) for _ in range(6)]
        cards = sum(packs, Cards())  # Concatenate
        return cls(cards=cards)

    def render(self):
        self.cards.render(rowsize=15)


if __name__ == "__main__":
    rng = random.Random(0)
    sealed = Sealed.make(rng=rng)
    sealed.render()
