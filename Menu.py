"""
pygame-menu
https://github.com/ppizarror/pygame-menu
EXAMPLE - SCROLL MENU
Shows scrolling in menu.
"""

__all__ = ['main']
import random
from turtle import color                       # meny.py should be in the folder

import pygame
import pygame_menu
from pygame_menu.examples import create_example_window

from typing import Any
from functools import partial

FPS = 30
WINDOW_SIZE = (800, 600)
number_of_colors = 8
colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
              for i in range(number_of_colors)]


class Menu:
    @staticmethod
    def on_button_click(value: str, text: Any = None) -> None:
        """
        Button event on menus.
        :param value: Button value
        :param text: Button text
        """
        # if not text:
        #     print(f'Hello from {value}')
        # else:
        #     print(f'Hello from {text} with {value}')
    @staticmethod
    def paint_background(surface: 'pygame.Surface') -> None:
        """
        Paints a given surface with background color.
        :param surface: Pygame surface
        """
        surface.fill((128, 230, 198))

    @staticmethod
    def make_long_menu() -> 'pygame_menu.Menu':
        """
        Create a long scrolling menu.
        :return: Menu
        """
        theme_menu = pygame_menu.themes.THEME_BLUE.copy()
        theme_menu.scrollbar_cursor = pygame_menu.locals.CURSOR_HAND

        # Main menu, pauses execution of the application
        menu = pygame_menu.Menu(
            height=400,
            onclose=pygame_menu.events.EXIT,
            theme=theme_menu,
            title='Other ponds',
            width=600
        )

        menu_sub = pygame_menu.Menu(
            columns=4,
            height=400,
            onclose=pygame_menu.events.EXIT,
            rows=3,
            theme=pygame_menu.themes.THEME_GREEN,
            title='Menu with columns',
            width=600
        )

        menu_contributors = pygame_menu.Menu(
            height=400,
            onclose=pygame_menu.events.EXIT,
            theme=pygame_menu.themes.THEME_SOLARIZED,
            title='Contributors',
            width=600
        )

        # Add table to contributors
        table_contrib = menu_contributors.add.table()
        table_contrib.default_cell_padding = 5
        table_contrib.default_row_background_color = 'white'
        bold_font = pygame_menu.font.FONT_OPEN_SANS_BOLD
        table_contrib.add_row(['N°', 'Github User'], cell_font=bold_font)
        for i in range(len(pygame_menu.__contributors__)):
            table_contrib.add_row([i + 1, pygame_menu.__contributors__[i]],
                                  cell_font=bold_font if i == 0 else None)

        # Update all column/row
        table_contrib.update_cell_style(-1, -1, font_size=15)
        table_contrib.update_cell_style(
            1, [2, -1], font=pygame_menu.font.FONT_OPEN_SANS_ITALIC)

        # for i in range(100):
        #     TextDraw("hello", font, colors[i], 10, i*20).draw(screen)

        # menu.add.button('Rows and Columns', menu_sub)
        # menu.add.button('Text scrolled', menu_text)
        # menu.add.button('Pygame-menu contributors', menu_contributors)
        # menu.add.vertical_margin(20)  # Adds margin

        # label1 = 'Button n°{}'
        # label2 = 'Text n°{}: '
        # for i in range(1, 20):
        #     if i % 2 == 0:
        #         menu.add.button(label1.format(i),
        #                         on_button_click,
        #                         f'Button n°{i}')
        #     else:
        #         menu.add.text_input(label2.format(i),
        #                             onchange=on_button_click,
        #
        #
        for i in range(8):
            menu.add.label(
                'fish pond',
                max_char=33,
                align=pygame_menu.locals.ALIGN_LEFT,
                margin=(0, 0),
                font_color=colors[i],
            )
        # menu.add.button('Exit', pygame_menu.events.EXIT)
        menu.add.button('My pond', pygame_menu.events.EXIT)

        label = 'Button n°{}'
        for i in range(1, 11):
            # Test large button
            if i == 5:
                txt = 'This is a very long button!'
            else:
                txt = label.format(100 * i)
            menu_sub.add.button(txt, Menu.on_button_click, 100 * i)
        menu_sub.add.button('Back', pygame_menu.events.BACK)

        # noinspection SpellCheckingInspection

        return menu


# def main(test: bool = False) -> None:
#     """
#     Main function.
#     :param test: Indicate function is being tested
#     """
#     screen = create_example_window('Example - Scrolling Menu', WINDOW_SIZE)
#     number_of_colors = 100

#     clock = pygame.time.Clock()

#     font = pygame.font.Font(None, 24)

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    # while True:

        # clock.tick(FPS)

        # Menu.paint_background(screen)
        # menu = Menu.make_long_menu()

        # menu.mainloop(
        #     surface=screen,
        #     bgfun=partial(Menu.paint_background, screen),
        #     disable_loop=test,
        #     fps_limit=FPS
        # )

        # pygame.display.flip()

        # if test:
        #     break
