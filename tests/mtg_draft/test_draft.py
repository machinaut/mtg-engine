#!/usr/bin/env python
import random

import pytest

from mtg_draft.draft import Draft, DraftRunner


def fixed_draft(num_players=8, seed=0):
    draft = Draft(num_players=num_players, set_name="neo", rng=random.Random(seed))
    for pack in range(3):
        for pick in range(15):
            for player in range(num_players):
                draft.pick(player, 0)
    for player in draft.players:
        assert len(player.cards) == 45
    return draft


def random_draft(num_players=8, draft_seed=0, pick_seed=0):
    rng = random.Random(pick_seed)  # used for picks
    draft = Draft(
        num_players=num_players, set_name="neo", rng=random.Random(draft_seed)
    )
    for pack in range(3):
        for pick in range(15):
            for player in range(num_players):
                draft.pick(player, rng.randint(0, 15 - pick - 1))
    for player in draft.players:
        assert len(player.cards) == 45
    return draft


def test_deterministic():
    """Check that the draft is deterministic on seed given fixed choices"""
    for seed in range(10):
        draft1 = fixed_draft(seed=seed)
        draft2 = fixed_draft(seed=seed)
        assert draft1.players == draft2.players
        draft3 = fixed_draft(seed=seed + 1)
        assert draft1.players != draft3.players
        draft4 = random_draft(draft_seed=seed, pick_seed=seed + 2)
        draft5 = random_draft(draft_seed=seed, pick_seed=seed + 2)
        assert draft4.players == draft5.players


def test_conservative():
    """Check that all the cards in a draft are conserved"""
    for draft_seed in range(10):
        drafts_cards = []  # list of lists of cards for a draft
        for pick_seed in range(10):
            draft = random_draft(draft_seed=draft_seed, pick_seed=pick_seed)
            draft_cards = []
            for player in draft.players:
                draft_cards.extend(player.cards)
            # sort by id(card)
            draft_cards = sorted(draft_cards, key=lambda x: id(x))
            drafts_cards.append(draft_cards)
        # Check that all the cards are the same
        for i in range(len(drafts_cards) - 1):
            assert drafts_cards[i] == drafts_cards[i + 1]


def test_packs_different():
    """Test that the packs in a draft are different from each other"""
    for num_players in range(2, 9):
        for seed in range(10):
            rng = random.Random(seed)
            draft = Draft(num_players=num_players, set_name="neo", rng=rng)
            packs = draft.boosters + [p.pack for p in draft.players]
            assert len(packs) == 3 * num_players
            for i, a in enumerate(packs):
                for b in packs[i + 1 :]:
                    assert a.copy() != b.copy()
                assert a == a.copy()


def test_runner():
    """Test running drafts with random agents"""
    for num_players in range(2, 9):
        for seed in range(10):
            rng = random.Random(seed)
            runner = DraftRunner.make(num_players=num_players, set_name="neo", rng=rng)
            runner.run()
