# builtins
import glob
from os import path

# Third-party
import pygame

# First-party
from lib.keymap import km1, km2
from lib import tmx
from lib import pyganim
from lib import menu

SCREEN_SIZE = (640, 480)

# Number of players by default.
PLAYERS = '1'

# Default map
DEFAULT_MAP = 'maps/map1.tmx'

# Path to backgrounds directory
BACKGROUNDS = path.join('images', 'backgrounds')
DEFAULT_BACKGROUND = 'black.bmp'

# Path to sprites directory
SPRITES = path.join('images','sprites')

# colors
GREEN = pygame.Color(0, 200, 0)
YELLOW = pygame.Color(150, 150, 0)
RED = pygame.Color(100, 0, 0)
DARK_GREY = pygame.Color(50, 50, 50)

class Bullet(pygame.sprite.Sprite):
    image = pygame.image.load('images/sprites/frog/Masamune.gif')
    image_right = pygame.transform.rotate(image, 270)
    image_left = pygame.transform.flip(image_right, True, False)
    SPEED = 500
    # lifespan of bullet in seconds
    LIFESPAN = 1
    LEFT = -1
    RIGHT = 1
    def __init__(self, location, direction, *groups):
        super().__init__(*groups)
        if direction == self.RIGHT:
            self.image = self.image_right
            self.rect = pygame.rect.Rect(location, self.image.get_size())
        else:
            self.image = self.image_left
            x_ = self.image.get_size()[0]
            self.rect = pygame.rect.Rect((location[0] - x_, location[1]), self.image.get_size())
        self.direction = direction
        self.lifespan = self.LIFESPAN
        
    def update(self, dt, game):
        self.lifespan -= dt
        if self.lifespan < 0:
            self.kill()
            return
        self.rect.x += self.direction * self.SPEED * dt
        
        # get all collided sprites, to kill only the nearest one.
        collided = pygame.sprite.spritecollide(self, game.enemies, False)
        if collided:
            self.kill_nearest(collided)
            self.kill()
                
    def kill_nearest(self, sprites):
        """Kill the nearest sprite in sprites."""
        sprites = sorted(sprites, key=lambda s: s.rect.x)
        if self.direction == self.RIGHT:
            sprites[0].kill()
        else:
            sprites[-1].kill()
            
            
class Enemy(pygame.sprite.Sprite):
    SPEED = 100
    image_left = pygame.image.load('images/sprites/enemies/Sentry-left.gif')
    image = image_left
    image_right = pygame.transform.flip(image_left, True, False)
    
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1
        
    def update(self, dt, game):
        self.rect.x += int(self.direction * self.SPEED * dt)
        
        if self.direction > 0:
            self.image = self.image_right
        else:
            self.image = self.image_left
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        for player in game.players:
            if not player.invincible and self.rect.colliderect(player.rect):
                player.health -= dt
                if player.health < 0:
                    player.is_dead = True

