#!/usr/bin/env python
# %% # Simulate a draft
import random
from dataclasses import dataclass
from typing import Optional

from mtg_cards.booster import get_booster

@dataclass
class DraftHistory:
    ''' The draft history for a single player, with picks and packs seen '''
    players: int  # number of players
    picks: list  # picks made by this player
    packs: list  # packs seen by this player


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
        # This is the current state of the packs, and will get updated
        self.packs = [[booster() for _ in range(3)] for _ in range(self.players)]
        # Get an immutable copy of the starting state of the packs
        self.starting_packs = tuple(tuple(p) for p in self.packs)
        # Used to store the picks
        self.picks = [[] for _ in range(self.players)]
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