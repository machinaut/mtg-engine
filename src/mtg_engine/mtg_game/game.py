#!/usr/bin/env python
"""
Drafting, based on the Decision Engine.
"""
import logging
from dataclasses import dataclass, field
from random import Random
from typing import List

from mtg_engine.decision_engine.engine import Engine, MessageGen
from mtg_engine.decision_engine.message import Choice, Option, View, Views
from mtg_engine.decision_engine.player import BiasedPlayer, HumanPlayer, Player
from mtg_engine.mtg_cards.cards import Card, Cards
from mtg_engine.mtg_cards.sets import get_basics
from mtg_engine.mtg_decks.decks import Deck, LimitedDeck


@dataclass
class StartFirstView(View):
    """Which player goes first"""

    desc: str = "Which player goes first, and who chose it"

    chooser: int = -1000
    player: int = -1000


@dataclass
class StartFirstViews(Views):
    """A set of views of which player goes first"""

    @classmethod
    def make(cls, chooser: int, player: int, num_players: int) -> "StartFirstViews":
        """Create a set of views for each player"""
        return cls(
            [StartFirstView(chooser=chooser, player=player) for _ in range(num_players)]
        )


@dataclass
class StartFirstOption(Option):
    """An option to choose the player to go first"""

    desc: str = "Which Player Starts"
    player: int = -1000


@dataclass
class StartFirstChoice(Choice):
    """Who goes first"""

    desc: str = "Choose which player goes first"

    @classmethod
    def make(cls, player: int, num_players: int) -> "StartFirstChoice":
        """Create a new StartFirstChoice"""
        options: List[Option] = [StartFirstOption(player=i) for i in range(num_players)]
        return cls(player=player, options=options)


@dataclass
class GameEngine(Engine):
    """Magic: the Gathering
    https://magic.wizards.com/en/formats/booster-draft
    """

    decks: List[Deck] = field(default_factory=list)
    rng: Random = field(default_factory=Random, repr=False)
    turn: int = -1

    def play(self) -> MessageGen:  # pylint: disable=useless-return
        """Callers should use Engine.run(), see Engine for details"""
        assert self.num_players >= 2, f"{self.num_players}"
        assert len(self.decks) == 2, f"{len(self.decks)}"
        yield from self.start()
        return None

    def start(self) -> MessageGen:  # pylint: disable=useless-return
        """103. Starting the Game
        https://yawgatog.com/resources/magic-rules/#R103"""
        # Pick who chooses who goes first
        chooser = self.rng.choice(range(self.num_players))
        choice = StartFirstChoice.make(player=chooser, num_players=self.num_players)
        decision = yield choice
        assert decision is not None and choice.is_valid_decision(decision)
        # Set the first player by setting the turn
        assert isinstance(decision.option, StartFirstOption)
        assert decision.index == decision.option.player
        self.turn = decision.index
        # Send the first view
        return (
            yield StartFirstViews.make(
                chooser=chooser,
                player=self.turn,
                num_players=self.num_players,
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    plains: Card = get_basics().cards[0]
    assert plains.name == "Plains", f"{plains}"
    deck = LimitedDeck(main=Cards([plains] * 40))
    assert deck.legal(), f"{deck}"
    decks: List[Deck] = [deck, deck]
    players: List[Player] = [HumanPlayer(), BiasedPlayer(rng=Random(0))]
    game_engine = GameEngine(players=players, decks=decks)
    game_engine.run()
