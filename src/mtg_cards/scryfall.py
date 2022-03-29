#!/usr/bin/env python
# %%
import gzip
import json
import logging
import os
from dataclasses import dataclass, field
from types import MappingProxyType, NoneType
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from mtg_cards import DATA_DIR
from mtg_cards.util import proxy


@dataclass
class ScryfallCache:
    """Singleton class for scryfall data cached locally (compressed)."""

    bulk_metadata: Optional[MappingProxyType] = None
    bulk_data: Dict[str, MappingProxyType] = field(default_factory=dict)

    def url_to_path(self, url: str) -> str:
        """Get the local path for a scryfall URL, if it were cached"""
        u = urlparse(url)
        assert u.scheme == "https", f"Expected https url, got {url}"
        assert u.netloc.endswith("scryfall.com"), f"Expected scryfall.com, got {url}"
        assert u.path.startswith("/file/"), f"Expected scryfall file, got {url}"
        return os.path.join(DATA_DIR, u.path[1:])  # remove leading /

    def url_to_compressed_path(self, url: str) -> str:
        """Get the local path for a scryfall URL, if it were cached compressed"""
        return self.url_to_path(url) + ".gz"

    def download_scryfall_file(self, url: str) -> str:
        """Download and cache a scryfall file, uncompressed"""
        path = self.url_to_path(url)
        # Download from scryfall
        logging.debug(f"Downloading {url} to {path}")
        r = requests.get(url)
        r.raise_for_status()
        # Make sure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Save the file
        with open(path, "wb") as f:
            f.write(r.content)
        return path

    def download_scryfall_json(self, url: str) -> str:
        """Download and cache a JSON file from Scryfall, returning local path"""
        path = self.url_to_compressed_path(url)
        logging.debug(f"Compressing {url} to {path}")
        r = requests.get(url)
        r.raise_for_status()
        # Make sure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Save the file compressed
        with gzip.open(path, "wt", encoding="UTF-8") as f:
            json.dump(r.json(), f)
        return path

    def get_scryfall_json(self, url: str) -> MappingProxyType:
        """Get a scryfall json url loaded as a MappingProxyType"""
        path = self.url_to_compressed_path(url)
        if not os.path.exists(path):
            path = self.download_scryfall_json(url)
        with gzip.open(path, "rt", encoding="UTF-8") as f:
            return proxy(json.load(f))

    def get_bulk_metadata(self) -> MappingProxyType:
        """Get the metadata for bulk data downloads from Scryfall"""
        return self.get_scryfall_json("https://api.scryfall.com/bulk-data")

    def get_bulk_data(self, data_type: str) -> MappingProxyType:
        """Get bulk data of the given type from scryfall"""
        metadata = self.get_bulk_metadata()
        for data in metadata["data"]:
            if data["type"] == data_type:
                return self.get_scryfall_json(data["download_uri"])
        raise ValueError(f"No bulk data of type {data_type} in {metadata}")

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
