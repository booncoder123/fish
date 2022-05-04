# -*- coding: utf-8 -*-
# back-end
import Client as client


import numpy as np
import threading
import time
import pygame
import matplotlib.pyplot as plt
import warnings
# import menu
import random                       # meny.py should be in the folder

from FishData import FishData
from PondData import PondData
from Client import Client
from Menu import Menu
from functools import partial

FPS = 30
np.random.seed(int(time.time()))
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Parameters
number_of_colors = 8

GAME_TITLE = 'The Aquarium'
SPEED_FISH = 5            # speed of fish    # starting number of fish
MAX_FISH = 100            # max number of fishs
TPS = 60
MAX_SIZE = 48
MAX_DURATION = 1*60*TPS    # number of seconds

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREY = (169, 169, 169)
GREEN = (0, 100, 0)

pla = pygame.image.load("./asset/fish.png")
sicksalmon = pygame.image.load("./asset/SickSalmon.png")
peem = pygame.image.load("./asset/Peem.png")


# Define the objects needed for the simulation
class Block(pygame.sprite.Sprite):

    def __init__(self, width, height, fill, color=BLACK):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = pygame.Surface([width, height])
        self.fill = fill
        if(self.fill):
            self.image.fill(color)
        self.rect = self.image.get_rect()

    def changeSize(self, width, height):
        self.image = pygame.Surface([width, height])
        if(self.fill):
            self.image.fill(self.color)


class Bar(Block):

    def __init__(self, x, y, lifetime, width=0, height=6,):
        self.width = width
        self.height = height
        self.lifetime = lifetime
        Block.__init__(self, self.width, self.height, True, RED)
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.width += (MAX_SIZE / self.lifetime)
        self.changeSize(self.width, self.height)


class MaxBar(Block):

    def __init__(self, x, y, width=6, height=6,):
        self.width = width
        self.height = height
        Block.__init__(self, self.width, self.height, True, GREY)
        self.rect.x = x
        self.rect.y = y

    def update(self, currentSize):
        self.width = currentSize
        self.changeSize(self.width, self.height)


class Fish(Block):

    def __init__(self, fishData, img=pla):
        self.fishData = fishData
        self.width = 6
        self.height = 6
        self.lifetime = fishData.lifetime
        self.face_right = True
        self.img = img
        Block.__init__(self, self.width, self.height, False)
        self.image = self.img
        self.image = pygame.transform.scale(
            self.image, (self.width, self.height))
        self.rect.x = np.random.randint(0, SCREEN_WIDTH)
        self.rect.y = np.random.randint(0, SCREEN_HEIGHT)
        self.bar = Bar(self.rect.x, self.rect.y - 12, self.lifetime)
        self.maxBar = MaxBar(self.rect.x, self.rect.y - 12)
        self.angle = np.arctan2(np.random.randint(-10, 11),
                                np.random.randint(-10, 11))
        self.age = 0
        self.speed = SPEED_FISH
        self.growth_rate = MAX_SIZE / (self.lifetime / 2)

    def changeSize(self, width, height):
        self.image = self.img
        self.image = pygame.transform.scale(self.image, (width, height))
        if not self.face_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def procreate(self, same_species_list, bar_list, maxBar_list):

        if (self.fishData.pheromone >= (self.fishData.pheromoneThresh * 10)):
            baby = FishData("Pla", self.fishData.id)
            elem = Fish(baby)
            elem.rect.x = self.rect.x
            elem.rect.y = self.rect.y
            elem.bar.rect.x = self.rect.x
            elem.bar.rect.y = self.rect.y - 12
            elem.maxBar.rect.x = self.rect.x
            elem.maxBar.rect.y = self.rect.y - 12
            c.pond.fishes.append(baby)
            same_species_list.add(elem)
            bar_list.add(elem.bar)
            maxBar_list.add(elem.maxBar)
            self.fishData.pheromone = 0

    def stay_on_screen(self):
        if self.rect.right > SCREEN_WIDTH or self.rect.x < 0:
            self.angle = np.pi - self.angle

        if self.rect.bottom > SCREEN_HEIGHT or self.rect.y < 0:
            self.angle = -self.angle

    def move(self):
        face = int(self.speed * np.cos(self.angle))
        if(face < 0 and self.face_right):
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_right = False
        elif(face >= 0 and not self.face_right):
            self.image = pygame.transform.flip(self.image, True, False)
            self.face_right = True
        # elif(face >= 0 and not self.face_right):
        #     self.image = pygame.transform.flip(self.image, True, False)
        self.rect.x += face
        self.rect.y += int(self.speed * np.sin(self.angle))
        self.bar.rect.x += face
        self.bar.rect.y += int(self.speed * np.sin(self.angle))
        self.maxBar.rect.x += face
        self.maxBar.rect.y += int(self.speed * np.sin(self.angle))

    def update(self, same_species_list, bar_list, maxBar_list):
        self.move()
        self.stay_on_screen()
        self.age += 1
        self.fishData.pheromone += 1
        self.bar.update()
        self.procreate(same_species_list, bar_list, maxBar_list)
        if(self.age <= (self.lifetime / 2) and self.width < MAX_SIZE):
            self.width += self.growth_rate
            self.height += self.growth_rate
            self.changeSize(self.width, self.height)
        self.maxBar.update(self.width)
        if self.age >= self.lifetime:
            self.fishData.status = 'dead'
        if len(c.pond.fishes) >= self.fishData.crowdThreshold:
            self.fishData.status = 'dead'
        if self.age == self.lifetime//2 and random.randint(0, 100) > 80:
            group_names = ['PEEM', 'SICK-SALMON']
            rand = random.randint(0, len(group_names)-1)
            migrate_handler = threading.Thread(
                target=c.migrate_fish, args=[self.fishData, group_names[rand]])
            migrate_handler.start()
            self.fishData.state = 'on-migrate'


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [0, 0]


