#!/usr/bin/env python
"""
Drafting, based on the Decision Engine.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from random import Random
from re import L
from typing import Dict, List

from mtg_engine.decision_engine.engine import Engine, MessageGen
from mtg_engine.decision_engine.message import Choice, Option, View, Views
from mtg_engine.decision_engine.player import HumanPlayer, Player, RandomPlayer
from mtg_engine.mtg_cards.booster import BoosterBox
from mtg_engine.mtg_cards.cards import Card, Cards


@dataclass
class PackView(View):
    """A pack passed or opened by a player"""

    desc: str = "Draft Pack"
    cards: List[int] = field(default_factory=list)


@dataclass
class PackViews(Views):
    """A set of views of each player's pack"""

    @classmethod
    def make(cls, packs: List[Cards]) -> "PackViews":
        """Create a set of views for each player"""
        return cls([PackView(cards=pack) for pack in packs])


@dataclass
class DraftPickOption(Option):
    """An option to pick a card"""

    card: Card = field(default_factory=Card)

    def __post_init__(self):
        self.desc = f"Pick {self.card}"


@dataclass
class DraftPickChoice(Choice):
    """Which card to pick"""

    desc: str = "Pick a card from the pack"

    @classmethod
    def make(cls, player: int, pack: Cards) -> "DraftPickChoice":
        """Create a choice from a pack of cards"""
        options: List[Option] = [DraftPickOption(card=card) for card in pack]
        return cls(player=player, options=options)


@dataclass
class DraftEngine(Engine):
    """Magic: the Gathering Drafting
    https://magic.wizards.com/en/formats/booster-draft
    """

    set_name: str = "neo"
    rng: Random = field(default_factory=Random, repr=False)
    packs: List[Cards] = field(default_factory=list)
    picks: Cards = field(default_factory=Cards)

    def get_new_packs(self):
        """Get new packs for every player"""
        assert all(len(pack) == 0 for pack in self.packs), "Packs should be empty"
        self.packs = [self.box.get_booster() for _ in range(self.num_players)]

    def pass_packs(self, left=True):
        """Rotate the packs to the left"""
        direction = -1 if left else 1
        self.packs = self.packs[direction:] + self.packs[:direction]

    def play(self) -> MessageGen:
        """Callers should use Engine.run(), see Engine for details"""
        assert 2 <= self.num_players <= 8, f"{self.num_players}"
        self.box = BoosterBox(set_name=self.set_name, rng=self.rng)
        for i in range(3):  # For each pack
            self.get_new_packs()  # Open pack
            for _ in range(15):  # For each card
                yield PackViews.make(self.packs)  # Show pack
                yield from self.get_picks()  # Pick card
                self.pass_packs(bool(i % 2))  # Pass pack
        return None

    def get_picks(self) -> MessageGen:
        """Get a pick choice from every player"""
        for i in range(self.num_players):
            choice = DraftPickChoice.make(player=i, pack=self.packs[i])
            decision = yield choice
            assert decision is not None and choice.is_valid_decision(decision)
            card = self.packs[i].pop(decision.option)
            self.picks.append(card)  # Add to picked cards for debugging purposes
        return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    rng = Random(0)
    players: List[Player] = [HumanPlayer(), RandomPlayer(rng=rng)]
    engine = DraftEngine(players=players, rng=rng)
    engine.run()
