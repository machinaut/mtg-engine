#!/usr/bin/env python
"""
Decision Engine class and utilities

The Engine class holds the core game state,
and sends/receives messages to/from players.
"""
import logging
from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from typing import Generator, List

from numpy import isin

from mtg_engine.decision_engine.message import Choice, Decision, View, Views
from mtg_engine.decision_engine.player import Player

# This is our typevar for the nested coroutines we use.
MessageGen = Generator[Views | Choice, Decision | None, Decision | None]


@dataclass
class Engine:
    """Engine class is the core of the game.
    It holds the state of the game,
    and sends/receives messages to/from players.
    """

    players: List[Player]

    @property
    def num_players(self) -> int:
        """Number of players in the game"""
        return len(self.players)

    def is_valid_player(self, player: int) -> bool:
        """Is this a valid player number"""
        return isinstance(player, int) and (0 <= player < self.num_players)

    def is_valid_views(self, views: Views) -> bool:
        """Check if the views are valid"""
        return isinstance(views, Views) and (len(views) == self.num_players)

    def is_valid_choice(self, choice: Choice) -> bool:
        """Check if the choice is valid"""
        return isinstance(choice, Choice) and (choice.player in range(self.num_players))

    def play(self) -> MessageGen:
        """Core coroutine in the game engine.
        Override this to implement your own game logic.
        """
        raise NotImplementedError

    def is_valid_player(self, player: int) -> bool:
        """Check if the player is valid"""
        return isinstance(player, int) and (0 <= player < self.num_players)

    def run(self):
        """Run the engine, until the game is finished"""
        logging.debug("Running engine: %s", self)
        game_generator = self.play()
        message = next(game_generator)
        while True:
            reply = self.send_receive(message)
            try:
                message = game_generator.send(reply)
            except StopIteration:
                break
        logging.debug("Completed engine: %s", self)

    def send_receive(self, message: Choice | Views) -> Decision | None:
        """Send the given message, and return the reply if any"""
        # If a choice, send it to the player, and return the result
        if isinstance(message, Choice):
            choice = message
            assert self.is_valid_choice(choice), f"Invalid {choice}"
            decision = self.players[choice.player].choice(choice)
            assert choice.is_valid_decision(decision), f"Invalid {decision}"
            return decision
        # If a views, send it to all players, and return None
        if isinstance(message, Views):
            views = message
            assert self.is_valid_views(views), f"Invalid {views}"
            for player, view in zip(self.players, views):
                assert isinstance(view, View), f"{view}"
                player.view(view)  # Send the view to the player
            return None
        # If neither, raise an error
        raise ValueError(f"{message} is not a Choice or Views")
