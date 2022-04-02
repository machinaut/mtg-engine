#!/usr/bin/env python
from random import Random

import pytest

from mtg_engine.decision_engine.player import FixedPlayer, RandomPlayer
from mtg_engine.mtg_draft.draft import DraftEngine


def test_draft():
    for num_players in range(2, 9):
        for seed in range(3):
            players = [RandomPlayer(rng=Random(i + 100)) for i in range(num_players)]
            draft = DraftEngine(players=players, rng=Random(seed))
            draft.run()


def fixed_draft(num_players=8, seed=0):
    rng = Random(seed)
    players = [FixedPlayer() for _ in range(num_players)]
    draft = DraftEngine(players=players, rng=rng)
    draft.run()
    return draft


def random_draft(num_players=8, draft_seed=0, pick_seed=0):
    rng = Random(draft_seed)
    players = [RandomPlayer(rng=Random(pick_seed + i)) for i in range(num_players)]
    draft = DraftEngine(players=players, rng=rng)
    draft.run()
    return draft


def test_deterministic():
    """Check that the draft is deterministic on seed given fixed choices"""
    for seed in range(3):
        draft1 = fixed_draft(seed=seed)
        draft2 = fixed_draft(seed=seed)
        for i in range(draft1.num_players):
            assert draft1.players[i].history == draft2.players[i].history
        assert draft1.players == draft2.players
        draft3 = fixed_draft(seed=seed + 1)
        assert draft1.players != draft3.players
        draft4 = random_draft(draft_seed=seed, pick_seed=seed + 2)
        draft5 = random_draft(draft_seed=seed, pick_seed=seed + 2)
        for i in range(draft4.num_players):
            assert draft4.players[i].history == draft5.players[i].history
        assert draft4.players == draft5.players


def test_conservative():
    """Check that all the cards in a draft are conserved"""
    for num_players in range(2, 9):
        for draft_seed in range(3):
            for pick_seed in range(3):
                draft = random_draft(
                    num_players=num_players, draft_seed=draft_seed, pick_seed=pick_seed
                )
                assert len(draft.picks) == num_players * 15 * 3


def test_packs_different():
    """Test that the packs in a draft are different from each other"""
    for num_players in range(2, 9):
        for seed in range(3):
            draft1 = random_draft(num_players=num_players, draft_seed=seed)
            draft2 = random_draft(num_players=num_players, draft_seed=seed)
            draft3 = random_draft(num_players=num_players, draft_seed=seed + 1)
            assert sorted(draft1.picks) == sorted(draft2.picks)
            assert sorted(draft1.picks) != sorted(draft3.picks)
