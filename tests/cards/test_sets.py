#!/usr/bin/env python

import pytest

from mtg_engine.mtg_cards.cards import Cards
from mtg_engine.mtg_cards.sets import get_basics, get_set


def test_set_is_cards():
    set_ = get_set("neo")
    assert isinstance(set_.cards, Cards)


def test_set_basics():
    basics = get_basics("neo")
    assert isinstance(basics, Cards)
    names = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
    for card in basics:
        assert card.name in names
    assert len(set(c.name for c in basics)) == len(names)
    assert len(basics.unique()) == len(names)
