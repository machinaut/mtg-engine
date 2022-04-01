#!/usr/bin/env python
"""
Example using the decision engine to make blackjack.

https://bicyclecards.com/how-to-play/blackjack/

Simplified to only be a single hand, with no betting.
"""
from collections import defaultdict
from dataclasses import dataclass, field
from random import Random
from typing import Dict, List

from mtg_engine.decision_engine.game import Game, GameGenerator
from mtg_engine.decision_engine.message import (
    Choice,
    MessageBundle,
    Option,
    View,
    Views,
)

# Ignore suits, just using integer card values, where J/Q/K=10, A=1
CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


@dataclass
class FaceUpCardView(View):
    """A face_up card that everyone can see"""

    value: int  # Card value 1 = A, 2-9, 10 = J/Q/K
    player: int  # Player index, -1 for dealer


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

    player: int  # Player index, -1 for dealer


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
class StandOption(Option):
    """An option to stand (end turn)"""

    desc: str = "Stand"


@dataclass
class HitOption(Option):
    """An option to hit (get another card)"""

    desc: str = "Hit"


@dataclass
class StandHitChoice(Choice):
    """A choice to stand or hit"""

    desc: str = "Stand or Hit"

    @classmethod
    def make(cls) -> "StandHitChoice":
        """Create a choice to stand or hit"""
        return cls(options=[StandOption(), HitOption()])


@dataclass
class WinnersView(View):
    """A view of the winners"""

    winners: List[int]  # List of player indices, empty means dealer won


@dataclass
class WinnersViews(Views):
    """A set of views for each player for the winners"""

    @classmethod
    def make(cls, winners: List[int], num_players: int) -> "WinnersViews":
        """Create a set of views for each player"""
        return cls([WinnersView(winners) for _ in range(num_players)])


@dataclass
class Blackjack(Game):
    """Simplified 1-player blackjack game"""

    rng: Random = field(default_factory=Random, repr=False)
    # map from player -> cards
    cards: Dict[int, List[int]] = field(default_factory=lambda: defaultdict(list))

    def draw(self) -> int:
        """Get a random card value"""
        return self.rng.choice(CARDS)

    def play(self) -> GameGenerator:
        """See documentation for more info about types"""
        # Setup the game
        result = yield from self.deal()
        assert result == -1, "Should not have a result"
        # Each player gets a turn
        for i in range(self.num_players):
            result = yield from self.turn(i)
            assert result == -1, "Should not have a result"
        # Dealer gets a turn
        result = yield from self.dealer_turn()
        assert result == -1, "Should not have a result"
        # Show the winners
        result = yield from self.show_winners()
        assert result == -1, "Should not have a result"
        return result

    def deal(self) -> GameGenerator:
        """Deal everyone starting hands"""
        # First card face up
        message_bundle = MessageBundle()
        # Deal to all the players, then dealer
        for i in list(range(self.num_players)) + [-1]:
            card = self.draw()
            self.cards[i].append(card)
            views = FaceUpCardViews.make(card, i, self.num_players)
            message_bundle.views.append(views)
        # Second card face up to all players
        for i in range(self.num_players):
            card = self.draw()
            self.cards[i].append(card)
            views = FaceUpCardView.make(card, i, self.num_players)
            message_bundle.views.append(views)
        # Second dealer card face down
        card = self.draw()
        self.cards[-1].append(card)
        views = FacedownCardViews.make(card, -1, self.num_players)
        message_bundle.views.append(views)
        # Return the message bundle, without a choice
        result = yield message_bundle
        assert result == -1, "Should not have a result"
        return result

    def turn(self, player: int) -> GameGenerator:
        """A single player has the option to take hits until bust or stand"""
        assert self.is_valid_player(player), f"{player}"
        # Players can get hits until they bust
        choice = StandHitChoice.make()
        result = -1
        while not self.is_busted(player):
            # Get the player's choice
            result = yield MessageBundle(choice=choice, player=player)
            assert choice.is_valid_option(result), f"{result}"
            if result == 0:  # Stand
                break
            # Hit, send views for the new card
            card = self.draw()
            self.cards[player].append(card)
            views = FaceUpCardView.make(card, player, self.num_players)
            result = yield MessageBundle(views=[views])
            assert result == -1, "Should not have a result"
        return result

    def dealer_turn(self) -> GameGenerator:
        """Dealer reveals card and hits until >= 17"""
        card = self.cards[-1][-1]  # Dealer face down card
        views = FaceUpCardViews.make(card, -1, self.num_players)
        result = yield MessageBundle(views=views)
        assert result == -1, "Should not have a result"
        while self.score(-1) < 17:
            card = self.draw()
            self.cards[-1].append(card)
            views = FaceUpCardView.make(card, -1, self.num_players)
            result = yield MessageBundle(views=[views])
            assert result == -1, "Should not have a result"
        return result

    def is_busted(self, player: int) -> bool:
        """Check if a player has busted"""
        return self.score(player) > 21

    def score(self, player: int) -> int:
        """Get the score of a player's hand"""
        cards = self.cards[player].copy()
        best_score = sum(cards)
        # Try switching aces to 11 to see if it's better
        while 1 in cards:
            cards.remove(1)
            cards.append(11)
            score = sum(cards)
            if score <= 21:
                best_score = score
        return best_score

    def show_winners(self) -> GameGenerator:
        """Show the winners"""
        # Get the winners
        winners = []
        # Get the best score
        best_score = 0
        for i in self.cards.keys():
            if not self.is_busted(i):
                best_score = max(self.score(i), best_score)
        # Get the players with that score (not incl. dealer)
        for i in range(self.num_players):
            if not self.is_busted(i) and self.score(i) == best_score:
                winners.append(i)
        # Send the views
        views = WinnersViews.make(winners, self.num_players)
        result = yield MessageBundle(views=views)
        assert result == -1, "Should not have a result"
        return result
