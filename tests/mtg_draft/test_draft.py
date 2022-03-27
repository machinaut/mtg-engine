#!/usr/bin/env python
import random
import logging

import pytest

from mtg_draft.draft import Draft



def test_deterministic():
    rng = random.Random(0)
    players = 8
    draft1 = Draft(players=players, set_name='neo', rng=rng)
    for pack in range(3):
        for pick in range(15):
            for player in range(players):
                print('pack', pack, 'pick', pick, 'player', player)
                draft1.pick(player, 0)
    draft2 = Draft(players=players, set_name='neo', rng=rng)
    for pack in range(3):
        for pick in range(15):
            for player in range(players):
                print('pack', pack, 'pick', pick, 'player', player)
                draft2.pick(player, 0)
    assert draft1.cards == draft2.cards