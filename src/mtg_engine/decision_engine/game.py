#!/usr/bin/env python
"""
Game class used by the engine.

The core functionality of the class is in being a message-bundle generator,
and works as a couroutine.

Decisions are .send()ed to the game, which yields MessageBundles.

The core type here is the GameGenerator, which the core generator,
as well as all subgenerators, are.
"""

from dataclasses import dataclass, field
from random import Random
from typing import Generator, List, Optional

from mtg_engine.decision_engine.message import MessageBundle, Views
from mtg_engine.decision_engine.player import Player

# This is our typevar for the nested coroutines we use.
GameGenerator = Generator[MessageBundle, int, None]


@dataclass
class Game:
    """Core game logic and state"""

    players: List[Player]

    @property
    def num_players(self) -> int:
        """Number of players in the game"""
        return len(self.players)

    def play(self) -> GameGenerator:
        """Core coroutine in the game engine.

        Game play progresses until a choice needs to be made,
        and at that point yields all the messages that need to be sent.
        """
        raise NotImplementedError
