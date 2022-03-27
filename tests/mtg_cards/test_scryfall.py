#!/usr/bin/env python
import pytest

from mtg_cards import scryfall


def test_get_draft_cards():
    cards = scryfall.get_draft_cards(set_name='neo')
    assert len(cards) == 302
    # Check cards are the same objects
    for a, b in zip(cards, scryfall.get_draft_cards(set_name='neo')):
        assert a is b