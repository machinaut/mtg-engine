#!/usr/bin/env python
"""
`mtg_cards.cards` MTG card dataclasses

Card - is the primary class for a single card, and
Cards - is the primary class for an ordered list of cards.

Note: There should only ever be one Card object for each card,
so the Card class is a singleton.

Cards objects can have arbitrarily many Card objects, in any order.

TODO: test that rendering a single card and sets of cards works,
both in jupyter and in a terminal.
"""
# %%
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Iterator, List, Union

import imgcat
import PIL
from IPython.display import Image, display

from mtg_engine.mtg_cards.scryfall import cache_scryfall_file
from mtg_engine.mtg_cards.util import isnotebook


@dataclass
class Card:
    """
    Card - is the primary class for a single MtG card
    There should only ever be one Card object for each card,
    so the Card class is a singleton.

    card.oracle contains the scryfall data for the card,
    and is the source of truth for all the other card data.

    Visually display a single card with Card.render()
    """

    name: str
    oracle: MappingProxyType = field(repr=False)

    def __hash__(self) -> int:
        """Hash based on the name of the card"""
        return hash(self.name)

    @property
    def set_number(self):
        """Get the set number of the card"""
        return (self.oracle["set"], self.oracle["collector_number"])

    def __lt__(self, other) -> bool:
        """Used to sort cards by set and collector number"""
        assert isinstance(other, Card), f"{other}"
        return self.set_number < other.set_number

    @classmethod
    def from_json(cls, card):
        """Create a Card object from a scryfall JSON card"""
        assert isinstance(card, MappingProxyType), f"{card}"
        return cls(name=card["name"], oracle=card)

    @property
    def rarity(self):
        """Get the rarity of the card"""
        return self.oracle["rarity"]

    @property
    def type_line(self):
        """Get the type line of the card"""
        return self.oracle["type_line"]

    @property
    def dfc(self):
        """Get the double-faced card"""
        return "card_faces" in self.oracle

    @property
    def land(self):
        """Is the card a land?"""
        return "Land" in self.type_line

    @property
    def basic(self):
        """Is the card a basic land?"""
        return "Basic" in self.type_line

    def get_image_url(self, fmt="small"):
        """Get the scryfall URL for a card image"""
        # Handle double-faced cards
        card = self.oracle
        if "card_faces" in card:
            card = card["card_faces"][0]  # Just get the front image
        assert "image_uris" in card, f"{card.keys()}"
        assert fmt in card["image_uris"], f"{card['image_uris'].keys()}"
        return card["image_uris"][fmt]

    def get_card_image(self, fmt="small"):
        """Get a path to a local card image"""
        image_url = self.get_image_url(fmt=fmt)
        return cache_scryfall_file(image_url)

    def render(self, fmt="png"):
        """Display a card image"""
        img_path = self.get_card_image(fmt=fmt)
        # Render the file at img_path
        if isnotebook():
            img = Image(filename=img_path)
            display(img)
        else:
            with open(img_path, "rb") as file:
                imgcat.imgcat(file)
            img = None
        return img

    def pil(self, fmt="small"):
        """Get a PIL.Image"""
        img_path = self.get_card_image(fmt=fmt)
        return PIL.Image.open(img_path)


