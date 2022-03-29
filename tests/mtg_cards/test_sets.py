#!/usr/bin/env python

import pytest

from mtg_cards.cards import Cards
from mtg_cards.sets import get_set


def test_set_is_cards():
    set_ = get_set("neo")
    assert isinstance(set_.cards, Cards)


def test_set_basics():
    set_ = get_set("neo")
    assert isinstance(set_.basics, Cards)
    names = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
    for card in set_.basics:
        assert card.name in names
