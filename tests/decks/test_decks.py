#!/usr/bin/env python

from random import Random
from telnetlib import SE

import pytest

from mtg_engine.decision_engine.player import BiasedPlayer, FixedPlayer, Player
from mtg_engine.mtg_decks.build import DeckEngine
from mtg_engine.mtg_decks.decks import Deck
from mtg_engine.mtg_decks.sealed import Sealed


def build_deck(deck: Deck, player: Player):
    assert isinstance(deck, Deck)
    assert isinstance(player, Player)
    deck_engine = DeckEngine(players=[player], deck=deck)
    deck_engine.run()
    assert deck.legal()
    assert deck_engine.deck is deck
    return deck


def build_random_deck(deck: Deck, seed: int):
    player = BiasedPlayer(rng=Random(seed))
    return build_deck(deck, player)


def build_fixed_deck(deck: Deck):
    player = FixedPlayer()
    return build_deck(deck, player)


def test_build_deck():
    deck1 = Sealed.make("neo", rng=Random(0))
    deck1 = build_random_deck(deck1, 0)
    deck2 = Sealed.make("neo", rng=Random(1))
    deck2 = build_fixed_deck(deck2)


def test_pick_all():
    rng = Random(0)
    deck = Sealed.make("neo", rng=rng)
    assert len(deck.pool) == 90
    assert len(deck.sideboard) == 90
    assert len(deck.main) == 0
    for _ in range(90):
        side_before = len(deck.sideboard)
        main_before = len(deck.main)
        deck.pick(deck.sideboard[0])
        side_after = len(deck.sideboard)
        main_after = len(deck.main)
        assert side_before - 1 == side_after
        assert main_before + 1 == main_after
    assert len(deck.sideboard) == 0
    for _ in range(len(deck.main)):
        deck.unpick(deck.main[0])
    assert len(deck.main) == 0


def test_random_agent_determinism():
    deck1 = Sealed.make("neo", rng=Random(0))
    deck2 = Sealed.make("neo", rng=Random(0))
    deck3 = Sealed.make("neo", rng=Random(0))
    assert deck1 == deck2
    assert deck1 == deck3
    deck1 = build_random_deck(deck1, 0)
    deck2 = build_random_deck(deck2, 0)
    assert deck1 == deck2
    deck3 = build_random_deck(deck3, 1)
    assert deck1 != deck3


def test_five_basics():
    deck = Sealed.make("neo", rng=Random(0))
    basic_names = sorted(set(c.name for c in deck.basics))
    assert len(basic_names) == 5
    correct_names = ["Forest", "Island", "Mountain", "Plains", "Swamp"]
    assert basic_names == correct_names
