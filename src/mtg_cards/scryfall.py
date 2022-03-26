#!/usr/bin/env python

# %%
import requests
import os
import glob
import json

DATA_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../data'))

# Using Scryfall bulk data, more info here:
# https://scryfall.com/docs/api/bulk-data

# %%
def get_oracle_data(force_redownload: bool=False) -> dict:
    '''Get a dict of JSON data of Oracle Cards from Scryfall'''
    path = os.path.join(DATA_DIR, 'oracle-cards*.json')
    # check if we already have one
    files = glob.glob(path)
    if len(files) == 0 or force_redownload:
        download_oracle_data()
        files = glob.glob(path)
    assert len(files) == 1, f'Expected 1 file, got {files}'
    # Load file json
    with open(files[0], 'r') as f:
        data = json.load(f)
    return data

def download_oracle_data() -> str:
    ''' Download Oracle Cards data from Scryfall, delete old files if they exist'''
    # First download new data, then delete any old files
    url = 'https://api.scryfall.com/bulk-data'
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    oracle_data, = [d for d in data['data'] if d['name'] == 'Oracle Cards']
    oracle_uri = oracle_data['download_uri']
    oracle_name = os.path.basename(oracle_uri)
    path = os.path.join(DATA_DIR, oracle_name)
    # Download the file
    print(f'Downloading {oracle_uri}')
    r = requests.get(oracle_uri)
    r.raise_for_status()
    oracle = r.json()
    # Save the file
    with open(path, 'w') as f:
        json.dump(oracle, f)
    print(f'Saved {oracle_name}')
    # Delete other files
    files = glob.glob(os.path.join(DATA_DIR, 'oracle-cards*.json'))
    for f in files:
        if f != path:
            os.remove(f)
            print(f'Deleted {f}')
    # Return the path
    return path

def get_set_data(set: str="neo"):
    oracle_data = get_oracle_data()
    cards = filter(lambda c: c['set'] == set, oracle_data)
    return list(cards)

# # %%
# from collections import defaultdict
# set_data = get_set_data()
# rarities = defaultdict(int)
# for card in set_data:
#     rarities[card['rarity']] += 1
# print(rarities)

# %%
if __name__ == '__main__':
    download_oracle_data()