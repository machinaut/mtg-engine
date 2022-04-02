#!/usr/bin/env python

from random import Random

from mtg_engine.decision_engine.example_blackjack import Blackjack
from mtg_engine.decision_engine.player import RandomPlayer


def test_blackjack():
    for num_players in range(1, 5):
        for i in range(10):
            players = [RandomPlayer(rng=Random(i + 100)) for i in range(num_players)]
            engine_rng = Random(0)
            engine = Blackjack(players=players, rng=engine_rng)
            engine.run()