class Player(pygame.sprite.Sprite):
    """
    Create a player instance.
    Args:
        location: (x,y) pixel location.  Where to place the player.
        keymap: a keymap.Keys instance specifying which keys the player uses.
        character: images to use for the player instance.  As long.
                   A folder with the name character must exist in images/sprites.
                   Right now this has to be frog, since that is the only folder in
                   images/sprites.
        *groups: sprite group that the player belongs to.
    """
    # Player's left and right speed in pixels per second
    SPEED = 200

    # Player's jumping speed in pixels per second.
    JUMP_SPEED = -700
    
    # How much time passes between shots in seconds.
    COOLDOWN_TIME = 0.5
    
    # Player's maximum health
    MAX_HEALTH = 2
    
    # Directions
    LEFT = -1
    RIGHT = 1
    
    # moving constants
    STILL = 0
    WALKING = 1
    RUNNING = 1.5
    NOT_RUNNING = 1.0

    def init_animations(self, character):
        # folder containing the character images.
        p = path.join(SPRITES, character)
        walk_anim_files = sorted(glob.glob(path.join(p, 'walk-[0-9][0-9].gif')))
        
        self.walk_left_anim = pyganim.PygAnimation([(image, .1) for image in walk_anim_files])
        self.walk_right_anim = self.walk_left_anim.getCopy()
        self.walk_right_anim.flip(True, False)
        self.walk_right_anim.makeTransformsPermanent()
        self.face_left = pyganim.PygAnimation([(walk_anim_files[0], 10)])
        self.face_right = self.face_left.getCopy()
        self.face_right.flip(True, False)
        self.face_right.makeTransformsPermanent()

    def __init__(self, location, keymap, character, *groups):
        """Create a player object.
            :args: """
        super().__init__(*groups)
        
        self.K_LEFT = keymap.LEFT
        self.K_RIGHT = keymap.RIGHT
        self.K_JUMP = keymap.JUMP
        self.K_SHOOT = keymap.SHOOT
        self.K_INVINCIBLE = keymap.INVINCIBLE
        # True if the player is on a surface, else False.
        self.resting = False
        
        # Set to True only when player dies.
        self.is_dead = False
        
        # gun_cooldown is the time left before the player can shoot again.
        self.gun_cooldown = 0
        
        # Whether the player has used the double jump.
        self.double_jumped = False
        
        # player's health; currently, it goes down based on how long 
        # the player collides with the enemy.
        self.health = self.MAX_HEALTH
        
        # self.direction and self.moving are for determining which way
        # the player is facing (either self.LEFT or self.RIGHT) and
        # whether the player is moving (either self.STILL or self.WALK)
        self.direction = self.RIGHT
        self.moving = self.STILL
        self.running = self.NOT_RUNNING
        
        # Whether the character should try to jump.  This gets set to True
        # when the player hits the jump button (default space) but does not 
        # necessarily mean the player can actually jump.
        self.jump = False
        
        # whether the player should try to shoot.
        self.shoot = False
        
        # hit some key to become invincible.
        self.invincible = False
        
        # Vertical velocity.  This gets changed by either falling or jumping.
        self.dy = 0
        
        self.init_animations(character)
        
        # assign all the animations that belong to the player.
        self.animations = {self.LEFT:  {self.STILL: self.face_left,
                                        self.WALKING: self.walk_left_anim},
                           self.RIGHT: {self.STILL: self.face_right,
                                        self.WALKING: self.walk_right_anim}
                           }
        
        # the current animation that is playing
        self.current_animation = self.face_right
        
        # TODO: Find out what is actually displaying the image.
        # I think the image gets blitted by the tmx module?
        self.image = self.face_right.getCurrentFrame()
        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def animate(self):
        """Animate the player based on direction and movement.
           
        If the animation that should be playing is already playing, this basically does nothing."""
        last_anim = self.current_animation
        next_anim = self.animations[self.direction][self.moving]
        if next_anim != last_anim:
            last_anim.stop()
            next_anim.play()
            self.current_animation = next_anim

        self.image = next_anim.getCurrentFrame()



    def try_to_jump(self, game):
        """Tries to jump."""
        if self.jump:
            if self.resting:
                self.dy = self.JUMP_SPEED * self.running
                game.jump.play()
                self.double_jumped = False
            elif self.dy > 60 and not self.double_jumped:
                self.dy = self.JUMP_SPEED * self.running
                self.double_jumped = True
                game.jump.play()
            self.jump = False


    def try_to_shoot(self, game):
        """Tries to shoot."""
        if self.shoot:
            if not self.gun_cooldown:
                game.shoot.play()
                Bullet(self.rect.center, self.direction, game.sprites)
                self.gun_cooldown = self.COOLDOWN_TIME
            self.shoot = False

    def do_actions(self, game):
        self.try_to_jump(game)
        self.try_to_shoot(game)


    def move(self, dt, game):
        """Movement and collision stuff"""
        last_position = self.rect.copy()
        self.rect.x += int(self.direction * self.SPEED * self.moving * self.running * dt)
        self.dy = min(game.MAX_FALL_SPEED, self.dy + game.GRAVITY * dt)
        self.rect.y += self.dy * dt
        new = self.rect
        self.resting = False
    
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last_position.right <= cell.left and new.right > cell.left:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.right = cell.left
            if 'r' in blockers and last_position.left >= cell.right and new.left < cell.right:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.left = cell.right
            if 't' in blockers and last_position.bottom <= cell.top and new.bottom > cell.top:
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    self.resting = True
                    self.double_jumped = False
                    new.bottom = cell.top
                    self.dy = game.GRAVITY * dt
            if 'b' in blockers and last_position.top >= cell.bottom and new.top < cell.bottom: 
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    new.top = cell.bottom
                    self.dy = 0
        
        return new

    def update(self, dt, game):
        
        # finds the right animation and displays it.
        self.animate()
        
        # jump, shoot, whatever.
        self.do_actions(game)
        
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        new = self.move(dt, game)
        
        game.tilemap.set_focus(new.x, new.y)
        if new.x < -10 or new.y > game.tilemap.px_height:
            self.is_dead = True

        
class Game():
    GRAVITY = 2000
    MAX_FALL_SPEED = 600
    FPS = 60
    LIFEBAR_LENGTH = 250
    LIFEBAR_WIDTH = 10
    
    
    def main(self, screen, level, players):
        self.level_beaten = False
        clock = pygame.time.Clock()
        
        
        self.tilemap = tmx.load(level, screen.get_size())
        try:
            background_file = self.tilemap.properties['background']
            
        except KeyError:
            background_file = DEFAULT_BACKGROUND
        
        background = pygame.image.load(path.join(BACKGROUNDS, background_file))
        background = pygame.transform.scale(background, SCREEN_SIZE)
        
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        
        self.players = []
        
        self.players.append(Player((start_cell.px, start_cell.py), km1, 'frog', self.sprites))
        if players == '2':    
            self.players.append(Player((start_cell.px, start_cell.py), km2, 'frog', self.sprites))
 
        self.tilemap.layers.append(self.sprites)
        
        # sound effects
        self.jump = pygame.mixer.Sound('sounds/jump.wav')
        self.shoot = pygame.mixer.Sound('sounds/shoot.wav')
        self.explosion = pygame.mixer.Sound('sounds/explosion.wav')
        
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        
        self.tilemap.layers.append(self.enemies)
        
        while True:
            dt = clock.tick(self.FPS) / 1000
            key = pygame.key.get_pressed()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    return
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                        
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
                            player.running = player.RUNNING
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
                            player.running = player.NOT_RUNNING

            
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

        
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    menu.main_menu(screen, Game, DEFAULT_MAP, PLAYERS)
    