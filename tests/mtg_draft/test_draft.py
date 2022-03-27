#!/usr/bin/env python
import random
import logging

import pytest

from mtg_draft.draft import Draft



def test_deterministic():
    rng = random.Random(0)
    N = 8
    draft1 = Draft(N=N, set_name='neo', rng=random.Random(0))
    for pack in range(3):
        for pick in range(15):
            for player in range(N):
                draft1.pick(player, 0)
    draft2 = Draft(N=N, set_name='neo', rng=random.Random(0))
    for pack in range(3):
        for pick in range(15):
            for player in range(N):
                draft2.pick(player, 0)
    assert draft1.players == draft2.players
    draft3 = Draft(N=N, set_name='neo', rng=random.Random(1))
    for pack in range(3):
        for pick in range(15):
            for player in range(N):
                draft3.pick(player, 0)
    assert draft1.players != draft3.players