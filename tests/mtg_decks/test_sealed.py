#!/usr/bin/env python

import random

import pytest

from mtg_decks.sealed import Sealed


def test_sealed():
    for seed in range(10):
        rng = random.Random(seed)
        sealed = Sealed.make(set_name="neo", rng=rng)
        assert len(sealed.cards) == 90
