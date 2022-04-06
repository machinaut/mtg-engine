#!/usr/bin/env python
""" Zone class and subclasses """
from dataclasses import dataclass, field
from random import Random
from typing import List, Optional

from mtg_engine.mtg_cards.cards import Card
from mtg_engine.mtg_decks.decks import Deck
from mtg_engine.mtg_game.objects import CardObject, Object


@dataclass
class Zone:
    """
    Zone:
    A place where objects can be during a game.
    See section 4, "Zones."
    """

    public: bool = True  # only hand and library are hidden zones
    objects: List[Object] = field(default_factory=list)

    def append(self, object_):
        """Append an object to the list"""
        assert isinstance(object_, Object)
        self.objects.append(object_)

    def __len__(self):
        return len(self.objects)


@dataclass
class Library(Zone):
    """
    Library:
    1. A zone. A player's library is where that player draws cards from.
    2. All the cards in a player's library.
    See rule 401, "Library."
    """

    public: bool = False  # Hidden zone
    rng: Random = field(default_factory=Random)

    def shuffle(self):
        """Shuffle the library"""
        self.rng.shuffle(self.objects)


@dataclass
class Hand(Zone):
    """
    Hand:
    1. A zone. A player's hand is where that player holds cards they have drawn but not played yet.
    2. All the cards in a player's hand.
    See rule 402, "Hand."
    """

    public: bool = False  # Hidden zone


@dataclass
class Battlefield(Zone):
    """
    Battlefield:
    A zone. The battlefield is the zone in which permanents exist.
    It used to be known as the "in-play" zone.
    See rule 403, "Battlefield."
    """


@dataclass
class Graveyard(Zone):
    """
    Graveyard:
    1. A zone. A player's graveyard is their discard pile.
    2. All the cards in a player's graveyard.
    See rule 404, "Graveyard."
    """


@dataclass
class Stack(Zone):
    """
    Stack:
    A zone. The stack is the zone in which spells, activated abilities,
    and triggered abilities wait to resolve.
    See rule 405, "Stack."
    """


@dataclass
class Exile(Zone):
    """
    Exile:
    1. A zone. Exile is essentially a holding area for cards.
    It used to be known as the "removed-from-the-game" zone.
    2. To put an object into the exile zone from whatever zone it's currently in.
    An "exiled" card is one that's been put into the exile zone.
    See rule 406, "Exile."
    """


@dataclass
class Command(Zone):
    """
    Command:
    A zone for certain specialized objects that have an overarching effect on the game,
    yet are not permanents and cannot be destroyed.
    See rule 408, "Command."
    """


@dataclass
class Zones:
    """Container class for all of the zones"""

    # Shared zones
    battlefield: Battlefield = field(default_factory=Battlefield)
    stack: Stack = field(default_factory=Stack)
    exile: Exile = field(default_factory=Exile)
    command: Command = field(default_factory=Command)
    # Zones for each player, indexed by player index
    libraries: List[Library] = field(default_factory=list)
    hands: List[Hand] = field(default_factory=list)
    graveyards: List[Graveyard] = field(default_factory=list)

    def setup(self, decks: List[Deck], rng: Random):
        """
        Make a list of libraries, hands, graveyards for each player
        """
        assert len(self.libraries) == 0, "Libraries starts empty"
        assert len(self.hands) == 0, "Hands starts empty"
        assert len(self.graveyards) == 0, "Graveyards starts empty"
        for deck in decks:
            self.hands.append(Hand())
            self.graveyards.append(Graveyard())
            self.libraries.append(
                Library(
                    objects=[CardObject(card=card) for card in deck.main],
                    rng=rng,
                )
            )
            self.libraries[-1].shuffle()

    def draw(self, player: int) -> Card:
        """
        Draw a card from the library and put it in the hand
        """
        library = self.libraries[player]
        hand = self.hands[player]
        # TODO: implement losing the game if the library is empty
        assert len(library.objects) > 0, "Library is empty"
        card = library.objects.pop(0)
        assert isinstance(card, CardObject)
        hand.append(card)
        return card.card

    def hand_to_library_bottom(self, player: int, card: Card):
        """
        Put a card from the hand to the bottom of the library
        """
        hand = self.hands[player]
        library = self.libraries[player]
        # find the object that matches the card
        found: Optional[CardObject] = None
        for obj in hand.objects:
            assert isinstance(obj, CardObject)
            if obj.card == card:
                found = obj
                break
        else:
            raise ValueError(f"Card {card} not found in hand")
        # remove the object from the hand
        hand.objects.remove(found)
        # put the object at the bottom of the library
        library.objects.append(found)

    def shuffle_hand_into_library(self, player: int):
        """
        Shuffle the hand into the library
        """
        hand = self.hands[player]
        library = self.libraries[player]
        library.objects.extend(hand.objects)
        hand.objects.clear()
        library.shuffle()
