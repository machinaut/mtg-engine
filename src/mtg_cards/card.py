#!/usr/bin/env python
# %% # Card dataclass
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import List

import imgcat
from IPython.display import Image, display

from mtg_cards.util import isnotebook


@dataclass
class Card:
    name: str
    oracle: MappingProxyType = field(repr=False)

    @classmethod
    def from_scryfall(cls, card):
        assert isinstance(card, MappingProxyType), f'{card}'
        return cls(name=card['name'], oracle=card)

    @property
    def rarity(self):
        return self.oracle['rarity']

    @property
    def type_line(self):
        return self.oracle['type_line']

    @property
    def dfc(self):
        return 'card_faces' in self.oracle

    @property
    def land(self):
        return 'Land' in self.type_line

    @property
    def basic(self):
        return 'Basic' in self.type_line

    def render(self, fmt='png'):
        ''' Display a card image '''
        # Prevent circular imports
        from mtg_cards.scryfall import get_card_image
        img_path = get_card_image(self.oracle, fmt=fmt)
        # Render the file at img_path
        if isnotebook():
            im = Image(filename=img_path)
            display(im)
        else:
            im = imgcat.imgcat(open(img_path))
        return im


@dataclass
class Cards:
    ''' A list of cards '''
    cards: List[Card]

    def __iter__(self):
        return iter(self.cards)

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, key):
        cards = self.cards[key]
        if isinstance(key, slice):
            return self.__class__(cards)
        elif isinstance(cards, Card):  # Single card
            return cards  # technically a single card
        elif len(cards) == 1:
            assert False, f'{key} returned {len(cards)} cards'
            return cards[0]
        else:
            raise IndexError(f'Update Cards.__getitem__ for: key={key}')

    def __add__(self, other):
        if isinstance(other, Cards):
            return self.__class__(self.cards + other.cards)
        raise TypeError(f'Cannot add {type(other)} to {type(self)}')

    def filt_dfc(self):
        return self.__class__(list(filter(lambda c: c.dfc, self.cards)))

    def filt_not_dfc(self):
        return self.__class__(list(filter(lambda c: not c.dfc, self.cards)))

    def filt_rarity(self, rarity):
        return self.__class__(list(filter(lambda c: c.rarity == rarity, self.cards)))

    def filt_common(self):
        return self.filt_rarity('common')

    def filt_uncommon(self):
        return self.filt_rarity('uncommon')

    def filt_rare(self):
        return self.filt_rarity('rare')

    def filt_mythic(self):
        return self.filt_rarity('mythic')

    def filt_land(self):
        return self.__class__(list(filter(lambda c: c.land, self.cards)))

    def filt_not_land(self):
        return self.__class__(list(filter(lambda c: not c.land, self.cards)))

    def filt_basic(self):
        return self.__class__(list(filter(lambda c: c.basic, self.cards)))

    def pick(self, choice: int) -> Card:
        ''' Pick a card to remove from the pack '''
        assert 0 <= choice < len(self.cards), f'{choice}'
        return self.cards.pop(choice)

    def copy(self) -> 'Cards':
        ''' Get a copy of the cards '''
        return Cards(cards=self.cards.copy())
