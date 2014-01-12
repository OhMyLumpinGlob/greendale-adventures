# VERSION 0.1 ALPHA #

# TO-DO LIST
#- Create some levels, populate the level_data_files for those levels

# IMPORTS #
import pygame
from pygame.locals import *
import sys, os

# CLASSES #
class ControlClass:

    def __init__(self):
        self.current_level = None
        self.sprites = None
        self.player = None
        self.FPS = pygame.time.Clock()
        self.RESOURCES_DICT = self.get_resources_dict()
        self.WALKSPEED = 10

    def first_setup(self):
        self.sprites = SpriteGroupClass()
        self.player = PlayerClass(self.get_resource('player_spritesheet').strip())
        self.change_level('study_room1')

    def get_resource(self, resource_id):
        return self.RESOURCES_DICT[resource_id]

    def set_player_position(self, dest):
        self.player.set_position(dest)

    def get_terrain_group(self):
        return self.current_level.get_terrain_group()

    def add_to_sprites(self, obj):
        self.sprites.add(obj)

    def event_handler(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self.quit_game()
            elif event.key == K_UP:
                self.player.move(0,-(self.WALKSPEED),'up')
            elif event.key == K_DOWN:
                self.player.move(0,self.WALKSPEED,'down')
            elif event.key == K_LEFT:
                self.player.move(-(self.WALKSPEED),0,'left')
            elif event.key == K_RIGHT:
                self.player.move(self.WALKSPEED,0,'right')
            elif event.key == K_w:
                print self.player.get_rect().top
            elif event.key == K_s:
                print self.player.get_rect().bottom
            elif event.key == K_a:
                print self.player.get_rect().left
            elif event.key == K_d:
                print self.player.get_rect().right
            elif event.key == K_SPACE:
                collide_list = pygame.sprite.spritecollide(self.player, self.get_level_exits(), False)
                if len(collide_list) > 0:
                    self.change_level(collide_list[0].dest)
        elif event.type == pygame.QUIT:
            self.quit_game()    

    def change_level(self, new_level):
        self.current_level = Level(new_level)
        self.current_level.make_level()

    def get_level_exits(self):
        return self.current_level.get_exit_group()

    def render(self):
        self.sprites.clear(screen, self.current_level.get_background())
        self.get_terrain_group().clear(screen, self.current_level.get_background())
        self.sprites.update()
        self.get_terrain_group().draw(screen)
        self.sprites.draw(screen)
        pygame.display.flip()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def get_resources_dict(self):
        resources = {}
        with open('data/resources') as f:
            for line in f:
                line = line.split()
                resources[line[0]] = line[1]
        return resources

    def add_to_terrain_group(self,obj):
        self.current_level.TerrainGroup.add(obj)

class LevelExit(pygame.sprite.Sprite):

    def __init__(self, dest, rect):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.dest = dest

class Level:

    def __init__(self, level_name):
        self.level_name = level_name
        self.background = None
        self.TerrainGroup = SpriteGroupClass()
        self.LevelExitGroup = SpriteGroupClass()
        
    def make_level(self):
        with open('data/level_data_files/' + self.level_name, 'r') as f:
            for line in f:
                line = line.split()
                if line[0] == 'background':
                    self.background = pygame.image.load(Control.get_resource(line[1]))
                    screen.blit(self.background, (0,0))
                elif line[0] == 'terrain':
                    Terrain(line[1],(int(line[2]),int(line[3]),int(line[4]),int(line[5])), pygame.image.load(Control.get_resource(line[6])))
                elif line[0] == 'exit':
                    self.LevelExitGroup.add(LevelExit(line[1],(int(line[2]),int(line[3]),int(line[4]),int(line[5]))))
                elif line[0] == 'playerposition':
                    Control.set_player_position((int(line[1]),int(line[2])))
        

    def get_background(self):
        return self.background

    def get_terrain_group(self):
        return self.TerrainGroup

    def get_exit_group(self):
        return self.LevelExitGroup

    def get_level_name(self):
        return self.level_name
        
                    
class SpriteGroupClass(pygame.sprite.Group):

    def __init__(self):
        pygame.sprite.Group.__init__(self)

class PlayerClass(pygame.sprite.Sprite):

    def __init__(self, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.sprite_dict = self._get_sprites(spritesheet)
        self.image = self.sprite_dict['down1']
        self.rect = self.image.get_rect()
        Control.add_to_sprites(self)
        self.animate_counter = 1
        self.direc = 'down'

    def move(self,x,y,direc):
        self.rect.move_ip(x,y)
        if len(pygame.sprite.spritecollide(self, Control.get_terrain_group(), False)) > 0:
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

    def get_rect(self):
        return self.rect

class Terrain(pygame.sprite.Sprite):

    def __init__(self, name, rect, image):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.name = name
        self.image = image
        Control.add_to_terrain_group(self)

# INIT #
pygame.init() # Initialise Pygame for use
screen = pygame.display.set_mode((1366,768),DOUBLEBUF|FULLSCREEN) # Set the display surface, store as screen.
pygame.key.set_repeat(50,50) # Sets KEYDOWN events to repeat if key is held down

Control = ControlClass() # Creates the control class through which everything is accessed
Control.first_setup() # Boots up the game


# MAIN #

while 1:
    Control.FPS.tick(30) # Keeps the FPS below 30
    for event in pygame.event.get():
        Control.event_handler(event) # Process events and issues commands based on those events
    Control.render() # blits/draws everything onto the screen surface, and renders the display
