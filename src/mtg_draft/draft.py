#!/usr/bin/env python
# %% # Simulate a draft
import random
from dataclasses import dataclass
from typing import Optional

from mtg_cards.booster import get_booster


@dataclass
class Draft:
    ''' Simulate a draft '''
    players: int = 8
    set_name: str = 'neo'
    rng: Optional[random.Random] = None

    def __post_init__(self):
        assert 1 < self.players < 9, f'{self.players}'
        assert self.set_name == 'neo', f'{self.set_name}; only NEO for now'
        if self.rng is None:
            self.rng = random.Random()
        # Get the packs, each player gets 3
        booster = lambda: get_booster(set_name=self.set_name, rng=self.rng)
        self.packs = [[booster() for _ in range(3)] for _ in range(self.players)]
        # Used to store the picks
        self.picks = [[] for _ in range(self.players)]
        self.trajs = [[] for _ in range(self.players)]
        self.turn = 0

    @property
    def pack(self) -> int:
        ''' Which pack are we on '''
        pack = self.turn // 15
        assert 0 <= pack < 45, f'{pack}'
        return pack

    def validate(self):
        ''' State correctness checks '''
        # Check that everyone has equal number of picks
        assert all(len(p) == self.turn for p in self.picks), f'{self.picks}'
        # Check that trajectories are all the same length
        assert all(len(t) == len(self.trajs[0]) for t in self.trajs), f'{self.trajs}'

    def get_obs(self) -> list:
        ''' Get all the observations, which are tuples of (traj, picks, pack) '''
        self.validate()
        return [(t, p, b[self.pack]) for t, p, b in zip(self.trajs, self.picks, self.packs)]


draft = Draft()
draft.get_obs()[0]