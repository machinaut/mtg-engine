#!/usr/bin/env python

import random

import pytest

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
