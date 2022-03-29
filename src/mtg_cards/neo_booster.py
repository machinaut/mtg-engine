#!/usr/bin/env python
"""
neo_booster - Generate a list of cards for a booster pack for the NEO set

This should only be called by the booster singleton cache.

NEO Draft Boosters Contain:
1 Rare or mythic rare card (mythic rare at 1 in 7.4, approximately)
1 Double-faced common or uncommon card
3 Uncommon cards
8 Common cards
1 Maybe foil (in 33% of Kamigawa: Neon Dynasty packs,
    a traditional foil, single or double-sided, of any rarity replaces a common.)
1 Land card (ukiyo-e land, common dual land, or basic land)

https://magic.wizards.com/en/articles/archive/feature/kamigawa-neon-dynasty-product-overview-2022-01-27
"""
import numpy as np

from mtg_cards.booster_probs import BoosterProbs, SlotProb
from mtg_cards.sets import get_set


def rare_slot_probs() -> SlotProb:
    """Get the probabilities for the rare/mythic slot"""
    cards = get_set("neo").cards
    # List the cards first
    rares = cards.filt_rare()
    mythics = cards.filt_mythic()
    rares_and_mythics = rares + mythics
    # Get the probabilities, and start by approx 1/7.4 for mythics
    mythic_prob = 1 / 7.4 / len(mythics)
    rare_prob = (7.4 - 1) / 7.4 / len(rares)
    probs = [rare_prob] * len(rares) + [mythic_prob] * len(mythics)
    assert len(probs) == len(rares_and_mythics)
    assert (
        7 < (1 / (mythic_prob * len(mythics))) < 8
    ), f"P: {mythic_prob * len(mythics)}"
    return SlotProb.from_cards_probs(rares_and_mythics, probs).normalize()


def dfc_slot_probs() -> SlotProb:
    """Get the probabilities for the double-faced card slot"""
    cards = get_set("neo").cards
    common_uncommon = cards.filt_common() + cards.filt_uncommon()
    dfc = common_uncommon.filt_dfc()
    return SlotProb.from_cards_probs(dfc, np.ones(len(dfc))).normalize()


def uncommon_slot_probs() -> SlotProb:
    """Get the probabilities of the single-faced uncommon slots"""
    cards = get_set("neo").cards
    uncommon_single_faced = cards.filt_not_dfc().filt_uncommon()
    probs = np.ones(len(uncommon_single_faced)) / len(uncommon_single_faced)
    return SlotProb.from_cards_probs(uncommon_single_faced, probs).normalize()


def common_slot_probs() -> SlotProb:
    """Get the probabilities of the single-faced common slots"""
    cards = get_set("neo").cards
    common_single_faced = cards.filt_not_dfc().filt_common().filt_not_land()
    probs = np.ones(len(common_single_faced)) / len(common_single_faced)
    return SlotProb.from_cards_probs(common_single_faced, probs).normalize()


def maybe_foil_slot() -> SlotProb:
    """Get the probabilities of the maybe foil slot"""
    foils = get_set("neo").cards
    common = foils.filt_not_dfc().filt_common().filt_not_land()
    foil_prob = 1 / 3 / len(foils)
    common_prob = 2 / 3 / len(common)
    foil_probs = SlotProb.from_cards_probs(foils, [foil_prob] * len(foils))
    common_probs = SlotProb.from_cards_probs(common, [common_prob] * len(common))
    return (foil_probs + common_probs).normalize()


def land_slot_probs() -> SlotProb:
    """Get the probabilities of the land slot"""
    cards = get_set("neo").cards
    lands = cards.filt_land().filt_common()
    return SlotProb.from_cards_probs(lands, np.ones(len(lands))).normalize()


def get_booster_probs() -> BoosterProbs:
    """Get a list of probabilities of cards for each slot in the booster"""
    booster_probs = BoosterProbs(set_name="neo")
    # Rares and Mythic slot
    booster_probs.probs.append(rare_slot_probs())
    # Double-faced common or uncommon
    booster_probs.probs.append(dfc_slot_probs())
    # Uncommon Single Faced
    booster_probs.probs += [uncommon_slot_probs()] * 3
    # Common Single Faced
    booster_probs.probs += [common_slot_probs()] * 8
    # Maybe foil
    booster_probs.probs.append(maybe_foil_slot())
    # Land
    booster_probs.probs.append(land_slot_probs())
    # Sort all of the slots
    booster_probs.sort()
    # Done
    return booster_probs
