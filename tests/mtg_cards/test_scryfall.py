#!/usr/bin/env python
import pytest

from mtg_cards import scryfall


def test_get_draft_cards():
    cards = scryfall.get_draft_cards(set_name="neo", cache=False)
    assert len(cards) == 302
    # Check cards are the same objects if we call it twice
    cards2 = scryfall.get_draft_cards(set_name="neo")
    for a, b in zip(cards, cards2):
        assert a is b
