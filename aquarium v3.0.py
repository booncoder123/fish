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
MAX_SIZE = 48
MAX_DURATION = 1*60*TPS    # number of seconds

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREY = (169,169,169)
GREEN = (0, 100, 0)


# Define the objects needed for the simulation
class Block(pygame.sprite.Sprite):

    def __init__(self, width, height, color = BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
    def changeSize(self, width, height):
        self.image = pygame.Surface([width, height])
        self.image.fill(self.color)

class Bar(Block):

    def __init__(self,x, y, lifetime, width=0, height=6,):
        self.width = width
        self.height = height
        self.lifetime = lifetime
        Block.__init__(self, self.width, self.height, RED)
        self.rect.x = x
        self.rect.y = y
    def update(self):
        self.width += (MAX_SIZE / self.lifetime)
        self.changeSize(self.width, self.height)

class MaxBar(Block):

    def __init__(self,x, y, width=6, height=6,):
        self.width = width
        self.height = height
        Block.__init__(self, self.width, self.height, GREY)
        self.rect.x = x
        self.rect.y = y
    def update(self, currentSize):
        self.width = currentSize
        self.changeSize(self.width, self.height)

class Fish(Block):

    def __init__(self, lifetime=100, colour=BLACK, width=6, height=6):
        self.width = width
        self.height = height
        self.lifetime = lifetime
        Block.__init__(self, self.width, self.height)
        self.rect.x = np.random.randint(0, SCREEN_WIDTH)
        self.rect.y = np.random.randint(0, SCREEN_HEIGHT)
        self.bar = Bar(self.rect.x, self.rect.y - 12, self.lifetime)
        self.maxBar = MaxBar(self.rect.x, self.rect.y - 12)
        self.angle = np.arctan2(np.random.randint(-10, 11), 
                                np.random.randint(-10, 11))
        self.age = 0
        self.speed = SPEED_FISH
        self.lifetime = lifetime
        self.growth_rate = MAX_SIZE / (self.lifetime / 2)

    def procreate(self, same_species_list, bar_list, maxBar_list):
        lay_age = self.lifetime / 2
        lay_prob = 1./lay_age
        if (self.age > lay_age and 
           lay_prob > np.random.uniform() and 
            len(same_species_list) < MAX_FISH):
            elem = Fish(np.random.randint(50,250))
            elem.rect.x = self.rect.x
            elem.rect.y = self.rect.y
            elem.bar.rect.x = self.rect.x
            elem.bar.rect.y = self.rect.y - 12
            elem.maxBar.rect.x = self.rect.x
            elem.maxBar.rect.y = self.rect.y - 12
            same_species_list.add(elem)
            bar_list.add(elem.bar)
            maxBar_list.add(elem.maxBar)

    def stay_on_screen(self):
        if self.rect.right > SCREEN_WIDTH or self.rect.x < 0:
            self.angle = np.pi - self.angle
        if self.rect.bottom > SCREEN_HEIGHT or self.rect.y < 0:
            self.angle = -self.angle

    def move(self):
        self.rect.x += int(self.speed * np.cos(self.angle))
        self.rect.y += int(self.speed * np.sin(self.angle))
        self.bar.rect.x += int(self.speed * np.cos(self.angle))
        self.bar.rect.y += int(self.speed * np.sin(self.angle))
        self.maxBar.rect.x += int(self.speed * np.cos(self.angle))
        self.maxBar.rect.y += int(self.speed * np.sin(self.angle))

    def update(self, same_species_list, bar_list, maxBar_list):
        self.move()
        self.stay_on_screen()
        self.age += 1
        self.bar.update()
        self.procreate(same_species_list, bar_list, maxBar_list)
        if(self.age <= (self.lifetime / 2) and self.width < MAX_SIZE):
            self.width += self.growth_rate
            self.height += self.growth_rate
            self.changeSize(self.width, self.height)
        self.maxBar.update(self.width)
        if self.age >= self.lifetime:
            self.kill()
            self.bar.kill()
            self.maxBar.kill()

# Initialize PyGame
pygame.init()
pygame.display.set_caption(GAME_TITLE)
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# Launches an introductory menu 
menu.launch(screen)

fish_list = pygame.sprite.Group()
bar_list = pygame.sprite.Group()
maxBar_list = pygame.sprite.Group()

for i in range(N_FISH_START):
    fish = Fish(np.random.randint(50,250))
    fish_list.add(fish)
    bar_list.add(fish.bar)
    maxBar_list.add(fish.maxBar)
    

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
        fish.update(fish_list, bar_list, maxBar_list)

    font = pygame.font.Font(None, 24)
    text = ('Fish : ' + str(len(fish_list)) + '  ')
    text_render = font.render(text, 1, GREEN)
    textpos = text_render.get_rect()
    textpos.right = SCREEN_WIDTH
    textpos.top = 0
    screen.blit(text_render, textpos)

    fish_list.draw(screen)
    maxBar_list.draw(screen)
    bar_list.draw(screen)
    
    pygame.display.flip()
    clock.tick(TPS)

del font, text_render
pygame.display.quit()
pygame.quit()

