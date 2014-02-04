# Copyright 2014 Cody Piersall

"""
This is a platformer game.  It's still a work in progress, you know?
"""

# builtins
import argparse
import configparser
import os

# Third-party
import pygame

# First-party
from lib.keymap import km1, km2
from lib import tmx, menu, images 
from lib import sprites

__author__ = 'Cody Piersall'

# screen size when '--small' option is passed via command line.s
SCREEN_SIZE = (640, 480)

# Paths to maps directory
MAPS_DIRECTORY = 'maps'
CHARACTERS_DIRECTORY = os.path.join('images', 'sprites', 'players')

# Path to backgrounds directory
BACKGROUNDS_DIRECTORY = os.path.join('images', 'backgrounds')
DEFAULT_BACKGROUND = 'black.bmp'


# Fallback defaults for when no .gameconfig file is available
DEFAULT_PLAYERS = '1'
DEFAULT_MAP = 'map1.tmx'
DEFAULT_CHARACTER = 'frog'

# colors
GREEN = pygame.Color(0, 200, 0)
YELLOW = pygame.Color(150, 150, 0)
RED = pygame.Color(100, 0, 0)
DARK_GREY = pygame.Color(50, 50, 50)

SETTINGS_FILE = '.gameconfig'
class Game():
    GRAVITY = 2000
    FPS = 60
    LIFEBAR_LENGTH = 250
    LIFEBAR_WIDTH = 10
    
    
    def change_state(self, key, event):
        """Change game's states based on player input"""
        if event.type == pygame.KEYDOWN:
            for player in self.players:
                if event.key == player.K_LEFT:
                    player.moving = player.WALKING
                    player.direction = player.LEFT
                elif event.key == player.K_RIGHT:
                    player.moving = player.WALKING
                    player.direction = player.RIGHT
                elif event.key == player.K_JUMP:
                    player.jump = True
                elif event.key == player.K_SHOOT:
                    player.x_multiplier = player.RUNNING
                    player.shoot = True
                elif event.key == player.K_INVINCIBLE:
                    player.invincible = not player.invincible
        
        elif event.type == pygame.KEYUP:
            for player in self.players:
                if event.key == player.K_LEFT:
                    if key[player.K_RIGHT]:
                        player.moving = player.WALKING
                        player.direction = player.RIGHT
                    else:
                        player.moving = player.STILL
                elif event.key == player.K_RIGHT:
                    if key[player.K_LEFT]:
                        player.moving = player.WALKING
                        player.direction = player.LEFT
                    else:
                        player.moving = player.STILL
                elif event.key == player.K_SHOOT:
                    player.x_multiplier = player.NOT_RUNNING

    def main(self, screen, settings):
        """ 
        Start the game by passing it the screen and settings dict.
        settings has to have these keys:
            level: the level to start.
            players: the number of players.
            character: the selected character.
            
        """
        
        level = settings['level']
        players = settings['players']
        character = settings['character']
        
        self.level_beaten = False
        self.tilemap = tmx.load(os.path.join(MAPS_DIRECTORY,level), screen.get_size())
        try:
            background_file = self.tilemap.properties['background']
            
        except KeyError:
            background_file = DEFAULT_BACKGROUND
        
        background = images.load(os.path.join(BACKGROUNDS_DIRECTORY, background_file), convert=True, size=screen.get_size())
        
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        
        self.players = []
        
        self.players.append(sprites.Player((start_cell.px, start_cell.py), km1, character, self.sprites))
        if players == 2:    
            self.players.append(sprites.Player((start_cell.px, start_cell.py), km2, character, self.sprites))
 
        self.tilemap.layers.append(self.sprites)
        
        # sound effects
        self.jump = pygame.mixer.Sound('sounds/jump.wav')
        self.shoot = pygame.mixer.Sound('sounds/shoot.wav')
        self.explosion = pygame.mixer.Sound('sounds/explosion.wav')
        
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            
            sprites.Enemy((enemy.px, enemy.py), enemy['enemy'], self.enemies)
        
        self.tilemap.layers.append(self.enemies)
        
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(self.FPS) / 1000
            key = pygame.key.get_pressed()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    return
                
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        return
                        
                else:
                    self.change_state(key, event)

            screen.blit(background, (0,0))
            self.tilemap.update(dt, self)
            self.tilemap.draw(screen)
            for offset, player in enumerate(self.players):
                self.draw_lifebar(screen, player.health, player.MAX_HEALTH, offset)
                if player.is_dead:
                    return
            pygame.display.flip()
            
            # this is how you beat the level.
            try:
                if self.tilemap.properties['type'] == 'exit':
                    for player in self.players:
                        if self.tilemap.layers['triggers'].collide(player.rect, 'exit'):
                            self.level_beaten = True
                        
            except KeyError:
                pass
            # level finished.  better do something better.
            if self.level_beaten: 
                self.beat_level(screen, clock)
                return
            
    def beat_level(self, screen, clock):
        font = pygame.font.Font(None, 150)
        label = font.render('You win!!!', 1, (255,0,0))
        
        time_passed = 0
        dt = clock.tick() / 1000
 
        while time_passed < 0.5:
            dt = clock.tick() / 1000                
            screen.blit(label, (100,100))
            time_passed += dt
            
            pygame.display.flip()
            
    def draw_lifebar(self, screen, health, max_health, offset):
        # outline for lifebar
        pygame.draw.rect(screen, DARK_GREY, (10,10 + offset*25, self.LIFEBAR_LENGTH, 20))
        
        ratio = health / max_health
        if ratio < 0.15:
            color = RED
        elif ratio < .7:
            color = YELLOW
        else:
            color = GREEN
        
        length = (self.LIFEBAR_LENGTH - 3) * health/max_health 
        pygame.draw.rect(screen, color, (12,12 + offset*25, (length), 16))


