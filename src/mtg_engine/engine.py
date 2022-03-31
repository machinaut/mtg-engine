#!/usr/bin/env python
"""
`mtg_engine.engine` - Engine class and utilities

The Engine class holds the core game state,
and sends/receives messages to/from players.
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional

from mtg_engine.game import Game
from mtg_engine.player import Player


@dataclass
class Engine:
    """Engine class is the core of the game.
    It holds the state of the game,
    and sends/receives messages to/from players.
    """

    game: Game
    players: List[Player]
    rng: Optional[random.Random] = field(default=None, repr=False)

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()

    def run(self):
        """Run the engine, until the game is finished"""
