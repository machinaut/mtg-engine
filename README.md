# mtg-engine
Python Engine for Magic: the Gathering

**NOTA BENE:** Only supports a single set for now: [NEO (Kamigawa: Neon Dynasty)](https://scryfall.com/sets/neo).

## Packages

### `mtg_cards` - Card data and card utilities

This is the foundational package, in that all the other packages depend on it.

It includes utilities for downloading data and images from Scryfall, and caching them.

It heavily uses an internal method `proxy()` to make read-only versions of data.

### `mtg_draft` - Draft engine

This simulates a draft, starting with just the standard 8-person 3-pack draft.

The draft is a synchronous-stepping game, with a human interface for debugging.

TODO: pull in 17lands data on drafts to use for simulation.

### `mtg_deck` - Deck utilities

This simulates deckbuilding, starting with sealed limited (6-booster).

TODO: add draft-limited (3-booster, can be <45 cards given basics in packs)

TODO: pull in 17lands data on deckbuilding

### `mtg_engine` - Rules engine for playing games

This simulates a game.  This will be the hardest to build, probably.

## Resources

[Scryfall](https://scryfall.com/sets/neo)
[Hyperlinked MtG Rules](https://yawgatog.com/resources/magic-rules/)
[The Collation Project](https://www.lethe.xyz/mtg/collation/index.html)