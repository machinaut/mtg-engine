#!/usr/bin/env python
import random

import pytest
from mtg_cards.booster import BoosterBox
from mtg_cards.sets import get_set


def test_duplicates():
    """Test that the booster doesn't have duplicates of card objects."""
    box = BoosterBox(set_name="neo", rng=random.Random(0))
    ids = set()
    for _ in range(1000):
        for card in box.get_booster():
            ids.add(id(card))
    assert len(ids) == 302, "Duplicate cards objects in booster packs."


def test_determinism():
    """Test that the booster is deterministic."""

    for i in range(10):
        box1 = BoosterBox(set_name="neo", rng=random.Random(i))
        cards1 = box1.get_booster()
        box2 = BoosterBox(set_name="neo", rng=random.Random(i))
        cards2 = box2.get_booster()
        # Check we got the same cards in both packs
        assert cards1 == cards2, f"{cards1} != {cards2}"
        # Check that the cards are the same objects
        for a, b in zip(cards1, cards2):
            assert a is b


def test_different():
    """Test that the booster is different each time."""
    packs = []
    for i in range(1000):
        box = BoosterBox(set_name="neo", rng=random.Random(i))
        packs.append(box.get_booster())
    # Check that the packs are different
    for i in range(len(packs) - 1):
        assert packs[i] != packs[i + 1], f"{packs[i]} == {packs[i + 1]}"
    # Same but for a single box
    packs = []
    box = BoosterBox(set_name="neo", rng=random.Random(0))
    for _ in range(1000):
        packs.append(box.get_booster())
    # Check that the packs are different
    for i in range(len(packs) - 1):
        assert packs[i] != packs[i + 1], f"{packs[i]} == {packs[i + 1]}"


# TODO: Test that adding uniform slot probs for cards + basics results in obvious thing
def test_slot_math():
    set_ = get_set("neo")
