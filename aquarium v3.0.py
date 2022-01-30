# -*- coding: utf-8 -*-
"""
Simple simulation of an aquarium with fish and predators

- The fish (black squares) move on a straight line;
- The dolphins (blue rectangles) chase the mass of fish;
- The sharks (red rectangles) chase the single closest fish.

See which species outlives the other

Created on Sat Mar 19 22:29:59 2016
@author: Riccardo Rossi
"""

import numpy as np
import time
import pygame
import matplotlib.pyplot as plt
import warnings
import menu                        # meny.py should be in the folder
np.random.seed(int(time.time()))
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Parameters
GAME_TITLE = 'The Aquarium'
SPEED_FISH = 5             # speed of fish
N_FISH_START = 10        # starting number of fish
MAX_FISH = 100            # max number of fishs
TPS = 10
MAX_DURATION = 1*60*TPS    # number of seconds

FISH_PROCREATION_AGE = 50
FISH_PROB_PROCREATION = 1./FISH_PROCREATION_AGE

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 100, 0)


# Define the objects needed for the simulation
class Block(pygame.sprite.Sprite):

    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect()


class Animal(Block):

    def __init__(self, width, height):
        Block.__init__(self, width, height)
        self.rect.x = np.random.randint(0, SCREEN_WIDTH)
        self.rect.y = np.random.randint(0, SCREEN_HEIGHT)
        self.angle = np.arctan2(np.random.randint(-10, 11), 
                                np.random.randint(-10, 11))
        self.age = 0
        self.speed = 0

    def stay_on_screen(self):
        if self.rect.right > SCREEN_WIDTH or self.rect.x < 0:
            self.angle = np.pi - self.angle
        if self.rect.bottom > SCREEN_HEIGHT or self.rect.y < 0:
            self.angle = -self.angle

    def move(self):
        self.rect.x += int(self.speed * np.cos(self.angle))
        self.rect.y += int(self.speed * np.sin(self.angle))

    def get_old(self):
        self.age += 1

    def update(self):
        self.get_old()


class Fish(Animal):

    def __init__(self, lifetime=5000, colour=BLACK, width=6, height=6):
        Animal.__init__(self, width, height)
        self.image.fill(colour)
        self.speed = SPEED_FISH
        self.lifetime = lifetime

    def procreate(self, same_species_list):
        if (self.age > FISH_PROCREATION_AGE and 
            FISH_PROB_PROCREATION > np.random.uniform() and 
            len(same_species_list) < MAX_FISH):
            elem = Fish()
            elem.rect.x = self.rect.x
            elem.rect.y = self.rect.y
            same_species_list.add(elem)
            self.age = 0

    def update(self, same_species_list):
        self.move()
        self.stay_on_screen()
        Animal.update(self)
        self.procreate(same_species_list)
        if self.age >= self.lifetime:
            self.kill()

# Initialize PyGame
pygame.init()
pygame.display.set_caption(GAME_TITLE)
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# Launches an introductory menu 
menu.launch(screen)

fish_list = pygame.sprite.Group()
predator_list = pygame.sprite.Group()

for i in range(N_FISH_START):
    fish = Fish()
    fish_list.add(fish)

stage = 1
dt = []
n_fish = []

running = True
clock = pygame.time.Clock()
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            running = False
            
    stage += 1
    dt.append(stage)
    n_fish.append(len(fish_list))

    screen.fill(WHITE)
    for fish in fish_list:
        fish.update(fish_list)

    font = pygame.font.Font(None, 24)
    text = ('Fish : ' + str(len(fish_list)) + '  ')
    text_render = font.render(text, 1, GREEN)
    textpos = text_render.get_rect()
    textpos.right = SCREEN_WIDTH
    textpos.top = 0
    screen.blit(text_render, textpos)

    fish_list.draw(screen)
    pygame.display.flip()
    clock.tick(TPS)

del font, text_render
pygame.display.quit()
pygame.quit()

