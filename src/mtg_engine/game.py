#!/usr/bin/env python
"""
mtg_engine.game - Game class

The core Game class is held by an Engine,
and is structured as a Message generator
"""

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Game:
    """Core game logic and state"""

    rng: Optional[random.Random] = field(default=None, repr=False)

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()
