#!/usr/bin/env python
import random

import pytest

from mtg_cards import booster


def test_duplicates():
    """Test that the booster doesn't have duplicates of card objects."""
    rng = random.Random(0)
    ids = set()
    for _ in range(1000):
        for card in booster.get_booster(set_name="neo", rng=rng):
            ids.add(id(card))
    assert len(ids) == 302, "Duplicate cards objects in booster packs."


def test_determinism():
    """Test that the booster is deterministic."""
    for i in range(10):
        rng = random.Random(i)
        cards1 = booster.get_booster(set_name="neo", rng=rng)
        rng = random.Random(i)
        cards2 = booster.get_booster(set_name="neo", rng=rng)
        # Check we got the same cards in both packs
        assert cards1 == cards2, f"{cards1} != {cards2}"
        # Check that the cards are the same objects
        for a, b in zip(cards1, cards2):
            assert a is b


def test_different():
    """Test that the booster is different each time."""
    packs = []
    for i in range(1000):
        rng = random.Random(i)
        packs.append(booster.get_booster(set_name="neo", rng=rng))
    # Check that the packs are different
    for i in range(len(packs) - 1):
        assert packs[i] != packs[i + 1], f"{packs[i]} == {packs[i + 1]}"
