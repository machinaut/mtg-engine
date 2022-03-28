#!/usr/bin/env python
# %% # Simulate a draft
import logging
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from urllib.parse import non_hierarchical

from mtg_cards.booster import get_booster
from mtg_cards.card import Card, Cards


@dataclass
class DraftPlayer:
    ''' Store the state of a single player during the draft '''
    player: int
    players: int
    pack: Optional[Cards] = None
    seen: List[Cards] = field(default_factory=list)
    picks: List[int] = field(default_factory=list)
    cards: List[Card] = field(default_factory=list)

    def pick(self, pick: int) -> Card:
        ''' Pick a card to remove from the pack '''
        assert 0 <= pick < len(self.pack), f'{pick}'
        pack = self.pack
        seen = pack.copy()
        card = pack.pick(pick)
        self.picks.append(pick)  # Add the pick to the list of picks
        self.seen.append(seen)  # Add the pack to the list of seen packs
        self.cards.append(card)  # Add the card to the list of cards
        # The draft will take the pack from us when everyone passes


@dataclass
class Draft:
    ''' Simulate a draft '''
    N: int = 8
    set_name: str = 'neo'
    rng: Optional[random.Random] = None
    current_pack: int = 0
    current_pick: int = 0
    turn: int = 0
    players: List[DraftPlayer] = field(default_factory=list)
    boosters: List[Cards] = field(default_factory=list)

    def get_booster(self):
        ''' Generate a booster pack using our internal RNG '''
        return get_booster(set_name=self.set_name, rng=self.rng)

    def get_player(self, i):
        ''' Create a new DraftPlayer and give them one of the booster packs '''
        return DraftPlayer(player=i, players=self.N, pack=self.get_booster())

    def __post_init__(self):
        assert 1 < self.N < 9, f'{self.N}'
        assert self.set_name == 'neo', f'{self.set_name}; only NEO for now'
        if self.rng is None:
            self.rng = random.Random()
        # Player objects, used to track each player's state
        self.players = [self.get_player(i) for i in range(self.N)]
        # Get the packs, each player starts with 1, so we need 2 more
        self.boosters = [self.get_booster() for _ in range(2 * self.N)]
        # Start the draft
        self.turn = 1
        self.current_pack = 1
        self.current_pick = 1

    @property
    def done(self) -> bool:
        ''' Check if the draft is done '''
        return self.turn >= 45

    def ready_to_pass(self) -> bool:
        ''' Check if we're ready to pass the packs '''
        return all(len(p.picks) == self.turn for p in self.players)

    def pass_packs(self):
        ''' Call this when all players have made a pick '''
        # assert we're not at the end of the draft
        assert 1 <= self.turn <= 45, f'{self.turn}'
        # increment the turn
        self.turn += 1
        if self.turn >= 45:
            return  # done with draft
        # increment the pick number, possibly opening a new pack
        self.current_pick += 1
        if self.current_pick > 15:
            logging.debug("Opening new pack")
            # Assert all the current packs are empty
            assert all(len(p.pack) == 0 for p in self.players), f'{self}'
            self.current_pack += 1
            self.current_pick = 1
            # Get new packs from boosters
            for player in self.players:
                player.pack = self.boosters.pop(0)
        else:
            # Pass to left, right, left
            pass_dir = [-1, +1][self.current_pack % 2]
            logging.debug(f"Passing to {pass_dir}")
            # Shift all of the packs
            packs = [p.pack for p in self.players]
            packs = packs[pass_dir:] + packs[:pass_dir]
            for player, pack in zip(self.players, packs):
                player.pack = pack

    def pick(self, i: int, choice: int, auto_pass: bool = True):
        ''' Make a pick for a player '''
        # Validate inputs
        assert isinstance(i, int) and (0 <= i < self.N), f'{i}'
        player = self.players[i]
        player.pick(choice)

        # If this is the last pick, pass the packs
        if auto_pass and self.ready_to_pass():
            self.pass_packs()


if __name__ == '__main__':
    # set logging level to debug
    logging.basicConfig(level=logging.DEBUG)
    rng = random.Random(0)
    N = 8
    draft = Draft(N=N, rng=rng)
    for i in range(45):
        for p in range(N):
            draft.pick(p, 0)
