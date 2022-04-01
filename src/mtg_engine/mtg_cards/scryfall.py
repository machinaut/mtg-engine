#!/usr/bin/env python
"""
mtg_cards.scryfall - Scryfall data cache and utilities

Note that this does _not_ depend on the Card/Cards dataclasses,
in order to avoid a circular import loop between this file and it.

Callers should use the direct functions in this module,
and not access the singleton instance of the ScryfallCache directly.
"""

# %%
import gzip
import json
import logging
import os
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
from mtg_cards import DATA_DIR
from mtg_cards.util import proxy


def url_to_path(url: str) -> str:
    """Get the local path for a scryfall URL, if it were cached"""
    url_parsed = urlparse(url)
    assert url_parsed.scheme == "https", f"{url}"
    assert url_parsed.netloc.endswith("scryfall.com"), f"{url}"
    assert url_parsed.path.startswith("/"), f"{url}"
    return os.path.join(DATA_DIR, url_parsed.path[1:])  # remove leading /


def url_to_compressed_path(url: str) -> str:
    """Get the local path for a scryfall URL, if it were cached compressed"""
    return url_to_path(url) + ".gz"


def download_scryfall_file(url: str) -> str:
    """Download and cache a scryfall file, uncompressed"""
    path = url_to_path(url)
    # Download from scryfall
    logging.debug("Downloading %s to %s", url, path)
    request = requests.get(url)
    request.raise_for_status()
    # Make sure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Save the file
    with open(path, "wb") as file:
        file.write(request.content)
    return path


def cache_scryfall_file(url: str) -> str:
    """Cache a scryfall file, uncompressed"""
    path = url_to_path(url)
    if not os.path.exists(path):
        path = download_scryfall_file(url)
    return path


def download_scryfall_json(url: str) -> str:
    """Download and cache a JSON file from Scryfall, returning local path"""
    path = url_to_compressed_path(url)
    logging.debug("Compressing %s to %s", url, path)
    request = requests.get(url)
    request.raise_for_status()
    # Make sure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Save the file compressed
    with gzip.open(path, "wt", encoding="UTF-8") as file:
        json.dump(request.json(), file)
    return path


def get_scryfall_json(url: str) -> MappingProxyType:
    """Get a scryfall json url loaded as a MappingProxyType"""
    path = url_to_compressed_path(url)
    if not os.path.exists(path):
        path = download_scryfall_json(url)
    with gzip.open(path, "rt", encoding="UTF-8") as file:
        return proxy(json.load(file))


@dataclass
class ScryfallCache:
    """Singleton class for scryfall data cached locally (compressed)."""

    bulk_metadata: Optional[MappingProxyType] = None
    bulk_data: Dict[str, MappingProxyType] = field(default_factory=dict)

    def get_bulk_metadata(self) -> MappingProxyType:
        """Get the metadata for bulk data downloads from Scryfall"""
        if self.bulk_metadata is None:
            url = "https://api.scryfall.com/bulk-data"
            self.bulk_metadata = get_scryfall_json(url)
        return self.bulk_metadata

    def get_bulk_data(self, data_type: str) -> MappingProxyType:
        """Get bulk data of the given type from scryfall"""
        if data_type not in self.bulk_data:
            metadata = self.get_bulk_metadata()
            for data in metadata["data"]:
                if data["type"] == data_type:
                    self.bulk_data[data_type] = get_scryfall_json(data["download_uri"])
                    break
            else:
                raise ValueError(f"No bulk data of type {data_type} in {metadata}")
        return self.bulk_data[data_type]

    def get_all_bulk_data(self) -> None:
        """Download all of the bulk data to save it to cache"""
        metadata = self.get_bulk_metadata()
        for data in metadata["data"]:
            self.get_bulk_data(data["type"])


# Singleton instance for the cache of scryfall data
scryfall_cache = ScryfallCache()

# Copy some singleton methods into module namespace
get_bulk_metadata = scryfall_cache.get_bulk_metadata
get_bulk_data = scryfall_cache.get_bulk_data
get_all_bulk_data = scryfall_cache.get_all_bulk_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    get_all_bulk_data()
