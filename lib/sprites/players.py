"""Player classes"""

# first-party imports
import glob
import os

# third-party imports
import pygame

# first-party imports
from .base import AffectedByGravitySprite
from .objects import Bullet
from .. import pyganim

# Path to sprites directory
SPRITES = os.path.join('images','sprites')

class Player(AffectedByGravitySprite):
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
    MAX_HEALTH = 5

    def init_animations(self, character):
        # folder containing the character images.
        p = os.path.join(SPRITES, character)
        walk_anim_files = sorted(glob.glob(os.path.join(p, 'walk-[0-9][0-9].gif')))
        
        self.walk_left_anim = pyganim.PygAnimation([(image, .1) for image in walk_anim_files])
        self.walk_right_anim = self.walk_left_anim.getCopy()
        self.walk_right_anim.flip(True, False)
        self.walk_right_anim.makeTransformsPermanent()
        self.face_left = pyganim.PygAnimation([(walk_anim_files[0], 10)])
        self.face_right = self.face_left.getCopy()
        self.face_right.flip(True, False)
        self.face_right.makeTransformsPermanent()


    def init_keys(self, keymap):
        """Set player keys based on keymap."""
        self.K_LEFT = keymap.LEFT
        self.K_RIGHT = keymap.RIGHT
        self.K_JUMP = keymap.JUMP
        self.K_SHOOT = keymap.SHOOT
        self.K_INVINCIBLE = keymap.INVINCIBLE


    def init_state(self):
        """Initialize the players state."""
        
        # True if the player is on a surface, else False.
        self.resting = False

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
        
        # hit some key to become invincible permanently.
        self.invincible = False
        
    def __init__(self, location, keymap, character, *groups):
        """Create a player object."""
        
        super().__init__(*groups)
        
        self.init_keys(keymap)
        
        self.init_state()
        
        # Vertical velocity.  This gets changed by either falling or jumping.
        self.dy = 0
        
        self.defense = 1 
        self.init_animations(character)
        
        # assign all the animations that belong to the player.
        self.animations = {self.LEFT:  {self.STILL: self.face_left,
                                        self.WALKING: self.walk_left_anim},
                           self.RIGHT: {self.STILL: self.face_right,
                                        self.WALKING: self.walk_right_anim}
                           }
        
        # the current animation that is playing
        self.current_animation = self.face_right
        
        self.image = self.face_right.getCurrentFrame()
        self.rect = pygame.rect.Rect(location, self.image.get_size())

    def try_to_jump(self, game):
        """Tries to jump."""
        if self.jump:
            if self.resting:
                self.dy = self.JUMP_SPEED
                game.jump.play()
                self.double_jumped = False
            elif self.dy > 60 and not self.double_jumped:
                self.dy = self.JUMP_SPEED
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


    def update(self, dt, game):
        
        # finds the right animation and displays it.
        self.animate()
        
        self.update_hit_timer(dt)
        # jump, shoot, whatever.
        self.do_actions(game)
        
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        new = self.move(dt, game)
        
        game.tilemap.set_focus(new.x, new.y)
        if new.x < -10 or new.y > game.tilemap.px_height:
            self.is_dead = True
        
