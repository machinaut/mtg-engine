#!/usr/bin/env python
# %% # Render cards
import imgcat
from IPython.display import Image, display

from mtg_cards.scryfall import get_card_image


def isnotebook():
    # https://stackoverflow.com/a/39662359
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


def render_card(card, fmt='png'):
    ''' Render a card image '''
    img_path = get_card_image(card, fmt=fmt)
    # Render the file at img_path
    if isnotebook():
        im = Image(filename=img_path)
        display(im)
    else:
        im = imgcat.imgcat(open(img_path))
    return im


if __name__ == '__main__':
    from mtg_cards.booster import get_booster

    for card in get_booster('neo'):
        render_card(card)
