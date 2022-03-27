#!/usr/bin/env python
# Using Scryfall bulk data, more info here:
# https://scryfall.com/docs/api/bulk-data
# %%

import glob
import json
import os
from types import MappingProxyType, NoneType
from urllib.parse import urlparse
import logging

import requests

DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../data'))

bulk_metadata = MappingProxyType({})
bulk_data = MappingProxyType({})


def proxy(data):
    ''' Get a read-only proxy for a mapping '''
    if isinstance(data, MappingProxyType):
        return data
    elif isinstance(data, dict):
        return MappingProxyType({k: proxy(v) for k, v in data.items()})
    elif isinstance(data, list):
        return tuple([proxy(item) for item in data])
    elif isinstance(data, (str, int, float, tuple, NoneType)):
        return data
    else:
        raise TypeError(f'Unsupported type: {type(data)}')


def proxy_json_file(filename: str) -> MappingProxyType:
    ''' Get a read-only copy of a JSON file '''
    assert filename.endswith('.json'), f'Expected JSON file, got {filename}'
    with open(filename, 'r') as f:
        return proxy(json.load(f))


def get_bulk_metadata() -> MappingProxyType:
    ''' Get the metadata for bulk data downloads from Scryfall '''
    global bulk_metadata
    if not len(bulk_metadata):
        bulk_metdata_path = os.path.join(DATA_DIR, 'bulk_metadata.json')
        url = 'https://api.scryfall.com/bulk-data'
        try:
            r = requests.get(url)
            r.raise_for_status()
            metadata = {d['name']: d for d in r.json()['data']}
            if not os.path.exists(bulk_metdata_path):
                logging.debug("Caching bulk metadata from scryfall")
            with open(bulk_metdata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logging.debug("Got exception downloading metadata:", e)
            logging.debug("loading from cached file")
            with open(bulk_metdata_path, 'r') as f:
                metadata = json.load(f)
        bulk_metadata = MappingProxyType(metadata)
    return bulk_metadata


def get_bulk_data() -> MappingProxyType:
    ''' Get all bulk data from Scryfall '''
    global bulk_data
    if not len(bulk_data):
        for bulk_type in get_bulk_metadata():
            get_bulk_data_type(bulk_type)
    return bulk_data


def get_bulk_data_type(bulk_type: str) -> MappingProxyType:
    ''' Get Bulk Data from Scryfall'''
    global bulk_data
    # Check if we already have it loaded
    if bulk_type not in bulk_data:
        # If not load it
        metadata = get_bulk_metadata()
        bulk_obj = metadata[bulk_type]
        bulk_uri = bulk_obj['download_uri']
        bulk_path = download_cache_file(bulk_uri)
        bulk_data_type = proxy_json_file(bulk_path)
        bulk_data = MappingProxyType(bulk_data | {bulk_type: bulk_data_type})
    return bulk_data[bulk_type]


def download_cache_file(uri: str) -> str:
    ''' Download or get a cached version of a file, return local path'''
    u = urlparse(uri)
    assert u.scheme == 'https', f'Expected https uri, got {uri}'
    assert u.netloc.endswith(
        'scryfall.com'), f'Expected scryfall.com, got {uri}'
    assert u.path.startswith('/file/'), f'Expected scryfall file, got {uri}'
    local_path = os.path.join(DATA_DIR, u.path[1:])  # remove leading /
    if not os.path.exists(local_path):
        # Download from scryfall
        logging.debug(f'Downloading {uri}')
        r = requests.get(uri)
        r.raise_for_status()
        # Make sure the directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # Save the file
        with open(local_path, 'wb') as f:
            f.write(r.content)
        logging.debug(f'Saved {local_path}')
    return local_path


def get_draft_cards(set_name: str = "neo") -> MappingProxyType:
    ''' Get all cards in a set '''
    set_name = set_name.lower()
    default_cards = get_bulk_data_type('Default Cards')
    # Filter to cards in this set
    cards = filter(lambda c: c['set'] == set_name, default_cards)
    # Filter to just cards in draft boosters
    cards = filter(lambda c: c['booster'], cards)
    # Sort by 'collector_number'
    cards = sorted(cards, key=lambda c: int(c['collector_number']))
    assert len(cards), f'No cards found for {set_name}'
    return cards


def get_card_image(card: MappingProxyType, fmt: str = 'png') -> str:
    ''' Get the image for a card '''
    # Handle double-faced cards
    if 'card_faces' in card:
        card = card['card_faces'][0]  # Just get the front image
    assert 'image_uris' in card, f'{card.keys()}'
    assert fmt in card['image_uris'], f"{card['image_uris'].keys()}"
    image_uri = card['image_uris'][fmt]
    return download_cache_file(image_uri)


if __name__ == '__main__':
    get_draft_cards()  # Download data for draft cards