#!/usr/bin/env python
"""
Deck building engine, based on decision engine
"""


import logging
from dataclasses import dataclass, field
from random import Random
from typing import List, Optional

from mtg_engine.decision_engine.engine import Engine, MessageGen
from mtg_engine.decision_engine.message import Choice, Option, View, Views
from mtg_engine.decision_engine.player import BiasedPlayer, Player
from mtg_engine.mtg_cards.cards import Card, Cards
from mtg_engine.mtg_decks.decks import Deck
from mtg_engine.mtg_decks.sealed import Sealed


@dataclass
class DeckView(View):
    """All of the cards in the starting deck configuration"""

    desc: str = "Starting Deck Configuration"
    # Implicitly, the pool is the combination of the side and main
    main: Cards = field(default_factory=Cards)
    sideboard: Cards = field(default_factory=Cards)

    @classmethod
    def make(cls, deck: Deck) -> "DeckView":
        """Create a view of a deck"""
        return cls(main=deck.main, sideboard=deck.sideboard)


@dataclass
class DeckViews(Views):
    """A single view of each player's deck"""

    @classmethod
    def make(cls, deck: Deck) -> "DeckViews":
        """Create a set of views for each player"""
        return cls([DeckView.make(deck)])


@dataclass
class DeckPickOption(Option):
    """An option to pick a card from side to main"""

    card: Optional[Card] = None

    def __post_init__(self):
        self.desc = f"Pick {self.card}"


@dataclass
class DeckUnpickOption(Option):
    """An option to unpick (remove) a card from main to side"""

    card: Optional[Card] = None

    def __post_init__(self):
        self.desc = f"Unpick {self.card}"


@dataclass
class DeckFinishOption(Option):
    """An option to finish picking"""

    desc: str = "Finish picking"


@dataclass
class DeckChoice(Choice):
    """Which card to pick"""

    player: int = 0
    desc: str = "Pick a card from the pack"

    @classmethod
    def make(cls, deck: Deck) -> "DeckChoice":
        """Create a choice from a deck"""
        options: List[Option] = []
        if deck.legal():
            options.append(DeckFinishOption())
        for card in deck.sideboard:
            options.append(DeckPickOption(card=card))
        for card in deck.basics:
            options.append(DeckPickOption(card=card))
        for card in deck.main:
            options.append(DeckUnpickOption(card=card))
        return cls(options=options)


@dataclass
class DeckEngine(Engine):
    """Engine for building a limited deck"""

    deck: Deck = field(default_factory=Deck)
    max_turns: int = 1000

    def play(self) -> MessageGen:  # pylint: disable=useless-return
        """Callers should use Engine.run(), see Engine for details"""
        assert self.num_players == 1, f"{self.num_players}"
        # Send the initial view
        yield DeckViews.make(self.deck)
        # Send choices until we get a finish decision
        for _ in range(self.max_turns):
            # Get a decision, break if they took a finish decision
            choice = DeckChoice.make(self.deck)
            decision = yield choice
            assert decision is not None
            assert choice.is_valid_decision(decision)
            if isinstance(decision.option, DeckFinishOption):
                break
            if isinstance(decision.option, DeckPickOption):
                self.deck.pick(decision.option.card)
            elif isinstance(decision.option, DeckUnpickOption):
                self.deck.unpick(decision.option.card)
            else:
                raise ValueError(f"Unknown option: {decision.option}")
        else:
            raise RuntimeError("Deck building took too long")
        return None  # not actually useless, needed for generator type


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    my_deck = Sealed.make(set_name="neo", rng=Random(0))
    players: List[Player] = [BiasedPlayer(rng=Random(0))]
    deck_engine = DeckEngine(players=players, deck=my_deck)
    deck_engine.run()
    print("deck main:", len(my_deck.main), "side:", len(my_deck.sideboard))
    assert my_deck.legal()
