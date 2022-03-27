#!/usr/bin/env python
import random

import pytest
from mtg_cards import booster


def test_duplicates():
    """Test that the booster doesn't have duplicates of card objects. """
    rng = random.Random(0)
    ids = set()
    for _ in range(1000):
        for card in booster.get_booster(set_name='neo', rng=rng):
            ids.add(id(card))
    assert len(ids) == 302, 'Duplicate cards objects in booster packs.'
