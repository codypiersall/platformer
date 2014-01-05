# builtins
import argparse
import os

# Third-party
import pygame

# First-party
from lib.keymap import km1, km2
from lib import tmx, menu, images 
from lib import sprites

ENEMY_MAP = {'Knight': sprites.Knight}
SCREEN_SIZE = (640, 480)

# Number of players by default.
PLAYERS = '1'

# Default map
DEFAULT_MAP = 'maps/map1.tmx'

# Path to backgrounds directory
BACKGROUNDS = os.path.join('images', 'backgrounds')
DEFAULT_BACKGROUND = 'black.bmp'

# colors
GREEN = pygame.Color(0, 200, 0)
YELLOW = pygame.Color(150, 150, 0)
RED = pygame.Color(100, 0, 0)
DARK_GREY = pygame.Color(50, 50, 50)

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
        level = settings['level']
        players = settings['players']
        character = settings['character']
        
        self.level_beaten = False
        
        self.tilemap = tmx.load(level, screen.get_size())
        try:
            background_file = self.tilemap.properties['background']
            
        except KeyError:
            background_file = DEFAULT_BACKGROUND
        
        background = images.load(os.path.join(BACKGROUNDS, background_file), convert=True, size=screen.get_size())
        
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
            
            ENEMY_MAP[enemy['enemy']]((enemy.px, enemy.py), enemy['enemy'], self.enemies)
        
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


def get_clargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--small',
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
    menu.main_menu(screen, Game)
    