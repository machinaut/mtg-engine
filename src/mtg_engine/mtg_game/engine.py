#!/usr/bin/env python
"""
`mtg_engine.engine` - Engine class and utilities

The Engine class holds the core game state,
and sends/receives messages to/from players.
"""
import logging
from dataclasses import dataclass
from typing import List

from mtg_engine.decision_engine.message import Decision, MessageBundle, View, Views
from mtg_engine.decision_engine.player import Player


@dataclass
class Engine:
    """Engine class is the core of the game.
    It holds the state of the game,
    and sends/receives messages to/from players.
    """

    players: List[Player]

    def run(self):
        """Run the engine, until the game is finished"""
        logging.debug("Running engine: %s", self)
        game_generator = self.game.play()
        message_bundle = next(game_generator)
        while True:
            option_int = self.send_receive(message_bundle)
            try:
                message_bundle = game_generator.send(option_int)
            except StopIteration:
                break
        logging.debug("Completed engine: %s", self)

    def send_receive(self, message_bundle: MessageBundle) -> int:
        """Send all the messages in a MessageBundle, and return
        the chosen decision option.
        """
        assert isinstance(message_bundle, MessageBundle), f"{message_bundle}"
        # We might have a lot of views to send
        for views in message_bundle.views:
            assert isinstance(views, Views), f"{views}"
            # For each views, which is a set of views to be sent to every player
            for player, view in zip(self.players, views):
                assert isinstance(view, View), f"{view}"
                player.view(view)  # Send the view to the player
        # Send the choice to the correct player
        choice = message_bundle.choice
        assert isinstance(choice, int), f"{choice}"
        decision = self.players[message_bundle.player].choice(choice)
        assert isinstance(decision, Decision), f"{decision}"
        # return the chosen option
        return decision.option
