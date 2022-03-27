#!/usr/bin/env python
# %% # Sample random booster packs
import logging
import random
from types import MappingProxyType
from typing import Optional

import numpy as np

from mtg_cards.card import Cards
from mtg_cards.scryfall import get_draft_cards, proxy

# Use this to cache computing the booster probabilities
booster_probs = MappingProxyType({})


def get_booster_probs(set_name: str = "neo") -> tuple:
    ''' Get the probability for each card of each slot in a booster '''
    global booster_probs
    if set_name not in booster_probs:
        logging.info(f"Computing booster probs for {set_name}")
        if set_name == 'neo':
            slot_probs = get_slot_probs_neo()
        else:
            raise ValueError(f'Unknown set {set_name}')
        booster_probs = MappingProxyType(
            booster_probs | {set_name: proxy(slot_probs)})
    return booster_probs[set_name]


def get_slot_probs_neo() -> tuple:
    ''' Get a list of probabilities of cards for each slot
    https://magic.wizards.com/en/articles/archive/feature/kamigawa-neon-dynasty-product-overview-2022-01-27
    1 Rare or mythic rare card (mythic rare at 1 in 7.4, approximately)
    1 Double-faced common or uncommon card
    3 Uncommon cards
    8 Common cards
    1 Maybe foil (in 33% of Kamigawa: Neon Dynasty packs,
        a traditional foil, single or double-sided, of any rarity replaces a common.)
    1 Land card (ukiyo-e land, common dual land, or basic land)

    The return value is a MappingProxyType of card position to lists
        each list is a pair of (probability, card)
    '''
    slot_probs = []
    cards = get_draft_cards('neo')
    assert isinstance(cards, Cards), f'Expected Cards, got {type(cards)}'
    # Rares and Mythic slot
    # List the cards first
    rares = cards.filt_rare()
    mythics = cards.filt_mythic()
    rares_and_mythics = rares + mythics
    # Get the probabilities, and start by
    mythic_prob = 1 / 7.4 / len(mythics)
    rare_prob = (7.4 - 1) / 7.4 / len(rares)
    probs = [rare_prob] * len(rares) + [mythic_prob] * len(mythics)
    probs = np.array(probs) / np.sum(probs)
    assert len(probs) == len(rares_and_mythics)
    assert (1/8) < (mythic_prob * len(mythics)) < (1 /
                                                   7), f'P: {mythic_prob * len(mythics)}'
    slot_probs.append(list(zip(probs, rares_and_mythics)))
    # Double-faced common or uncommon
    common_uncommon = cards.filt_common() + cards.filt_uncommon()
    dfc_common_uncommon = common_uncommon.filt_dfc()
    probs = np.ones(len(dfc_common_uncommon)) / len(dfc_common_uncommon)
    slot_probs.append(list(zip(probs, dfc_common_uncommon)))
    # Uncommon Single Faced
    uncommon_single_faced = cards.filt_not_dfc().filt_uncommon()
    probs = np.ones(len(uncommon_single_faced)) / len(uncommon_single_faced)
    for i in range(3):
        slot_probs.append(list(zip(probs, uncommon_single_faced)))
    # Common Single Faced
    common_single_faced = cards.filt_not_dfc().filt_common().filt_not_land()
    probs = np.ones(len(common_single_faced)) / len(common_single_faced)
    for i in range(8):
        slot_probs.append(list(zip(probs, common_single_faced)))
    # Maybe foil
    maybe_foil = cards + common_single_faced
    foil_prob = 1 / 3 / len(cards)
    common_prob = 2 / 3 / len(common_single_faced)
    probs = [foil_prob] * len(cards) + [common_prob] * len(common_single_faced)
    probs = np.array(probs) / np.sum(probs)
    assert len(probs) == len(maybe_foil), f'{len(probs)} {len(maybe_foil)}'
    # There's duplicates between the two lists, so we need to combine them
    combined_cards = []
    combined_probs = []
    for i, card in enumerate(maybe_foil):
        if card in combined_cards:
            continue
        combined_cards.append(card)
        total_prob = 0.0
        for j, prob in enumerate(probs):
            if maybe_foil[j] == card:
                total_prob += prob
        combined_probs.append(total_prob)
    assert len(combined_cards) == len(combined_probs)
    combined_probs = np.array(combined_probs) / np.sum(combined_probs)
    slot_probs.append(list(zip(combined_probs, combined_cards)))
    # Land
    common_lands = cards.filt_land().filt_common()
    probs = np.ones(len(common_lands)) / len(common_lands)
    slot_probs.append(list(zip(probs, common_lands)))
    # Sort them by card name for easier debugging
    for sp in slot_probs:
        # check that probabilities sum to 1
        probs = [p for p, c in sp]
        assert np.isclose(np.sum(probs), 1.0), f'{np.sum(probs)}'
        sp.sort(key=lambda x: x[1].name)
    # Check we got all 15 slots
    assert len(slot_probs) == 15, f'{len(slot_probs)}'
    return proxy(slot_probs)


def get_booster(set_name: str = "neo", rng: Optional[random.Random] = None) -> list:
    ''' Get a booster of cards '''
    slot_probs = get_booster_probs(set_name)
    if rng is None:
        rng = random
    # Pick the cards
    pack = []
    for sp in slot_probs:
        probs, cards = zip(*sp)
        choice, = rng.choices(cards, probs, k=1)
        pack.append(choice)
    return pack


if __name__ == '__main__':
    for card in get_booster():
        print(card)
