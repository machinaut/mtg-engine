#!/usr/bin/env python

import random

import pytest

from mtg_decks.decks import RandomDeckAgent
from mtg_decks.sealed import Sealed


def test_pick_all():
    rng = random.Random(0)
    deck = Sealed.make("neo", rng=rng)
    assert len(deck.pool) == 90
    assert len(deck.main) == 0
    for _ in range(90):
        pool_before = len(deck.pool)
        main_before = len(deck.main)
        deck.pick(deck.pool[0])
        pool_after = len(deck.pool)
        main_after = len(deck.main)
        assert pool_before - 1 == pool_after
        assert main_before + 1 == main_after
    assert len(deck.pool) == 0
    for _ in range(len(deck.main)):
        deck.unpick(deck.main[0])
    assert len(deck.main) == 0


def test_random_agent_determinism():
    deck1 = Sealed.make("neo", rng=random.Random(0))
    deck2 = Sealed.make("neo", rng=random.Random(0))
    deck3 = Sealed.make("neo", rng=random.Random(0))
    assert deck1 == deck2
    assert deck1 == deck3
    rng1 = random.Random(0)
    agent1 = RandomDeckAgent(deck1, rng=rng1)
    rng2 = random.Random(0)
    agent2 = RandomDeckAgent(deck2, rng=rng2)
    agent1.run()
    agent2.run()
    assert agent1.deck == agent2.deck
    rng3 = random.Random(1)
    agent3 = RandomDeckAgent(deck3, rng=rng3)
    agent3.run()
    assert agent1.deck != agent3.deck
