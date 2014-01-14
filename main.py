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
        self.overlay = None
        self.FPS = pygame.time.Clock()
        self.RESOURCES_DICT = self.get_resources_dict()
        self.WALKSPEED = 10
        self.over_player_group = None
        self.UID_EXCLUSIONS = []

    def first_setup(self):
        self.sprites = SpriteGroupClass()
        self.over_player_group = SpriteGroupClass()
        self.player = PlayerClass(self.get_resource('player_spritesheet').strip())
        self.change_level('study_room1','down')
        self.overlay = Overlay()

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
                collide_list = pygame.sprite.spritecollide(self.player, self.get_level_objects(), False)
                if len(collide_list) > 0:
                    collide_list[0].interact()
            elif event.key == K_i:
                print self.player.get_inventory()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for obj in self.overlay.objects:
                    if event.pos[0] > obj.rect.left and event.pos[0] < obj.rect.right and event.pos[1] > obj.rect.top and event.pos[1] < obj.rect.bottom:
                        obj.clicked()
        elif event.type == pygame.QUIT:
            self.quit_game()    

    def change_level(self, new_level, direc):
        if self.current_level != None:
            prev_level = self.current_level.level_name
        else:
            prev_level = 'default'
        self.current_level = Level(new_level)
        self.current_level.make_level(prev_level)
        self.player.direc = direc

    def get_level_objects(self):
        return self.current_level.get_interactive_objects()
    
    def get_level_exits(self):
        return self.current_level.get_exit_group()

    def render(self):
        self.sprites.clear(screen, self.current_level.get_background())
        self.get_terrain_group().clear(screen, self.current_level.get_background())
        self.over_player_group.clear(screen, self.current_level.get_background())
        self.current_level.DrawnObjectGroup.clear(screen, self.current_level.get_background())
        self.depth_getter()
        self.sprites.update()
        self.overlay.objects.update()
        self.remove_from_terrain_group(self.over_player_group.sprites())
        self.get_terrain_group().draw(screen)
        self.current_level.DrawnObjectGroup.draw(screen)
        self.sprites.draw(screen)
        self.over_player_group.draw(screen)
        self.overlay.objects.draw(screen)
        self.add_to_terrain_group(self.over_player_group.sprites())
        self.over_player_group.empty()
        pygame.display.flip()

    def depth_getter(self):
        for sprite in self.get_terrain_group().sprites():
            if sprite.rect.bottom > self.player.rect.bottom:
                self.over_player_group.add(sprite)
    
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
        self.get_terrain_group().add(obj)

    def remove_from_terrain_group(self, objlist):
        self.get_terrain_group().remove(objlist)

class Overlay:

    def __init__(self):
        self.objects = SpriteGroupClass()
        with open('data/overlay') as f:
            for line in f:
                line = line.split()
                if line[0] == 'invslot':
                    self.objects.add(InvSlot((int(line[1]),int(line[2]),int(line[3]),int(line[4])),int(line[5])))
            

class InteractiveObject(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.type = 'undefined'

    def interact(self):
        if self.type == 'undefined':
            print 'Object type undefined'
        elif self.type == 'exit':
            self.use_exit()
        elif self.type == 'pickup':
            self.pick_up_object()

    def use_exit(self):
        Control.change_level(self.dest,self.direc)

    def pick_up_object(self):
        Control.player.add_to_inventory(self)

class LevelExit(InteractiveObject):

    def __init__(self, dest, rect, direc):
        InteractiveObject.__init__(self)
        self.rect = rect
        self.dest = dest
        self.direc = direc
        self.type = 'exit'

class Pickup(InteractiveObject):

    def __init__(self, name, image, pos, UID):
        InteractiveObject.__init__(self)
        self.name = name
        self.type = 'pickup'
        self.image = image
        self.rect = image.get_rect(left=pos[0],top=pos[1])
        self.icon = pygame.transform.scale(self.image, (50,50))
        self.UID = UID


class Level:

    def __init__(self, level_name):
        self.level_name = level_name
        self.background = None
        self.TerrainGroup = SpriteGroupClass()
        self.LevelExitGroup = SpriteGroupClass()
        self.InteractiveObjectGroup = SpriteGroupClass()
        self.DrawnObjectGroup = SpriteGroupClass()
        
    def make_level(self,prev_level):
        with open('data/level_data_files/' + self.level_name, 'r') as f:
            for line in f:
                line = line.split()
                if line[0] == 'background':
                    self.background = pygame.image.load(Control.get_resource(line[1]))
                    screen.blit(self.background, (0,0))
                elif line[0] == 'terrain':
                    self.TerrainGroup.add(Terrain(line[1],(int(line[2]),int(line[3]),int(line[4]),int(line[5])), pygame.image.load(Control.get_resource(line[6])),int(line[7])))
                elif line[0] == 'exit':
                    self.InteractiveObjectGroup.add(LevelExit(line[1],(int(line[2]),int(line[3]),int(line[4]),int(line[5])),line[6]))
                elif line[0] == 'playerposition':
                    if line[1] == prev_level:
                        Control.set_player_position((int(line[2]),int(line[3])))
                elif line[0] == 'pickup':
                    if line[4] not in Control.UID_EXCLUSIONS:
                        temp_object = Pickup(line[1],pygame.image.load(Control.get_resource(line[1])),(int(line[2]),int(line[3])),line[4])
                        self.InteractiveObjectGroup.add(temp_object)
                        self.DrawnObjectGroup.add(temp_object)
        
    def get_interactive_objects(self):
        return self.InteractiveObjectGroup

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
        self.inventory = [None]*20

    def move(self,x,y,direc):
        self.rect.move_ip(x,y)
        if self.check_collision():
            self.rect.move_ip(-x,-y)
        if direc == self.direc:
            self.animate_counter += 1
            if self.animate_counter > 3:
                self.animate_counter = 2
        else:
            self.direc = direc
            self.animate_counter = 1

    def check_collision(self):
        for sprite in pygame.sprite.spritecollide(self, Control.get_terrain_group(), False):
            if self.get_rect().bottom > sprite.rect.top + sprite.mask_y_offset:
                return True
        return False

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

    def add_to_inventory(self, obj):
        if self.inventory.count(None) > 0:
            self.inventory[self.inventory.index(None)] = obj
            Control.current_level.DrawnObjectGroup.remove(obj)
            Control.current_level.InteractiveObjectGroup.remove(obj)
            Control.UID_EXCLUSIONS.append(obj.UID)
        else:
            print 'Inventory Full'

    def get_inventory(self):
        return self.inventory

class InvSlot(pygame.sprite.Sprite):

    def __init__(self, rect, slot):
        pygame.sprite.Sprite.__init__(self)
        self.empty_image = pygame.image.load(Control.get_resource('inv_slot'))
        self.image = self.empty_image
        self.rect = Rect(rect)
        self.contained = None
        self.slot = slot
        self.type = 'invslot'

    def assign(self,obj):
        self.image = pygame.transform.scale(obj.image, (50,50))
        self.contained = obj

    def empty(self):
        self.image = self.empty_image

    def update(self):
        if Control.player.get_inventory()[self.slot] != self.contained:
            self.assign(Control.player.get_inventory()[self.slot])

    def clicked(self):
        print 'clicked slot ' + str(self.slot)

class Terrain(pygame.sprite.Sprite):

    def __init__(self, name, rect, image, mask_y_offset):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.name = name
        self.image = image
        self.mask_y_offset = mask_y_offset
        

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
