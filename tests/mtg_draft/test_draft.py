#!/usr/bin/env python
import random
import logging

import pytest

from mtg_draft.draft import Draft


def fixed_draft(N=8, seed=0):
    draft = Draft(N=N, set_name='neo', rng=random.Random(seed))
    for pack in range(3):
        for pick in range(15):
            for player in range(N):
                draft.pick(player, 0)
    return draft


def random_draft(N=8, draft_seed=0, pick_seed=0):
    rng = random.Random(pick_seed)  # used for picks
    draft = Draft(N=N, set_name='neo', rng=random.Random(draft_seed))
    for pack in range(3):
        for pick in range(15):
            for player in range(N):
                draft.pick(player, rng.randint(0, 15 - pick - 1))
    return draft


def test_deterministic():
    ''' Check that the draft is deterministic on seed given fixed choices '''
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
    ''' Check that all the cards in a draft are conserved '''
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

