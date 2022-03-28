#!/usr/bin/env python
# %% # Simulate a draft
import logging
from optparse import Option
import random
from dataclasses import dataclass, field
from typing import List, Optional

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
    cards: Cards = field(default_factory=Cards)

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

    def get_booster(self) -> Cards:
        ''' Generate a booster pack using our internal RNG '''
        return get_booster(set_name=self.set_name, rng=self.rng)

    def get_player(self, i) -> DraftPlayer:
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

    def pass_packs(self) -> None:
        ''' Call this when all players have made a pick '''
        # assert we're not at the end of the draft
        assert 1 <= self.turn <= 45, f'{self.turn}'
        # assert everyone has made their picks for this turn
        assert all(len(p.picks) == self.turn for p in self.players), f'{self}'
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

    def pick(self, i: int, choice: int, auto_pass: bool = True) -> None:
        ''' Make a pick for a player '''
        # Validate inputs
        assert isinstance(i, int) and (0 <= i < self.N), f'{i}'
        player = self.players[i]
        player.pick(choice)

        # If this is the last pick, pass the packs
        if auto_pass and self.ready_to_pass():
            self.pass_packs()


@dataclass
class DraftAgent:
    ''' Base class for an agent participating in a draft '''
    player: Optional[DraftPlayer] = None  # our state in the draft

    def pick(self) -> int:
        ''' Make a pick, given the state of the draft '''
        raise NotImplementedError


@dataclass
class RandomDraftAgent(DraftAgent):
    ''' An agent that picks a random card '''
    rng: Optional[random.Random] = field(default=None, repr=False)

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()

    def pick(self) -> int:
        ''' Pick a random card '''
        assert self.player is not None, f'{self}'
        return random.randint(0, len(self.player.pack) - 1)

@dataclass
class HumanDraftAgent(DraftAgent):
    ''' A human interface to a draft '''

    def pick(self):
        ''' Get a human pick '''
        assert self.player is not None, f'{self}'
        # Print the cards
        print("Picked:")
        self.player.cards.render()
        # Print the pack
        print("Pack:")
        self.player.pack.render()
        for i, card in enumerate(self.player.pack):
            print(f'{i}: {card.name}')

        pick = None
        while pick is None:
            try:
                pick = int(input('Pick: '))
            except ValueError:
                print('Invalid pick')
                pick = None
            if pick < 0 or pick >= len(self.player.pack):
                print('Invalid pick')
                pick = None
        logging.debug(f"Picked {pick}")
        return pick


@dataclass
class DraftRunner:
    ''' Runs a draft with agents '''
    draft: Draft
    agents: List[DraftAgent]

    @classmethod
    def make(cls, N: int, agents: Optional[List[DraftAgent]] = None,  set_name: str='neo', rng: Optional[random.Random] = None) -> 'DraftRunner':
        ''' Make a new draft, filling in agents with RandomDraftAgent '''
        if rng is None:
            rng = random.Random()
        draft = Draft(N=N, set_name=set_name, rng=rng)
        # Pad out given agents with RandomDraftAgent
        if agents is None:
            agents = [RandomDraftAgent(rng=rng) for _ in range(N)]
        else:
            agents.append([RandomDraftAgent(rng=rng) for _ in range(N - len(agents))])
        assert len(agents) == N, f'{len(agents)} != {N}'
        # Assign agents to players
        for i, agent in enumerate(agents):
            agent.player = draft.players[i]
        return cls(draft=draft, agents=agents)

    def run(self) -> None:
        ''' Run the draft '''
        while not self.draft.done:
            print("Turn:", self.draft.turn)
            for i, agent in enumerate(self.agents):
                self.draft.pick(i, agent.pick())


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    N = 2
    rng = random.Random(0)
    agents = [HumanDraftAgent()]
    runner = DraftRunner.make(agents=agents, N=N, rng=rng)
    runner.run()
