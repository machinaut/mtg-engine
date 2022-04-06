#!/usr/bin/env python
"""
Drafting, based on the Decision Engine.
"""
import logging
from dataclasses import dataclass, field
from random import Random
from typing import List

from mtg_engine.decision_engine.engine import Engine, MessageGen
from mtg_engine.decision_engine.message import Choice, Option, View, Views
from mtg_engine.decision_engine.player import BiasedPlayer, HumanPlayer, Player
from mtg_engine.mtg_cards.cards import Card, Cards
from mtg_engine.mtg_cards.sets import get_basics
from mtg_engine.mtg_decks.decks import Deck, LimitedDeck

# from mtg_engine.mtg_game.objects import CardObject
from mtg_engine.mtg_game.zones import Zones


@dataclass
class StartFirstView(View):
    """Which player goes first"""

    desc: str = "Which player goes first, and who chose it"

    chooser: int = -1000
    player: int = -1000


@dataclass
class StartFirstViews(Views):
    """A set of views of which player goes first"""

    @classmethod
    def make(cls, chooser: int, player: int, num_players: int) -> "StartFirstViews":
        """Create a set of views for each player"""
        return cls(
            [StartFirstView(chooser=chooser, player=player) for _ in range(num_players)]
        )


@dataclass
class StartFirstOption(Option):
    """An option to choose the player to go first"""

    desc: str = "Which Player Starts"
    player: int = -1000


@dataclass
class StartFirstChoice(Choice):
    """Who goes first"""

    desc: str = "Choose which player goes first"

    @classmethod
    def make(cls, player: int, num_players: int) -> "StartFirstChoice":
        """Create a new StartFirstChoice"""
        options: List[Option] = [StartFirstOption(player=i) for i in range(num_players)]
        return cls(player=player, options=options)


@dataclass
class LibraryView(View):
    """The cards in this player's library"""

    desc: str = "Player's Library"
    cards: Cards = field(default_factory=Cards)


@dataclass
class LibrarySizeView(View):
    """The number of cards in another player's library"""

    desc: str = "Player's Library Size"
    player: int = -1000
    size: int = -1000


@dataclass
class LibraryViews(Views):
    """A set of views of the number of cards in each player's library"""

    @classmethod
    def make(cls, player: int, cards: Cards, num_players: int) -> "LibraryViews":
        """Create a set of views for each player"""
        views: List[View] = []
        for i in range(num_players):
            if i == player:
                views.append(LibraryView(cards=cards))
            else:
                views.append(LibrarySizeView(player=player, size=len(cards)))
        return cls(views)


@dataclass
class StartingHandView(View):
    """The cards in this player's starting hand"""

    desc: str = "Player's Starting Hand"
    cards: Cards = field(default_factory=Cards)


@dataclass
class StartingHandSizeView(View):
    """The number of cards in another player's starting hand"""

    desc: str = "Player's Starting Hand Size"
    player: int = -1000
    size: int = -1000


@dataclass
class StartingHandViews(Views):
    """A set of views of the number of cards in each player's starting hand"""

    @classmethod
    def make(cls, player: int, cards: Cards, num_players: int) -> "StartingHandViews":
        """Create a set of views for each player"""
        views: List[View] = []
        for i in range(num_players):
            if i == player:
                views.append(StartingHandView(cards=cards))
            else:
                views.append(StartingHandSizeView(player=player, size=len(cards)))
        return cls(views)


@dataclass
class StartingHandKeepOption(Option):
    """An option to keep a card"""

    desc: str = "Keep this starting hand"


@dataclass
class StartingHandMulliganOption(Option):
    """An option to mulligan"""

    desc: str = "Mulligan this starting hand"


@dataclass
class StartingHandChoice(Choice):
    """Which card to keep or mulligan"""

    desc: str = "Choose a card to keep or mulligan"

    @classmethod
    def make(cls, player: int) -> "StartingHandChoice":
        """Create a new StartingHandChoice"""
        return cls(
            player=player,
            options=[
                StartingHandKeepOption(),
                StartingHandMulliganOption(),
            ],
        )


@dataclass
class StartingHandKeepView(View):
    """Did a player keep their starting hand?"""

    desc: str = "Did player keep their starting hand?"
    player: int = -1000
    keep: bool = False


@dataclass
class StartingHandKeepViews(Views):
    """A set of views of whether each player kept their starting hand"""

    @classmethod
    def make(cls, player: int, keep: bool, num_players: int) -> "StartingHandKeepViews":
        """Create a set of views for each player"""
        return cls(
            views=[
                StartingHandKeepView(player=player, keep=keep)
                for _ in range(num_players)
            ]
        )


@dataclass
class MulliganCardOption(Option):
    """An option to mulligan a card"""

    desc: str = "Mulligan this card"
    card: Card = field(default_factory=lambda: Card.bogus())


