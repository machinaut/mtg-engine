#!/usr/bin/env python
# %% # Card dataclass
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import List

import imgcat
import PIL
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

    def pil(self, fmt='small'):
        ''' Get a PIL.Image '''
        # Prevent circular imports
        from mtg_cards.scryfall import get_card_image
        img_path = get_card_image(self.oracle, fmt=fmt)
        return PIL.Image.open(img_path)


@dataclass
class Cards:
    ''' A list of cards '''
    cards: List[Card] = field(default_factory=list)

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
        else:
            raise IndexError(f'Cards.__getitem__({key})')

    def __add__(self, other):
        if isinstance(other, Cards):
            return self.__class__(self.cards + other.cards)
        raise TypeError(f'Cannot add {type(other)} to {type(self)}')

    def append(self, card):
        ''' Add a card to the pack '''
        assert isinstance(card, Card), f'{card}'
        self.cards.append(card)

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

    def render(self, fmt='small', rowsize=5):
        ''' Display an image with rows of cards '''
        if len(self.cards) == 0:
            return
        # split cards into rows of size rowsize
        rows = [self.cards[i:i + rowsize]
                for i in range(0, len(self.cards), rowsize)]
        # render each row into an image
        imgs = []
        for row in rows:
            rowimgs = [card.pil(fmt=fmt) for card in row]
            # concatenate images together horizontally
            width = sum(img.width for img in rowimgs)
            height = max(img.height for img in rowimgs)
            im = PIL.Image.new('RGB', (width, height))
            x = 0
            for img in rowimgs:
                im.paste(img, (x, 0))
                x += img.width
            imgs.append(im)
        # concatenate all rows together vertically
        width = max(img.width for img in imgs)
        height = sum(img.height for img in imgs)
        im = PIL.Image.new('RGB', (width, height))
        y = 0
        for img in imgs:
            im.paste(img, (0, y))
            y += img.height
        # display the image
        if isnotebook():
            im = Image(data=im.tobytes())
            display(im)
        else:
            imgcat.imgcat(im)
        return im
