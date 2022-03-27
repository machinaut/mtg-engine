#!/usr/bin/env python
# Using Scryfall bulk data, more info here:
# https://scryfall.com/docs/api/bulk-data
# %%

import glob
import json
import os
from types import MappingProxyType, NoneType

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


def get_bulk_metadata(overwrite: bool = False) -> MappingProxyType:
    ''' Get the metadata for bulk data downloads from Scryfall '''
    global bulk_metadata
    if len(bulk_metadata) > 0 and not overwrite:
        return bulk_metadata
    url = 'https://api.scryfall.com/bulk-data'
    r = requests.get(url)
    r.raise_for_status()
    metadata = {d['name']: d for d in r.json()['data']}
    bulk_metadata = proxy(metadata)
    return bulk_metadata


def get_bulk_data(bulk_type: str, overwrite: bool = False) -> MappingProxyType:
    ''' Get Bulk Data from Scryfall'''
    global bulk_data
    # Check if we already have it loaded
    if bulk_type in bulk_data and not overwrite:
        return bulk_data[bulk_type]
    # If not load it
    bulk = load_bulk_data(bulk_type, overwrite)
    # Add it to the global data
    bulk_data = MappingProxyType(bulk_data | {bulk_type: proxy(bulk)})
    return bulk_data[bulk_type]


def load_bulk_data(bulk_type: str, overwrite: bool = False) -> MappingProxyType:
    ''' Load a bulk data file from Scryfall, return a read-only proxy to the data '''
    # Check if we have a file downloaded
    filename = bulk_type.lower().replace(' ', '-')
    files = glob.glob(os.path.join(DATA_DIR, filename + '*.json'))
    if len(files) != 1 or overwrite:
        files = [download_bulk_data(bulk_type)]
    # Load the file
    assert len(files) == 1, f'Expected 1 file, got {len(files)}'
    print("Loading bulk data from", files[0])
    return proxy_json_file(files[0])


def download_bulk_data(bulk_type: str) -> str:
    ''' Download a bulk data file from Scryfall, return path to local file '''
    metadata = get_bulk_metadata()
    bulk_obj = metadata[bulk_type]
    bulk_uri = bulk_obj['download_uri']
    print(f'Downloading {bulk_uri}')
    r = requests.get(bulk_uri)
    r.raise_for_status()
    bulk = r.json()
    # Save the file
    bulk_name = os.path.basename(bulk_uri)
    bulk_path = os.path.join(DATA_DIR, bulk_name)
    with open(bulk_path, 'w') as f:
        json.dump(bulk, f)
    print(f'Saved {bulk_path}')
    # Check for other files, and delete them
    filename = bulk_type.lower().replace(' ', '-')
    files = glob.glob(os.path.join(DATA_DIR, filename + '*.json'))
    for f in files:
        if f != bulk_name:
            os.remove(f)
            print(f'Deleted {f}')
    return bulk_path


def get_all_bulk_data(overwrite: bool = False) -> MappingProxyType:
    ''' Get all bulk data from Scryfall '''
    global bulk_data
    # Check if we already have it loaded
    metadata = get_bulk_metadata()
    for name in metadata:
        if name not in bulk_data or overwrite:
            get_bulk_data(name, overwrite)
        assert name in bulk_data, f'{name} not in bulk_data; {bulk_data.keys()}'
    assert len(bulk_data) == len(
        metadata), f'Expected {len(metadata)} data, got {len(bulk_data)}'
    return bulk_data


def get_draft_cards(set_name: str = "neo") -> MappingProxyType:
    ''' Get all cards in a set '''
    set_name = set_name.lower()
    default_cards = get_bulk_data('Default Cards')
    # Filter to cards in this set
    cards = filter(lambda c: c['set'] == set_name, default_cards)
    # Filter to just cards in draft boosters
    cards = filter(lambda c: c['booster'], cards)
    # Sort by 'collector_number'
    cards = sorted(cards, key=lambda c: int(c['collector_number']))
    assert len(cards), f'No cards found for {set_name}'
    return cards


# %%

if __name__ == '__main__':
    get_all_bulk_data()
