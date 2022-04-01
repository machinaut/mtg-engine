#!/usr/bin/env python
"""
`mtg_cards` - Module for working with MTG card data
"""

import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../data"))
CACHE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../cache"))
