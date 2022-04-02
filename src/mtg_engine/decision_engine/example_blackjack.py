#!/usr/bin/env python
"""
Example using the decision engine to make blackjack.

https://bicyclecards.com/how-to-play/blackjack/

Simplified to only be a single hand, with no betting.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from random import Random
from typing import Dict, List

from mtg_engine.decision_engine.engine import Engine, MessageGen
from mtg_engine.decision_engine.message import Choice, Option, View, Views
from mtg_engine.decision_engine.player import HumanPlayer, Player

# Ignore suits, just using integer card values, where J/Q/K=10, A=1
CARDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


@dataclass
class FaceUpCardView(View):
    """A face_up card that everyone can see"""

    desc: str = "Face up card"
    value: int = -1000  # Card value 1 = A, 2-9, 10 = J/Q/K
    player: int = -1000  # Player index, -1 for dealer


@dataclass
class FaceUpCardViews(Views):
    """A set of views for each player for a face-up card"""

    @classmethod
    def make(cls, value: int, player: int, num_players: int) -> "FaceUpCardViews":
        """Create a set of views for each player"""
        view = FaceUpCardView(value=value, player=player)
        return cls([view] * num_players)


@dataclass
class MyFacedownCard(View):
    """A face_down card that only the player can see"""

    desc: str = "My face-down card"
    value: int = -1000  # Card value 1 = A, 2-9, 10 = J/Q/K


@dataclass
class OtherFaceDownCard(View):
    """A face_down card that this player cannot see"""

    desc: str = "Face-down card"
    player: int = -1000  # Player index, -1 for dealer


@dataclass
class FacedownCardViews(Views):
    """A set of views for each player for a face-down card"""

    @classmethod
    def make(cls, value: int, player: int, num_players: int) -> "FacedownCardViews":
        """Create a set of views for each player"""
        views = cls()
        for i in range(num_players):
            if i == player:
                views.append(MyFacedownCard(value=value))
            else:
                views.append(OtherFaceDownCard(player=i))
        return views


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
    def make(cls, player: int) -> "StandHitChoice":
        """Create a choice to stand or hit"""
        return cls(player=player, options=[StandOption(), HitOption()])


@dataclass
class ScoresView(View):
    """A view of the scores at the end of the game"""

    desc: str = "Ending Scores"
    player_scores: List[int] = field(default_factory=list)
    dealer_score: int = -1000


@dataclass
class ScoresViews(Views):
    """A set of views for each player for the scores at the end of the game"""

    @classmethod
    def make(cls, player_scores: List[int], dealer_score) -> "ScoresViews":
        """Create a set of views for each player"""
        view = ScoresView(player_scores=player_scores, dealer_score=dealer_score)
        return cls([view] * len(player_scores))


@dataclass
class Blackjack(Engine):
    """Simplified 1-player blackjack game"""

    rng: Random = field(default_factory=Random, repr=False)
    # map from player -> cards
    cards: Dict[int, List[int]] = field(default_factory=lambda: defaultdict(list))

    def draw(self) -> int:
        """Get a random card value"""
        return self.rng.choice(CARDS)

    def play(self) -> MessageGen:
        """Callers should use Engine.run(), see Engine for details"""
        # Setup the game
        result = yield from self.deal()
        # Each player gets a turn
        for i in range(self.num_players):
            result = yield from self.turn(i)
        # Dealer gets a turn
        result = yield from self.dealer_turn()
        # Show the scores
        result = yield from self.show_scores()
        return result

    def deal(self) -> MessageGen:
        """Deal everyone starting cards"""
        # First card face up
        # Deal to all the players, then dealer
        for i in list(range(self.num_players)) + [-1]:
            card = self.draw()
            self.cards[i].append(card)
            result = yield FaceUpCardViews.make(card, i, self.num_players)
        # Second card face up to all players, not dealer
        for i in range(self.num_players):
            card = self.draw()
            self.cards[i].append(card)
            result = yield FaceUpCardViews.make(card, i, self.num_players)
        # Second dealer card face down
        card = self.draw()
        self.cards[-1].append(card)
        result = yield FacedownCardViews.make(card, -1, self.num_players)
        return result

    def turn(self, player: int) -> MessageGen:
        """A single player has the option to take hits until bust or stand"""
        assert self.is_valid_player(player), f"{player}"
        # Players can get hits until they bust
        choice = StandHitChoice.make(player=player)
        result = None
        while not self.is_busted(player):
            # Get the player's choice
            result = yield choice
            assert result is not None, f"{result}"
            assert choice.is_valid_decision(result), f"{result}"
            if result.option == 0:  # Stand
                break
            # Hit, send views for the new card
            card = self.draw()
            self.cards[player].append(card)
            result = yield FaceUpCardViews.make(card, player, self.num_players)
        return result

    def dealer_turn(self) -> MessageGen:
        """Dealer reveals card and hits until >= 17"""
        card = self.cards[-1][-1]  # Dealer face down card
        result = yield FaceUpCardViews.make(card, -1, self.num_players)
        while self.score(-1) < 17:
            card = self.draw()
            self.cards[-1].append(card)
            result = yield FaceUpCardViews.make(card, -1, self.num_players)
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

    def show_scores(self) -> MessageGen:
        """Show the scores"""
        players_scores = [self.score(i) for i in range(self.num_players)]
        dealers_score = self.score(-1)
        return (yield ScoresViews.make(players_scores, dealers_score))


if __name__ == "__main__":
    # Run the game
    logging.basicConfig(level=logging.DEBUG)
    rng = Random(0)
    players: List[Player] = [HumanPlayer()]
    engine = Blackjack(players=players, rng=rng)
    engine.run()
