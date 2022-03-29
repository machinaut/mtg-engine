# `mtg_cards`

See the [top level Readme](../../README.md) for more information on the whole package.

`util` - Miscellaneous Utilities, doesn't depend on anything else.
`scryfall` - Download Scryfall data and cache locally, returns plain data structures. Depends on `util`.
`cards` - Contains the core classes `Card` and `Cards`, depends on `scryfall`.
`sets` - Handles set specific data, depends on `cards`.
`booster` - Handles the generation of booster packs, depends on `sets`.