@dataclass
class MulliganCardChoice(Choice):
    """Which card to mulligan"""

    desc: str = "Choose a card to mulligan"

    @classmethod
    def make(cls, player: int, cards: Cards) -> "MulliganCardChoice":
        """Create a new MulliganCardChoice"""
        return cls(
            player=player, options=[MulliganCardOption(card=card) for card in cards]
        )


@dataclass
class GameEngine(Engine):
    """Magic: the Gathering
    https://magic.wizards.com/en/formats/booster-draft
    """

    decks: List[Deck] = field(default_factory=list)
    rng: Random = field(default_factory=Random, repr=False)
    current_player: int = -1
    zones: Zones = field(default_factory=Zones)
    lifes: List[int] = field(default_factory=list)

    def play(self) -> MessageGen:  # pylint: disable=useless-return
        """Callers should use Engine.run(), see Engine for details"""
        assert self.num_players >= 2, f"{self.num_players}"
        assert len(self.decks) == 2, f"{len(self.decks)}"
        yield from self.start()
        return None  # not useless, needed for generator type

    def start(self) -> MessageGen:  # pylint: disable=useless-return
        """103. Starting the Game
        https://yawgatog.com/resources/magic-rules/#R103"""
        # The engine picks who chooses who goes first
        chooser = self.rng.choice(range(self.num_players))
        # Send that choice to the chooser
        choice = StartFirstChoice.make(player=chooser, num_players=self.num_players)
        decision = yield choice
        assert decision is not None and choice.is_valid_decision(decision)
        # Set the first player by setting the turn
        assert isinstance(decision.option, StartFirstOption)
        self.current_player = decision.option.player
        # Send the first view
        yield StartFirstViews.make(
            chooser=chooser,
            player=decision.option.player,
            num_players=self.num_players,
        )
        # Send all the library / size views
        for i in range(self.num_players):
            # Make a shuffled copy of the main deck, this is NOT the library
            yield LibraryViews.make(
                player=i,
                cards=self.decks[i].main.shuffled(rng=self.rng),
                num_players=self.num_players,
            )
        # Shuffle decks into libraries, make hands and graveyards (empty)
        self.zones.setup(decks=self.decks, rng=self.rng)
        # Set the life totals
        self.lifes = [20] * self.num_players  # TODO: this should emit a life total view
        # Draw starting hands
        yield from self.draw_hands()
        return None  # not useless, needed for generator type

    def draw_hands(self) -> MessageGen:  # pylint: disable=useless-return
        """Drawing hands and Mulliganing"""
        players_to_draw = list(range(self.num_players))
        # shift so that the current player is the first to draw
        players_to_draw = (
            players_to_draw[self.current_player :]
            + players_to_draw[: self.current_player]
        )
        assert players_to_draw[0] == self.current_player
        # Loop until no mulligans are taken, or until hand limit
        for cards_to_mulligan in range(7):
            # Go in player order
            for i in players_to_draw.copy():
                assert len(self.zones.hands[i]) == 0
                assert (
                    len(self.zones.libraries[i]) >= 40
                ), f"{len(self.zones.libraries[i])}"
                # Draw the hand
                cards = Cards([self.zones.draw(player=i) for _ in range(7)])
                assert (
                    len(self.zones.libraries[i]) >= 33
                ), f"{len(self.zones.libraries[i])}"
                # Send the hand view
                yield StartingHandViews.make(
                    player=i, cards=cards, num_players=self.num_players
                )
                # Get the cards to put at the bottom of the library
                for _ in range(cards_to_mulligan):
                    choice = MulliganCardChoice.make(player=i, cards=cards)
                    decision = yield choice
                    assert decision is not None and choice.is_valid_decision(decision)
                    # Remove the card from the hand
                    cards.remove(decision.option.card)
                    # Put the card back in the library
                    self.zones.hand_to_library_bottom(
                        player=i, card=decision.option.card
                    )
                # Send the keep / mulligan choice
                choice = StartingHandChoice.make(player=i)
                decision = yield choice
                assert decision is not None and choice.is_valid_decision(decision)
                # If the player mulligans, remove them from the list
                if isinstance(decision.option, StartingHandKeepOption):
                    players_to_draw.remove(i)
                else:
                    # Shuffle the hand into the library
                    self.zones.shuffle_hand_into_library(player=i)
                    assert len(self.zones.hands[i]) == 0, f"{len(self.zones.hands[i])}"
                    assert (
                        len(self.zones.libraries[i]) >= 40
                    ), f"{len(self.zones.libraries[i])}"
        return None  # not useless, needed for generator type


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    plains: Card = get_basics().cards[0]
    assert plains.name == "Plains", f"{plains}"
    deck = LimitedDeck(main=Cards([plains] * 40))
    assert deck.legal(), f"{deck}"
    decks: List[Deck] = [deck, deck]
    players: List[Player] = [HumanPlayer(), BiasedPlayer(rng=Random(0))]
    game_engine = GameEngine(players=players, decks=decks)
    game_engine.run()