class TextDraw:

    def __init__(self, text, font, color=BLACK, x=0, y=0):

        self.text = text
        self.font = font
        self.color = color
        self.x = x
        self.y = y

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        self.rect = self.font.render(self.text, True, self.color)
        screen.blit(self.rect, (self.x, self.y))


# Initialize PyGame

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption(GAME_TITLE)
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

    # Launches an introductory menu
    # menu.launch(screen)

    fish_list = pygame.sprite.Group()
    bar_list = pygame.sprite.Group()
    maxBar_list = pygame.sprite.Group()

    # Client
    # fish_list = []

    MY_POND = PondData("PLA")
    f1 = FishData("PLA", "123456")
    f2 = FishData("PLA", "123456")
    MY_POND.addFish(f1)
    MY_POND.addFish(f2)
    c = Client(MY_POND)
    msg_handler = threading.Thread(target=c.get_msg)
    msg_handler.start()
    send_handler = threading.Thread(target=c.send_pond)
    send_handler.start()
    # f1 = FishData("Sick Salmon", "123456")
    # f2 = FishData("Fish2", "123456")
    # MY_POND.addFish(f1)
    # MY_POND.addFish(f2)

    def fishCompare(fish1, fish2):
        if(fish1.id != fish2.id):
            return False
        return True

    # for client_fish in c.pond.fishes:
    #     fish_list.add(Fish(client_fish))

    # for fish in fish_list:
    #     fish = Fish(fish)
    #     fish_list.add(fish)
    #     bar_list.add(fish.bar)
    #     maxBar_list.add(fish.maxBar)

    for i in c.pond.fishes:
        fish = Fish(i)
        fish_list.add(fish)
        bar_list.add(fish.bar)
        maxBar_list.add(fish.maxBar)

    stage = 1
    dt = []
    n_fish = []
    number_of_colors = 100

    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
              for i in range(number_of_colors)]

    running = True
    clock = pygame.time.Clock()

    ourPondFishList = c.pond.fishes
    temp_fish_list = pygame.sprite.Group()
    temp_bar_list = pygame.sprite.Group()
    temp_maxBar_list = pygame.sprite.Group()

    def openMenu():
        Menu.paint_background(screen)
        menu = Menu.make_long_menu()

        menu.mainloop(
            surface=screen,
            bgfun=partial(Menu.paint_background, screen),
            disable_loop=False,
            fps_limit=FPS
        )

    def openGame():
        if(len(c.pond.fishes) > len(fish_list)):
            fish_diff = len(c.pond.fishes)-(len(fish_list))
            new_list = c.pond.fishes[len(fish_list):len(c.pond.fishes)]
            for fish in new_list:
                if(fish.fishData.genesis == "Peem"):
                    sfish = Fish(fish, peem)
                elif(fish.fishData.genesis == "SICK-SALMON"):
                    sfish = Fish(fish, sicksalmon)
                else:
                    sfish = Fish(fish)
                fish_list.add(sfish)
                bar_list.add(sfish.bar)
                maxBar_list.add(sfish.maxBar)

        for fish in fish_list:
            if fish.fishData.status == "dead" or fish.fishData.state == "on-migrate":
                c.pond.fishes.remove(fish.fishData)
                fish.kill()
                fish.bar.kill()
                fish.maxBar.kill()

        ourPondFishList = c.pond.fishes

        BackGround = Background('./asset/aqua.jpg')
        screen.fill(WHITE)
        screen.blit(BackGround.image, BackGround.rect)

        for fish in fish_list:
            fish.update(fish_list, bar_list, maxBar_list)

        font = pygame.font.Font(None, 24)
        TextDraw('Fish : ' + str(len(fish_list)) + '  ',
                 font, "black", SCREEN_WIDTH-70, 10).draw(screen)

        fish_list.draw(screen)
        maxBar_list.draw(screen)
        bar_list.draw(screen)

        pygame.display.flip()
        clock.tick(TPS)

    while running:
        if(len(c.pond.fishes) > len(fish_list)):
            fish_diff = len(c.pond.fishes)-(len(fish_list))
            new_list = c.pond.fishes[len(fish_list):len(c.pond.fishes)]
            for fish in new_list:
                if(fish.genesis == "PEEM"):
                    sfish = Fish(fish, peem)
                elif(fish.genesis == "SICK-SALMON"):
                    sfish = Fish(fish, sicksalmon)
                else:
                    sfish = Fish(fish)
                fish_list.add(sfish)
                bar_list.add(sfish.bar)
                maxBar_list.add(sfish.maxBar)

        for fish in fish_list:
            if fish.fishData.status == "dead" or fish.fishData.state == "on-migrate":
                c.pond.fishes.remove(fish.fishData)
                fish.kill()
                fish.bar.kill()
                fish.maxBar.kill()

        # menu = Menu.make_long_menu()
        # menu.mainloop(
        #     surface=screen,
        #     disable_loop=True,
        #     fps_limit=FPS
        # )

        # check = any( item in c.pond.fishes for item in fish_list)
        # for fish in c.pond.fishes:
        #     createdFish = Fish(fish)
        #     temp_fish_list.add(createdFish)
        #     temp_bar_list.add(createdFish.bar)
        #     temp_maxBar_list.add(createdFish.maxBar)

        # fish_list = temp_fish_list
        # bar_list = temp_bar_list
        # maxBar_list = temp_maxBar_list
        # temp_fish_list = pygame.sprite.Group()
        # temp_bar_list = pygame.sprite.Group()
        # temp_maxBar_list = pygame.sprite.Group()

        ourPondFishList = c.pond.fishes
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                running = False
            if event.type == pygame.KEYDOWN:
                openMenu()
            # if event.type == pygame.KEYUP:
            #     openGame()

        BackGround = Background('./asset/aqua.jpg')
        screen.fill(WHITE)
        screen.blit(BackGround.image, BackGround.rect)

        for fish in fish_list:
            fish.update(fish_list, bar_list, maxBar_list)

        font = pygame.font.Font(None, 24)
        TextDraw('Fish : ' + str(len(fish_list)) + '  ',
                 font, "black", SCREEN_WIDTH-70, 10).draw(screen)

        fish_list.draw(screen)
        maxBar_list.draw(screen)
        bar_list.draw(screen)

        pygame.display.flip()
        clock.tick(TPS)

    # del font,
    pygame.display.quit()
    pygame.quit()
