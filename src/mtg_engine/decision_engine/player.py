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

from mtg_engine.decision_engine.message import Choice, Decision, Message, Option, View


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
        assert len(choice.options) > 0, f"{choice} has no options"
        self.history.append(choice)
        # This is where the logic happens, so override it in subclasses
        index = self.decide(choice)
        assert choice.is_valid_index(index), f"{index} invalid"
        decision = Decision(index=index, option=choice.options[index])
        self.history.append(decision)
        return decision

    def decide(self, choice) -> int:
        """Override in subclasses, engine will call choice() instead"""
        raise NotImplementedError


@dataclass
class FixedPlayer(Player):
    """Player that always chooses the first option"""

    def decide(self, choice) -> int:
        """Always choose the first option"""
        return 0


@dataclass
class RandomPlayer(Player):
    """Default player that makes random decisions"""

    rng: Random = field(default_factory=Random, repr=False)

    def __eq__(self, other):
        """Test equality without comparing rng state"""
        assert isinstance(other, RandomPlayer)
        return self.history == other.history

    def decide(self, choice) -> int:
        """Make a random decision"""
        assert isinstance(choice, Choice)
        return self.rng.randint(0, len(choice.options) - 1)


@dataclass
class BiasedPlayer(Player):
    """Random player that picks the first option with 50% probability,
    and the rest uniformly.
    """

    rng: Random = field(default_factory=Random, repr=False)

    def decide(self, choice) -> int:
        """Make a random decision"""
        assert isinstance(choice, Choice)
        if self.rng.random() < 0.5:
            return 0
        else:
            return self.rng.randint(1, len(choice.options) - 1)


@dataclass
class HumanPlayer(Player):
    """Default player which prints out all options and reads input"""

    def view(self, view) -> None:
        """Print out the view"""
        super().view(view)
        print(view)

    def decide(self, choice) -> int:
        """Read input from the user"""
        assert isinstance(choice, Choice)
        print("Player", choice.player, ", Choose an option:")
        for i, option in enumerate(choice.options):
            print(f"\tOption {i}: {option}")
        selection = -1
        while not choice.is_valid_index(selection):
            try:
                selection = int(input("Your choice: "))
            except ValueError:
                pass
            print("Invalid selection:", selection)
        return selection
