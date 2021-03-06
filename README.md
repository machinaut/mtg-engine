# mtg-engine
Python Engine for Magic: the Gathering

![Pytest Status](https://github.com/machinaut/mtg-engine/actions/workflows/pytest.yml/badge.svg) ![Pylint Status](https://github.com/machinaut/mtg-engine/actions/workflows/pylint.yml/badge.svg)

**NOTA BENE:** Only supports a single set for now: [NEO (Kamigawa: Neon Dynasty)](https://scryfall.com/sets/neo).

## Sub-Modules

### `decision_engine` - Rules engine for playing games

This is an abstract game engine, where there is a core game engine which sends messages to and from players.

The messages are views (updates to the state of the board), or choices (actions players must take), or decisions (chosen options).

### `mtg_cards` - Card data and card utilities

This is the foundational data package.
It includes utilities for downloading data and images from Scryfall, and caching them.

It heavily uses an internal method `proxy()` to make read-only versions of data.

### `mtg_draft` - Draft engine

This simulates a draft, starting with just the standard 8-person 3-pack draft.

The draft is a synchronous-stepping game, with a human interface for debugging.

TODO: pull in 17lands data on drafts to use for simulation.

### `mtg_decks` - Deck utilities

This simulates deckbuilding, starting with sealed limited (6-booster).

TODO: pull in 17lands data on deckbuilding

### `mtg_game` - Rules engine for playing games

This simulates a game.  This will be the hardest to build, probably.

## Resources

* [Scryfall](https://scryfall.com/sets/neo)
* [Hyperlinked MtG Rules](https://yawgatog.com/resources/magic-rules/)
* [The Collation Project](https://www.lethe.xyz/mtg/collation/index.html)
