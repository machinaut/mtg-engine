#!/usr/bin/env python
"""
mtg_engine.player - Player class

The player mostly receives messages from the engine,
but will also send some in response.

The player keeps a record of all messages in a history,
which can be used as sequential context for AI.
"""
from dataclasses import dataclass, field
from random import Random
from typing import List, Optional

from mtg_decks.decks import Deck
from mtg_engine.message import Choice, Decision, Message, View


@dataclass
class Player:
    """Player class is the interface between the engine and the player.
    It receives messages from the engine, and sends messages to the engine.

    The Player instance is held by the engine, so the engine will call methods
    on it in order to send / receive messages.

    The Player class needs to be subclassed to implement the actual logic.
    """

    deck: Deck  # Starting deck
    history: List[Message] = field(default_factory=list)

    def view(self, view) -> None:
        """Send a View message to the engine"""
        assert isinstance(view, View)
        # Subclasses may also want to update some internal state
        self.history.append(view)

    def choice(self, choice) -> Decision:
        """Receive a choice message from the engine,
        and respond with a decision.

        Subclasses should override self.decide() instead of this method,
        in order to preserve the history writing logic.
        """
        assert isinstance(choice, Choice)
        self.history.append(choice)
        # This is where the logic happens, so override it in subclasses
        decision = self.decide(choice)
        assert isinstance(decision, Decision)
        self.history.append(decision)
        return decision

    def decide(self, choice) -> Decision:
        """Override in subclasses.  Make a decision"""
        raise NotImplementedError


@dataclass
class RandomPlayer(Player):
    rng: Random = field(default_factory=Random, repr=False)

    @classmethod
    def make(cls, deck: Deck, rng: Optional[Random] = None) -> "RandomPlayer":
        """Make a new random player, with the given deck"""
        if rng is None:
            rng = Random()
        return cls(deck, rng=rng)

    def decide(self, choice) -> Decision:
        """Make a random decision"""
        assert isinstance(choice, Choice)
        option = self.rng.randint(0, len(choice.options) - 1)
        return Decision(option)
