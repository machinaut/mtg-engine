#!/usr/bin/env python
"""
`mtg_cards.sets` MTG card set dataclasses

The SetCache is a singleton just used to handle caching to local files.
Sets are singleton objects, so they can be accessed by name.

Use get_set() to get a Set object for a set.
"""
# %%
import gzip
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict

from mtg_cards import CACHE_DIR
from mtg_cards.cards import Card, Cards
from mtg_cards.scryfall import get_bulk_data
from mtg_cards.util import proxy, unproxy


@dataclass
class Set:
    """Singleton class to hold information about a set"""

    set_name: str  # 3-letter lowercase code for the set (e.g. "neo")
    cards: Cards  # Cards found in draft boosters
    basics: Cards  # Basic lands found in this format (might have duplicates)

    @classmethod
    def make(cls, set_name: str = "neo", cache: bool = True) -> "Set":
        """
        Get a Set object containing all the cards found in draft boosters.

        set_name: str - the 3 letter (lowercase) code for the set (e.g. "neo")
        cache: bool - if true, load from a locally cached file, else pull from scryfall
            (if we pull from scryfall, write a new version of the cache file)
        """
        cache_file = os.path.join(CACHE_DIR, f"{set_name}.jsonl.gz")
        if not cache or not os.path.exists(cache_file):
            logging.debug("Creating cache file %s", cache_file)
            # Get the "Default Cards" bulk data from scryfall (probably cached)
            default_cards = get_bulk_data("default_cards")
            # Filter to cards in this set
            cards = filter(lambda c: c["set"] == set_name, default_cards)
            # Filter to just cards in draft boosters
            cards = filter(lambda c: c["booster"], cards)
            # Sort by 'collector_number'
            cards = sorted(cards, key=lambda c: int(c["collector_number"]))
            # Save cache file
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with gzip.open(cache_file, "wt", encoding="UTF-8") as file:
                file.write(json.dumps(unproxy(cards)) + "\n")
        # Load from the cache file, ensuring it's integrity
        logging.debug("Loading cache file %s", cache_file)
        with gzip.open(cache_file, "rt", encoding="UTF-8") as file:
            cards = Cards([Card.from_json(proxy(c)) for c in json.load(file)])
        # Create a Set object
        basics = cards.filt_basic()
        return cls(set_name, cards, basics)

    def render(self):
        """Render the cards in a set"""
        return self.cards.render(rowsize=30)


@dataclass
class SetCache:
    """Singleton class to hold all of the sets"""

    sets: Dict[str, Set] = field(default_factory=dict)

    def get_set(self, set_name: str = "neo", cache: bool = True) -> Set:
        """
        Get a Set object containing all the cards found in draft boosters.

        set_name: str - the 3 letter (lowercase) code for the set (e.g. "neo")
        cache: bool - if true, load from a locally cached file, else pull from scryfall
        """
        if set_name not in self.sets:
            self.sets[set_name] = Set.make(set_name=set_name, cache=cache)
        return self.sets[set_name]


set_cache = SetCache()

# Put some singleton methods in the module namespace
get_set = set_cache.get_set


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    get_set("neo").render()
