"""Player classes"""
from __future__ import division

# first-party imports
import glob
import os
import re

# third-party imports
import pygame

# first-party imports
from .base import BaseSprite
from .base import WALK_IMAGE_FILE_PATTERN, JUMP_IMAGE_FILE_PATTERN, WEAPON_FILE_PATTERN, STILL_FILE_PATTERN
from .objects import Bullet
from .. import images
from .. import pyganim

# Path to sprites directory
DEFAULT_PLAYERS = os.path.join('images','sprites', 'players')


class Player(BaseSprite):
    """
    Create a player instance.
    Args:
        location: (x,y) pixel location.  Where to place the player.
        keymap: a keymap.Keys instance specifying which keys the player uses.
        character: images to use for the player instance
                   A folder with the name character must exist in images/sprites.
                   Right now this has to be frog, since that is the only folder in
                   images/sprites.
        *groups: sprite group that the player belongs to.
    """
    # Player's left and right speed in pixels per second
    SPEED = 225

    # Player's jumping speed in pixels per second.
    JUMP_SPEED = -725

    # Player goes 1.5 times faster when running.
    RUNNING = 1.5
    # How much time passes between shots in seconds.
    COOLDOWN_TIME = 0.5

    # Player's maximum health
    MAX_HEALTH = 5


    def _get_image_files(self, character):
        """Return a tuple of the form (walk_files), (jump_files), weapon_file"""
        p = os.path.join(DEFAULT_PLAYERS, character)
        files = os.listdir(p)

        def filter_files(pattern):
            filter_function = lambda file:re.match(pattern, file)
            filtered_files = [os.path.join(p, i) for i in filter(filter_function, files)]
            return filtered_files

        walk_files = filter_files(WALK_IMAGE_FILE_PATTERN)
        jump_files = filter_files(JUMP_IMAGE_FILE_PATTERN)
        weapon_file = filter_files(WEAPON_FILE_PATTERN)[0]
        try:
            still_file = filter_files(STILL_FILE_PATTERN)[0]
        except IndexError:
            still_file = walk_files[0]

        return walk_files, jump_files, weapon_file, still_file

    def init_animations(self, character):
        # folder containing the character images.

        walk_anim_files, jump_anim_files, weapon_file, still_file = self._get_image_files(character)

        self.anim_walk_left = pyganim.PygAnimation([(image, .1) for image in walk_anim_files])
        self.anim_walk_right = pyganim.PygAnimation([(image, .1) for image in walk_anim_files], convert=False, flip=(True, False))

        self.image_face_left = images.load(still_file, convert=False)
        self.image_face_right = images.load(still_file, flip=(True, False), convert=False)

        self.anim_jump_left = pyganim.PygAnimation([(image, .1) for image in jump_anim_files])
        self.anim_jump_right = pyganim.PygAnimation([(image, .1) for image in jump_anim_files], convert=False, flip=(True,False))

        self.weapon = weapon_file

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
        self.x_multiplier = self.NOT_RUNNING

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

        super(Player, self).__init__(*groups)

        self.init_keys(keymap)

        self.init_state()

        # Vertical velocity.  This gets changed by either falling or jumping.
        self.dy = 0

        self.defense = 1
        self.init_animations(character)

        # assign all the ground_images that belong to the player.
        self.ground_images = {
                self.LEFT:
                    {self.STILL: self.image_face_left,
                     self.WALKING: self.anim_walk_left},

                 self.RIGHT:
                    {self.STILL: self.image_face_right,
                    self.WALKING: self.anim_walk_right}
                 }

        self.jump_images = {
                self.LEFT: self.anim_jump_left,
                self.RIGHT: self.anim_jump_right}

        # the current animation that is playing
        self.current_animation = self.anim_walk_left

        self.image = self.image_face_right
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
                Bullet(self.rect.center, self.direction, self.weapon, game.sprites)
                self.gun_cooldown = self.COOLDOWN_TIME
            self.shoot = False

    def do_actions(self, game):
        self.try_to_jump(game)
        self.try_to_shoot(game)

    def set_image(self):
        """Sets the appropriate image to self.image based on the player's state."""

        # if the player is shooting, the shooting animation should always play.
        # unfortunately, the player has no shooting method yet.

        # if the player is jumping, we can set the image to jump.
        if not self.resting:
            new = self.jump_images[self.direction]

        else:
            new = self.ground_images[self.direction][self.moving]

        # if the correct animation is already playing, we just need to
        # get the current frame.
        if new == self.current_animation:
            self.image = new.getCurrentFrame()
            return

        # We want to catch the Exception for when self.current_animation == None
        try:
            self.current_animation.stop()

        except AttributeError:
            pass

        # this will fail if it is a static image
        try:
            new.play()
            self.current_animation = new
            self.image = new.getCurrentFrame()

        except AttributeError:
            self.image = new
            self.current_animation = None

    def update(self, dt, game):

        # finds the right animation and displays it.
        self.set_image()

        self.update_hit_timer(dt)
        # jump, shoot, whatever.
        self.do_actions(game)

        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        new = self.move(dt, game)

        game.tilemap.set_focus(new.x, new.y)
        if new.x < -10 or new.y > game.tilemap.px_height:
            self.is_dead = True

