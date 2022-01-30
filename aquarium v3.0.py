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
SPEED_PREDATOR = 5         # speed of predators
N_FISH_START = 10        # starting number of fish
N_PREDATOR_START = 0      # starting number of predators
MAX_FISH = 100            # max number of fishs
MAX_PREDATOR = 100
TPS = 10
MAX_DURATION = 1*60*TPS    # number of seconds

PREDATOR_LIFE_TIME = 100
FISH_PROCREATION_AGE = 5
FISH_PROB_PROCREATION = 1./FISH_PROCREATION_AGE
PREDATOR_PROCREATION_MEALS = 30
PREDATOR_VISION = 100  # in pixels per direction

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

    def __init__(self, lifetime=10, colour=BLACK, width=6, height=6):
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


class Predator(Animal):

    def __init__(self, width=20, height=15):
        Animal.__init__(self, width, height)
        self.speed = SPEED_PREDATOR
        self.meals = 0

    def update(self):
        self.move()
        Animal.update(self)
        if self.age >= PREDATOR_LIFE_TIME:
            self.kill()

    def eat(self, n):
        self.meals += n


class Dolphin(Predator):

    def __init__(self, colour=BLUE, width=20, height=15):
        Predator.__init__(self, width, height)
        self.image.fill(colour)

    def decide(self, target_list=[]):
        vision = Block(PREDATOR_VISION, PREDATOR_VISION)
        vision.rect.center = self.rect.center
        vision_list = pygame.sprite.spritecollide(vision, target_list, False)

        if vision_list:
            targ_x = targ_y = 0
            for elem in vision_list:   # Dolphin goes towards most of the fish
                dist = max(((self.rect.x - elem.rect.x)**2 +
                            (self.rect.y - elem.rect.y)**2), 1)
                targ_x += np.cos(np.arctan2((elem.rect.y - self.rect.y),
                                            (elem.rect.x - self.rect.x)))/dist
                targ_y += np.sin(np.arctan2((elem.rect.y - self.rect.y),
                                            (elem.rect.x - self.rect.x)))/dist
                self.angle = np.arctan2(targ_y, targ_x)
        else:
            self.angle = np.arctan2(np.random.randint(-10, 11), 
                                    np.random.randint(-10, 11))

    def procreate(self, same_species_list):
        if (self.meals > PREDATOR_PROCREATION_MEALS and 
            len(same_species_list) < MAX_PREDATOR):
            elem = Dolphin()
            elem.rect.x = self.rect.x
            elem.rect.y = self.rect.y
            same_species_list.add(elem)
            elem.move()
            self.meals = 0
            self.age = 0

    def update(self, target_list, same_species_list):
        self.procreate(same_species_list)
        self.decide(target_list)
        Predator.update(self)
        self.image.fill((0, 0, 
                         int(50 + 205*(1 - self.age / PREDATOR_LIFE_TIME))))


class Shark(Predator):

    def __init__(self, colour=BLACK, width=20, height=15):
        Predator.__init__(self, width, height)
        self.image.fill(colour)

    def decide(self, target_list=[]):
        vision = Block(PREDATOR_VISION, PREDATOR_VISION)
        vision.rect.center = self.rect.center
        vision_list = pygame.sprite.spritecollide(vision, target_list, False)

        if vision_list:
            targ_x = targ_y = 0
            dist_min = SCREEN_HEIGHT**2 + SCREEN_WIDTH**2
            for elem in vision_list:     # shark goes towards the closest fish
                dist = max(((self.rect.x - elem.rect.x)**2 +
                            (self.rect.y - elem.rect.y)**2), 1)
                if dist < dist_min:
                    dist_min = dist
                    targ_x += (elem.rect.x - self.rect.x)
                    targ_y += (elem.rect.y - self.rect.y)
            self.angle = np.arctan2(targ_y, targ_x)
        else:
            self.angle = np.arctan2(np.random.randint(-10, 11), 
                                    np.random.randint(-10, 11))

    def procreate(self, same_species_list):
        if (self.meals > PREDATOR_PROCREATION_MEALS and 
            len(same_species_list) < MAX_PREDATOR):
            elem = Shark()
            elem.rect.x = self.rect.x
            elem.rect.y = self.rect.y
            same_species_list.add(elem)
            elem.move()
            self.meals = 0
            self.age = 0

    def update(self, target_list, same_species_list):
        self.procreate(same_species_list)
        self.decide(target_list)
        Predator.update(self)
        self.image.fill((int(50 + 205*(1 - self.age / PREDATOR_LIFE_TIME)), 
                         0, 0))

# Initialize PyGame
pygame.init()
pygame.display.set_caption(GAME_TITLE)
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

# Launches an introductory menu 
menu.launch(screen)

fish_list = pygame.sprite.Group()
predator_list = pygame.sprite.Group()

for i in range(N_FISH_START):
    fish = Fish(10)
    fish_list.add(fish)

for i in range(N_PREDATOR_START):
    if np.random.uniform() > 0.5:
        predator = Dolphin()
    else:
        predator = Shark()
    predator_list.add(predator)

stage = 1
dt = []
n_fish = []
n_predator = []

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
    n_predator.append(len(predator_list))

    screen.fill(WHITE)
    for predator in predator_list:
        predator.update(fish_list, predator_list)
        fish_hit_list = pygame.sprite.spritecollide(
                        predator, fish_list, True)
        predator.eat(len(fish_hit_list))
    for fish in fish_list:
        fish.update(fish_list)

    font = pygame.font.Font(None, 24)
    text = ('Fish : ' + str(len(fish_list)) + 
            ';  predators : ' + str(len(predator_list)) + '  ')
    text_render = font.render(text, 1, GREEN)
    textpos = text_render.get_rect()
    textpos.right = SCREEN_WIDTH
    textpos.top = 0
    screen.blit(text_render, textpos)

    fish_list.draw(screen)
    predator_list.draw(screen)
    pygame.display.flip()
    clock.tick(TPS)

del font, text_render
pygame.display.quit()
pygame.quit()

