#!/usr/bin/env python
# %%
import json
import logging
import os
from types import MappingProxyType, NoneType
from urllib.parse import urlparse

import requests

from mtg_cards.card import Card, Cards

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

bulk_metadata = MappingProxyType({})
bulk_data = MappingProxyType({})
draft_cards = MappingProxyType({})


def proxy(data):
    """Get a read-only proxy for a mapping"""
    if isinstance(data, MappingProxyType):
        return data
    elif isinstance(data, dict):
        return MappingProxyType({k: proxy(v) for k, v in data.items()})
    elif isinstance(data, list):
        return tuple([proxy(item) for item in data])
    elif isinstance(data, (str, int, float, tuple, NoneType)):
        return data
    else:
        raise TypeError(f"Unsupported type: {type(data)}")


def unproxy(data):
    """Invert the proxy(), used to save data to JSON files"""
    if isinstance(data, MappingProxyType):
        return {k: unproxy(v) for k, v in data.items()}
    elif isinstance(data, (tuple, list)):
        return [unproxy(item) for item in data]
    elif isinstance(data, (str, int, float, NoneType)):
        return data
    else:
        raise TypeError(f"Unsupported type: {type(data)}")


def proxy_json_file(filename: str) -> MappingProxyType:
    """Get a read-only copy of a JSON file"""
    assert filename.endswith(".json"), f"Expected JSON file, got {filename}"
    with open(filename, "r") as f:
        return proxy(json.load(f))


def get_bulk_metadata() -> MappingProxyType:
    """Get the metadata for bulk data downloads from Scryfall"""
    # More info: https://scryfall.com/docs/api/bulk-data
    global bulk_metadata
    if not len(bulk_metadata):
        bulk_metdata_path = os.path.join(DATA_DIR, "bulk_metadata.json")
        url = "https://api.scryfall.com/bulk-data"
        try:
            r = requests.get(url)
            r.raise_for_status()
            metadata = {d["name"]: d for d in r.json()["data"]}
            if not os.path.exists(bulk_metdata_path):
                logging.debug("Caching bulk metadata from scryfall")
            with open(bulk_metdata_path, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logging.debug("Got exception downloading metadata:", e)
            logging.debug("loading from cached file")
            with open(bulk_metdata_path, "r") as f:
                metadata = json.load(f)
        bulk_metadata = MappingProxyType(metadata)
    return bulk_metadata


def get_bulk_data() -> MappingProxyType:
    """Get all bulk data from Scryfall"""
    global bulk_data
    if not len(bulk_data):
        for bulk_type in get_bulk_metadata():
            get_bulk_data_type(bulk_type)
    return bulk_data


def get_bulk_data_type(bulk_type: str) -> MappingProxyType:
    """Get Bulk Data from Scryfall"""
    global bulk_data
    # Check if we already have it loaded
    if bulk_type not in bulk_data:
        # If not load it
        metadata = get_bulk_metadata()
        bulk_obj = metadata[bulk_type]
        bulk_uri = bulk_obj["download_uri"]
        bulk_path = download_cache_file(bulk_uri)
        bulk_data_type = proxy_json_file(bulk_path)
        bulk_data = MappingProxyType(bulk_data | {bulk_type: bulk_data_type})
    return bulk_data[bulk_type]


def download_cache_file(uri: str) -> str:
    """Download or get a cached version of a file, return local path"""
    u = urlparse(uri)
    assert u.scheme == "https", f"Expected https uri, got {uri}"
    assert u.netloc.endswith("scryfall.com"), f"Expected scryfall.com, got {uri}"
    assert u.path.startswith("/file/"), f"Expected scryfall file, got {uri}"
    local_path = os.path.join(DATA_DIR, u.path[1:])  # remove leading /
    if not os.path.exists(local_path):
        # Download from scryfall
        logging.debug(f"Downloading {uri}")
        r = requests.get(uri)
        r.raise_for_status()
        # Make sure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # Save the file
        with open(local_path, "wb") as f:
            f.write(r.content)
        logging.debug(f"Saved {local_path}")
    return local_path


def get_draft_cards(set_name: str = "neo", cache=True) -> MappingProxyType:
    """Get all cards in a set, usually load from cached JSON file"""
    global draft_cards
    set_name = set_name.lower()
    if set_name not in draft_cards:
        cache_file = os.path.join(DATA_DIR, "draft_cache", f"{set_name}.jsonl")
        if cache and os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                cards = [json.loads(line) for line in f]
                cards = proxy(cards)
        else:
            default_cards = get_bulk_data_type("Default Cards")
            # Filter to cards in this set
            cards = filter(lambda c: c["set"] == set_name, default_cards)
            # Filter to just cards in draft boosters
            cards = filter(lambda c: c["booster"], cards)
            # Sort by 'collector_number'
            cards = sorted(cards, key=lambda c: int(c["collector_number"]))
            # Save cache file
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w") as f:
                for card in cards:
                    f.write(json.dumps(unproxy(card)) + "\n")
        # Convert cards to card type, and cards to a tuple (immutable)
        cards = tuple(Card.from_scryfall(card) for card in cards)
        draft_cards = MappingProxyType(draft_cards | {set_name: cards})
    # Ensure we got the set
    assert set_name in draft_cards, f"No cards found for {set_name}"
    # Ensure there are cards in the set
    assert len(draft_cards[set_name]), f"No cards found for {set_name}"
    # Ensure this is an immutable type
    assert isinstance(draft_cards[set_name], tuple), f"{type(draft_cards[set_name])}"
    # Return a mutable container
    return Cards(list(draft_cards[set_name]))


def get_card_image(card: MappingProxyType, fmt: str = "png") -> str:
    """Get the image for a card"""
    # Handle double-faced cards
    if "card_faces" in card:
        card = card["card_faces"][0]  # Just get the front image
    assert "image_uris" in card, f"{card.keys()}"
    assert fmt in card["image_uris"], f"{card['image_uris'].keys()}"
    image_uri = card["image_uris"][fmt]
    return download_cache_file(image_uri)


if __name__ == "__main__":
    print(get_draft_cards())  # Download data for draft cards