def main_menu(screen, Game, default_settings,
              font='coders_crux.ttf'):
    
    font = pygame.font.Font(font, 32)
    main_menu = menu.Menu(screen, 'Start Options Quit'.split(), font=font, settings=default_settings)
    main_menu.add_start_action(0, Game)
    main_menu.add_back_action(-1)

    options_menu = main_menu.add_submenu(1,['Levels', 'Number of Players', 'Character Select', 'Back'])
    options_menu.add_back_action(-1)
    
    levels = [i for i in os.listdir(MAPS_DIRECTORY) if i.endswith('.tmx')]
    level_items = [os.path.splitext(l)[0] for l in levels] + ['Back']
    levels_menu = options_menu.add_submenu(0, level_items)
    levels_menu.add_back_action(-1)
    [levels_menu.change_settings(i, 'level', os.path.join(MAPS_DIRECTORY, levels[i])) for i in range(len(levels))]
    
    players_menu = options_menu.add_submenu(1, [1, 2, 'Back'])
    players_menu.add_back_action(-1)
    [players_menu.change_settings(i, 'players', i+1) for i in range(2)]
    
    characters = os.listdir(CHARACTERS_DIRECTORY)
    character_items = characters + ['Back']
    character_select_menu = options_menu.add_submenu(2, character_items)
    [character_select_menu.change_settings(i, 'character', character_items[i]) for i in range(len(characters))]
    character_select_menu.add_back_action(-1)
    
    try:
        main_menu.mainloop()
    except menu.Exit:
        pygame.quit()
            
def get_settings():
    """
    Read in settings from .config file; otherwise, use constants
    defined at the top of this module.
    """
    
    settings = {'level': DEFAULT_MAP,
                'character': DEFAULT_CHARACTER,
                'players': DEFAULT_PLAYERS}
    
    parser = configparser.ConfigParser()
    try:
        with open(SETTINGS_FILE) as fr:
            parser.read_file(fr)
            
        settings.update(parser['settings'])
        settings['players'] = int(settings['players'])
    except FileExistsError:
        print('The file {} does not exist'.format())
        
    return settings
    
    
def get_clargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--small',
                        help="Use a smaller screen.",
                        action='store_true',
                        default=False)
    
    parser.add_argument('-i', '--invincible',
                        help="Start off invincible.",
                        action='store_true',
                        default=False)
    
    return parser.parse_args()

if __name__ == '__main__':
    pygame.init()
    args = get_clargs()
    
    if args.small:
        screen = pygame.display.set_mode(SCREEN_SIZE)
    else:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    
    settings = get_settings()
    
    main_menu(screen, Game, settings)
    