@dataclass
class Cards:
    """
    Cards - A list of Card objects.

    Cards should have many list-like dynamics, like adding or appending.
    There are many filter methods that can be chained together, e.g.:

    cards = Cards.filt_land().filt_common().filt_basic()

    Visually display cards in a grid with Cards.render()
    """

    cards: List[Card] = field(default_factory=list)

    def __iter__(self) -> Iterator[Card]:
        """Iterate over the cards"""
        return iter(self.cards)

    def __len__(self) -> int:
        """Get the number of cards in the list"""
        return len(self.cards)

    def __getitem__(self, key) -> Union[Card, "Cards"]:
        """Get a card or a subset of cards by index"""
        cards = self.cards[key]
        if isinstance(key, slice):
            return self.__class__(cards)
        if isinstance(cards, Card):  # Single card
            return cards  # technically a single card
        raise IndexError(f"Cards.__getitem__({key})")

    def __add__(self, other) -> "Cards":
        """Add two Cards objects together (concatenate)"""
        if isinstance(other, Cards):
            return self.__class__(self.cards + other.cards)
        raise TypeError(f"Cannot add {type(other)} to {type(self)}")

    def __sub__(self, other) -> "Cards":
        """Return a copy of these cards, but without the other cards"""
        assert isinstance(other, Cards), f"{other}"
        other = other.sorted_copy()
        result = []
        for card in self.sorted_copy():
            if len(other) and card == other[0]:
                other.cards.pop(0)
            else:  # Add every card thats not in other
                result.append(card)
        assert len(other) == 0, f"Subtract leftover {other}"
        return self.__class__(result)

    def __contains__(self, card) -> bool:
        """Is a given card in this set of cards"""
        assert isinstance(card, Card), f"{card}"
        return card in self.cards

    def append(self, card) -> None:
        """Add a card to the pack"""
        assert isinstance(card, Card), f"{card}"
        self.cards.append(card)

    def remove(self, card) -> None:
        """Remove a card from the pack"""
        assert isinstance(card, Card), f"{card}"
        self.cards.remove(card)

    def pop(self, index) -> Card:
        """Remove a card from the pack"""
        assert isinstance(index, int), f"{index}"
        return self.cards.pop(index)

    def count(self, card) -> int:
        """Get the number of times a card appears"""
        assert isinstance(card, Card), f"{card}"
        return self.cards.count(card)

    def filt_dfc(self) -> "Cards":
        """Filter to just cards that are double-faced"""
        return self.__class__(list(filter(lambda c: c.dfc, self.cards)))

    def filt_not_dfc(self) -> "Cards":
        """Filter to just cards that are not double-faced"""
        return self.__class__(list(filter(lambda c: not c.dfc, self.cards)))

    def filt_rarity(self, rarity) -> "Cards":
        """Filter to just cards of a certain rarity"""
        return self.__class__(list(filter(lambda c: c.rarity == rarity, self.cards)))

    def filt_common(self) -> "Cards":
        """Filter to just cards that are common"""
        return self.filt_rarity("common")

    def filt_uncommon(self) -> "Cards":
        """Filter to just cards that are uncommon"""
        return self.filt_rarity("uncommon")

    def filt_rare(self) -> "Cards":
        """Filter to just cards that are rare"""
        return self.filt_rarity("rare")

    def filt_mythic(self) -> "Cards":
        """Filter to just cards that are mythic rare"""
        return self.filt_rarity("mythic")

    def filt_land(self) -> "Cards":
        """Filter to just cards that are a land"""
        return self.__class__(list(filter(lambda c: c.land, self.cards)))

    def filt_not_land(self) -> "Cards":
        """Filter to just cards that are not a land"""
        return self.__class__(list(filter(lambda c: not c.land, self.cards)))

    def filt_basic(self) -> "Cards":
        """Filter to just cards that are a basic land"""
        return self.__class__(list(filter(lambda c: c.basic, self.cards)))

    def filt_set(self, set_name):
        """Filter for cards in a given set"""
        set_name = set_name.lower()
        return self.__class__(
            list(filter(lambda c: c.oracle["set"] == set_name, self.cards))
        )

    def filt_booster(self):
        """Filter for cards that are in draft boosters"""
        return self.__class__(list(filter(lambda c: c.oracle["booster"], self.cards)))

    def sort(self):
        """Sort by set and collector number"""
        self.cards.sort(key=lambda c: c.set_number)

    def pick(self, choice: int) -> Card:
        """Pick a card to remove from the pack"""
        assert 0 <= choice < len(self.cards), f"{choice}"
        return self.cards.pop(choice)

    def copy(self) -> "Cards":
        """Get a copy of the cards"""
        return self.__class__(cards=self.cards.copy())

    def sorted_copy(self) -> "Cards":
        """Get a copy of the cards, sorted by set and collector number"""
        cards = self.copy()
        cards.sort()
        return cards

    def render(self, fmt="small", rowsize=5):
        """Display an image with rows of cards"""
        if len(self.cards) == 0:
            return None
        # split cards into rows of size rowsize
        rows = [self.cards[i : i + rowsize] for i in range(0, len(self.cards), rowsize)]
        # render each row into an image
        imgs = []
        for row in rows:
            rowimgs = [card.pil(fmt=fmt) for card in row]
            # concatenate images together horizontally
            width = sum(img.width for img in rowimgs)
            height = max(img.height for img in rowimgs)
            img = PIL.Image.new("RGB", (width, height))
            x_offset = 0
            for rowimg in rowimgs:
                img.paste(rowimg, (x_offset, 0))
                x_offset += rowimg.width
            imgs.append(img)
        # concatenate all rows together vertically
        width = max(img.width for img in imgs)
        height = sum(img.height for img in imgs)
        img = PIL.Image.new("RGB", (width, height))
        y_offset = 0
        for rowimg in imgs:
            img.paste(rowimg, (0, y_offset))
            y_offset += rowimg.height
        # display the image
        if isnotebook():
            img = Image(data=img.tobytes())
            display(img)
        else:
            imgcat.imgcat(img)
        return img


# if __name__ == '__main__':
#     from mtg_engine.mtg_cards.sets import get_set
#     get_set('neo').render()
