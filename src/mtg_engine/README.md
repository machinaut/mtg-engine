# Decision Engine Design

This is a generic design for a decision engine for multiplayer games.

A central engine runs the game, and it interacts with players who make decisions.

Three kinds of entities that store state:
* `engine` - which centrally has all of the state, including all of the entropy
* `player` - which have a private view of the state given by the engine

There's three basic actions that happen in the game:
* `view` - the engine gives an update to all of the players
* `choice` - the engine sends a choice (with options) to a single player
* `decision` - the player sends a decision in response to a choice

### Engine

The engine has all of the state and logic of the game, including the entropy.
So all dice rolls, the order of all cards in shuffled decks, etc is known to the engine.

Views are sent to all players together, but each one receives distinct views,
based on information that might be private to them.

The engine needs to figure out possible actions in order to send out choices,
which can mean it needs to do some kind of look-ahead in the game.
E.g. in order to figure out which spells a player can start casting,
the engine needs to figure out which spells have valid targets,
and the player can pay the costs for.

### Player

The player receives the views sent by the engine, as well as choices, to which it responds with decisions.

All of the views, choices, and decisions observed by a player are saved to a sequential history.

This history is what is used when training sequence models to predict the next action.

### View

These describe some update to the state of the game, which is visible to the player.
Different views are sent to different players, for example, when drawing a card,
only the player who drew the card can see the card.

```
    Player 1: You drew a Plains.
    Player 2: Player 1 drew a card.
```

Views are meant to be small, near-atomic updates.
The engine can send multiple views in a row without sending any choices.

### Choice

When the game gets to a point when a player must make a decision.
It contains a brief description of the choice that must be made,
and also contains all of the options enumerated.

```
Choice: Choose a card to put into your graveyard.
A. B. C.  .... (Cards in hand)
```

Many choices that are notionally a single action (e.g. "choose an ordering for these cards"),
are broken into several choices (e.g. "choose a first card, then a second, then a third, etc").

Choices are private to the player they are sent to,
and are not visible to other players.

Choices must have at least two options.  In cases where the player has no choice,
then the engine should just send a view
(which might look to the other players as if a choice had been made).

### Decision

A decision is a response from a player to a choice sent to them.
It is private to just the player and the engine.

The decision selects one of the enumerated options from the chioces.
