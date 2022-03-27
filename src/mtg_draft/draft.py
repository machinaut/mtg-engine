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
        # Get the packs, each player gets 3, saved as immutable
        # Note that the second and future packs might not be with the same player
        # Since we always index packs with (turn % player)
        booster = lambda: tuple(get_booster(set_name=self.set_name, rng=self.rng))
        self.starting_packs = tuple(tuple(booster() for _ in range(3)) for _ in range(self.players))
        # Current packs, will get updated as players draft
        # This is indexed by the starting position, not current player
        self.current_packs = [list(p[0]) for p in self.starting_packs]
        # This is which pick number we are currently on, which resets with new packs
        self.current_pick = 0
        # Turn increments by one with every pick
        self.turn = 0
        # History of packs seen by each player (immutable)
        self.seen = [[tuple(p)] for p in self.current_packs]
        # This is the current state of the packs, and will get updated
        self.packs = [[booster() for _ in range(3)] for _ in range(self.players)]
        # Store the pick index for each player for each turn
        self.picks = [[] for _ in range(self.players)]

    @property
    def pack(self) -> int:
        ''' Which pack are we on '''
        pack = self.turn // 15
        assert 0 <= pack < 45, f'{pack}'
        return pack

    def get_hist(self, player: int) -> list:
        ''' Get all the observations, which are tuples of (traj, picks, pack) '''
        assert isinstance(player, int) and (0 <= player < self.players), f'{player}'
        self.validate()
        picks = self.picks[player]
        packs = self.seen[player]
        assert len(packs) == len(picks) + 1, f'{len(packs)}, {len(picks)}'
        return DraftHistory(players=self.players, picks=picks, packs=packs)

    def pick(self, player:int, choice: int):
        ''' Make a pick for a player '''
        assert isinstance(player, int) and (0 <= player < self.players), f'{player}'
        current_pack = self.current_packs[self.turn % player]
        assert isinstance(choice, int) and (0 <= choice < len(self.packs[player])), f'{choice}'

        self.picks[player].append(choice)
        self.seen[player].append(self.packs[player][choice])
        self.packs[player].pop(choice)
        self.turn += 1

rng = random.Random(0)
draft = Draft(rng=rng)
draft.picks[0]