#!/usr/bin/env python
"""
`mtg_engine.game` - core Game, GameAgents, and other classes

The basic design for how this should work is:
* GameRunner is in control of everything
* The runner itself makes all automatic and state-based actions happen
* The runner does not (yet) provide a list of valid actions
* Every time a decision needs to be made by an agent, it calls that agent
* The agent then has to return immediately after that decision is made
* So, for example, casting a spell might take many decisions (choices, targets, etc)
* Any randomness is _not_ handled by the agent, but by the game
* The game owns all entropy (e.g. dice rolls, coin flips, "pick a random card" etc)
* The game is also responsible for setting up the battlefield (shuffling libraries, etc)
* The game/runner is NOT fully rules-compliant right now
* It's possible for agents to submit actions that are legal but not implemented

GameAgent is the interface to human or AI players

This is very inefficient but should at least be able to work
"""
# %% # Limited Deck Building
import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from mtg_cards.cards import Card, Cards
from mtg_decks.decks import Deck
from mtg_decks.sealed import random_sealed_deck


@dataclass
class GamePlayer:
    """State tracking for a player in a game"""

    deck: Deck
    library: Cards = field(default_factory=Cards)
    hand: Cards = field(default_factory=Cards)
    life: int = 20


@dataclass
class Game:
    """Class for tracking a single game.
    Non-determinism in the game is owned here (e.g. dice rolls).
    """

    players: List[GamePlayer]
    done: bool = False  # Maybe make this a property?
    rng: Optional[random.Random] = field(default=None, repr=False)
    winner: Optional[int] = None  # None indicates draw if done=True

    def __post_init__(self):
        """Set up the board for the game up until first decision"""
        raise NotImplementedError

    @property
    def num_players(self):
        """Return the number of players"""
        return len(self.players)

    @property
    def is_multiplayer(self):
        """Return True if the game is multiplayer"""
        return len(self.players) > 2

    @classmethod
    def make(cls, decks: List[Deck]):
        """Create a new game, where the 0th player is the first to act"""
        # Assert all decks are legal
        assert all(deck.legal() for deck in decks), "Invalid deck"
        players = [GamePlayer(deck) for deck in decks]
        return cls(players)

    def step(self) -> Optional[int]:
        """Run the game until a decision needs to be made,
        then return the player index"""
        raise NotImplementedError


@dataclass
class GameAgent:
    """A single player in a Game"""

    player: GamePlayer
    game: Optional[Game] = None

    @property
    def deck(self):
        """Return the deck"""
        return self.player.deck

    def act(self):
        """Perform the next action"""
        raise NotImplementedError


@dataclass
class RandomGameAgent(GameAgent):
    """A random agent for a game"""

    rng: Optional[random.Random] = None

    def __post_init__(self):
        if self.rng is None:
            self.rng = random.Random()

    @classmethod
    def from_deck(cls, deck: Deck, rng: Optional[random.Random] = None):
        """Create a new agent from a deck"""
        return cls(game=None, player=GamePlayer(deck=deck), rng=rng)


@dataclass
class GameRunner:
    """Runs a Game given a list of agents,
    Where the first agent in the list chooses who goes first.
    Randomness (dice rolls, etc) are owned by Game.

    Note: runner.agents must match game.decks, so do not re-order either.
    """

    game: Game
    agents: List[GameAgent]
    priority: Optional[int] = None  # The index of the next player to act

    @classmethod
    def make(cls, agents: List[GameAgent], rng: Optional[random.Random] = None):
        """Make a new Game with the given agents"""
        game = Game(players=[agent.player for agent in agents], rng=rng)
        return cls(game=game, agents=agents)

    def run(self):
        """Run the game"""
        logging.debug("Starting game with %s agents", len(self.agents))

        # Take turns until the game is over
        while not self.game.done:
            self.priority = self.game.step()
            self.agents[self.priority].act()

        winner = self.game.winner
        logging.debug("Game is done, winner %s", winner)
        return winner


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    rng = random.Random(0)
    decks = [random_sealed_deck(rng=rng) for i in range(2)]
    agents = [RandomGameAgent.from_deck(deck) for deck in decks]
    runner = GameRunner.make(agents=agents, rng=rng)
    runner.run()
