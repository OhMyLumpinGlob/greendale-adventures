# VERSION 0.1 ALPHA #

# IMPORTS #
import pygame
from pygame.locals import *
import sys, os

# FUNCTIONS #
def quit_game():
    pygame.quit()
    sys.exit()

def build_level(level):
    if level == 'study_room1':
        background = pygame.image.load(RESOURCES_DICT['study_room'])
        table = Terrain((591,202,271,301))
    else:
        print 'ERROR, LEVEL ' + level + ' NOT FOUND'
        quit_game()
    return background

def event_handler(event):
    if event.type == pygame.KEYDOWN:
        if event.key == K_ESCAPE:
            quit_game()
        elif event.key == K_UP:
            player.move(0,-WALKSPEED,'up')
        elif event.key == K_DOWN:
            player.move(0,WALKSPEED,'down')
        elif event.key == K_LEFT:
            player.move(-WALKSPEED,0,'left')
        elif event.key == K_RIGHT:
            player.move(WALKSPEED,0,'right')
        elif event.key == K_w:
            print player.rect.top
        elif event.key == K_s:
            print player.rect.bottom
        elif event.key == K_a:
            print player.rect.left
        elif event.key == K_d:
            print player.rect.right
    elif event.type == pygame.QUIT:
        quit_game()

def get_resources_dict():
    resources = {}
    with open('data/resources') as f:
        for line in f:
            line = line.split()
            resources[line[0]] = line[1]
    return resources
    

# CLASSES #
class Level:

    def __init__(self, level_name):
        self.level_name = level_name
        self.background = None
        
        self.make_level()
        

    def make_level(self):
        with open('data/level_data_files/' + self.level_name, 'r') as f:
            for line in f:
                line = line.split()
                if line[0] == 'background':
                    self.background = pygame.image.load(RESOURCES_DICT[line[1]])
                elif line[0] == 'terrain':
                    Terrain(line[1],(int(line[2]),int(line[3]),int(line[4]),int(line[5])))
        
                    

class SpriteGroupClass(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class PlayerClass(pygame.sprite.Sprite):

    def __init__(self, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_dict = self._get_sprites(spritesheet)
        self.image = self.sprite_dict['down1']
        self.rect = self.image.get_rect()
        sprites.add(self)
        self.animate_counter = 1
        self.direc = 'down'

    def move(self,x,y,direc):
        self.rect.move_ip(x,y)
        if len(pygame.sprite.spritecollide(player, TerrainGroup, False)) > 0:
            self.rect.move_ip(-x,-y)
        if direc == self.direc:
            self.animate_counter += 1
            if self.animate_counter > 3:
                self.animate_counter = 2
        else:
            self.direc = direc
            self.animate_counter = 1

    def set_position(self, dest):
        self.rect.x = dest[0]
        self.rect.y = dest[1]

    def _get_sprites(self, spritesheet):
        _dict = {}
        sprites = pygame.image.load(spritesheet)
        with open('data/player_spritesheet_data') as f:
            for line in f:
                line = line.split()
                ### QUICKFIX -- SCALED IMAGE UP, REMOVE WHEN FINAL ART IS READY ###
                img = sprites.subsurface((int(line[1]),int(line[2]),int(line[3]),int(line[4])))
                _dict[line[0]] = pygame.transform.scale(img, (int(img.get_width()*1.5),int(img.get_height()*1.5)))
        return _dict

    def update(self):
        self.image = self.sprite_dict[self.direc+str(self.animate_counter)]

class Terrain(pygame.sprite.Sprite):

    def __init__(self, name, rect):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.name = name
        TerrainGroup.add(self)

# INIT #
pygame.init()
screen = pygame.display.set_mode((1366,768),DOUBLEBUF|FULLSCREEN)
pygame.key.set_repeat(50,50)

# GLOBALS
FPS = pygame.time.Clock()
RESOURCES_DICT = get_resources_dict()
WALKSPEED = 10

# MAIN #
sprites = SpriteGroupClass()
TerrainGroup = SpriteGroupClass()
player = PlayerClass(RESOURCES_DICT['player_spritesheet'].strip())
player.set_position((487,375))
#background = build_level('study_room1')
current_level = Level('study_room1')
background = current_level.background
screen.blit(background, (0,0))

while 1:
    FPS.tick(30)
    for event in pygame.event.get():
        event_handler(event)
    sprites.clear(screen, background)
    sprites.update()
    sprites.draw(screen)
    pygame.display.flip()
