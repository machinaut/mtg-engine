#!/usr/bin/env python
"""
Example using the decision engine to make blackjack.

https://bicyclecards.com/how-to-play/blackjack/

Simplified to only be a single hand, with no betting.
"""
from dataclasses import dataclass, field
from random import Random
from typing import List

from mtg_engine.decision_engine.game import Game, GameGenerator
from mtg_engine.decision_engine.message import Choice, MessageBundle, View, Views

# Ignore suits, just using integer card values, where J/Q/K=10, A=1
CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


@dataclass
class FaceUpCardView(View):
    """A face_up card that everyone can see"""

    value: int  # Card value 1 = A, 2-9, 10 = J/Q/K
    player: int  # Player index


@dataclass
class FaceUpCardViews(Views):
    """A set of views for each player for a face-up card"""

    @classmethod
    def make(cls, value: int, player: int, num_players: int) -> "FaceUpCardViews":
        """Create a set of views for each player"""
        return cls([FaceUpCardView(value, player) for _ in range(num_players)])


@dataclass
class MyFacedownCard(View):
    """A face_down card that only the player can see"""

    value: int  # Card value 1 = A, 2-9, 10 = J/Q/K


@dataclass
class OtherFaceDownCard(View):
    """A face_down card that this player cannot see"""

    player: int  # Player index


@dataclass
class FacedownCardViews(Views):
    """A set of views for each player for a face-down card"""

    @classmethod
    def make(cls, value: int, player: int, num_players: int) -> "FacedownCardViews":
        """Create a set of views for each player"""
        views = []
        for i in range(num_players):
            if i == player:
                views.append(MyFacedownCard(value))
            else:
                views.append(OtherFaceDownCard(i))
        return cls(views)


@dataclass
class Blackjack(Game):
    """Simplified 1-player blackjack game"""

    rng: Random = field(default_factory=Random, repr=False)

    def draw(self) -> int:
        """Get a random card value"""
        return self.rng.choice(CARDS)

    def play(self) -> GameGenerator:
        """See documentation for more info about types"""
        # First card face up

    def deal(self) -> GameGenerator:
        """Deal everyone starting hands"""
        # First card face up
        message_bundle = MessageBundle()
        for i in range(self.num_players):
            views = FaceUpCardViews.make(self.draw(), i, self.num_players)
            message_bundle.views.append(views)
        # Second card face down
        for i in range(self.num_players):
            views = FacedownCardViews.make(self.draw(), i, self.num_players)
            message_bundle.views.append(views)
