#!/usr/bin/env python
"""
mtg_engine.game - Game class

The core Game class is held by an Engine,
and is structured as a Message generator, game.play().

Game logic is separated into generators,
which can call into subgenerators.
"""

from dataclasses import dataclass, field
from random import Random
from typing import Generator, List, Optional

from mtg_engine.choice import FirstPlayerChoice
from mtg_engine.message import MessageBundle, Views
from mtg_engine.player import Player
from mtg_engine.view import DeckSizeView, DeckView

# This is our typevar for the nested coroutines we use.
GameGenerator = Generator[MessageBundle, int, None]


@dataclass
class Game:
    """Core game logic and state"""

    players: List[Player]
    turn: int = 0
    rng: Random = field(default=Random, repr=False)

    @classmethod
    def make(cls, players: List[Player], rng: Optional[Random] = None) -> GameGenerator:
        """Make a new game, with the given players"""
        if rng is None:
            rng = Random()
        return cls(players, rng=rng)

    def play(self) -> GameGenerator:
        """Core coroutine in the game engine.

        Game play progresses until a choice needs to be made,
        and at that point yields all the messages that need to be sent.
        """
        message_bundle = yield from self.setup()

    def setup(self) -> GameGenerator:
        """Setting up the game, before the first turn"""
        # The first messages we send to the players are their order and deck info
        # Players see their own deck contents, but only the size of their opponents.
        deck_views = []
        # We create a view for each player, for each other player, then send in play order
        for i in range(len.self.players):
            views = Views
            for j, player in enumerate(self.players):
                if i == j:
                    view = DeckView(player.deck)
                else:
                    view = DeckSizeView(len(player.deck))
                views.append(view)
            deck_views.append(views)
        # Randomly pick to see who picks who goes first
        picks_first = self.rng.randint(0, len(self.players) - 1)
        # That player gets sent the first choice
        choice = FirstPlayerChoice.make(len(self.players))
        decision = yield MessageBundle(views=deck_views, choice=choice)
