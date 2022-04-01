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
from typing import List

from mtg_engine.decision_engine.message import Choice, Decision, Message, View


@dataclass
class Player:
    """Player class is the interface between the engine and the player.
    It receives messages from the engine, and sends messages to the engine.

    The Player instance is held by the engine, so the engine will call methods
    on it in order to send / receive messages.

    The Player class needs to be subclassed to implement the actual logic.
    """

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
        assert isinstance(choice, Choice), f"{choice} is not a Choice"
        self.history.append(choice)
        # This is where the logic happens, so override it in subclasses
        chosen_option = self.decide(choice)
        assert choice.is_valid_option(chosen_option), f"{chosen_option} invalid"
        decision = Decision(option=chosen_option)
        self.history.append(decision)
        return decision

    def decide(self, choice) -> int:
        """Override in subclasses, engine will call choice() instead"""
        raise NotImplementedError


@dataclass
class RandomPlayer(Player):
    """Default player that makes random decisions"""

    rng: Random = field(default_factory=Random, repr=False)

    def decide(self, choice) -> Decision:
        """Make a random decision"""
        assert isinstance(choice, Choice)
        option = self.rng.randint(0, len(choice.options) - 1)
        return Decision(option)


@dataclass
class HumanPlayer(Player):
    """Default player which prints out all options and reads input"""

    def decide(self, choice) -> int:
        """Read input from the user"""
        assert isinstance(choice, Choice)
        print("Choose an option:")
        for i, option in enumerate(choice.options):
            print(f"\tOption {i}: {option}")
        option = -1
        while not choice.is_valid_option(option):
            try:
                option = int(input("Your choice: "))
            except ValueError:
                print("Invalid option:", option)
        return option
