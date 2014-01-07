import pygame

import re

SUPPORTED_IMAGE_FORMATS = '(gif)|(png)'
WALK_IMAGE_FILE_PATTERN = re.compile('walk-[0-9][0-9].' + SUPPORTED_IMAGE_FORMATS)
JUMP_IMAGE_FILE_PATTERN = re.compile('jump-[0-9][0-9].' + SUPPORTED_IMAGE_FORMATS)
WEAPON_FILE_PATTERN = re.compile('weapon.' + SUPPORTED_IMAGE_FORMATS)

class BaseSprite(pygame.sprite.Sprite):
    """Sprite class from which all other sprites in the game inherit."""
    RIGHT = 1
    LEFT= -1
    
    # moving constants
    STILL = 0
    WALKING = 1
    RUNNING = 1
    NOT_RUNNING = 1.0
    # 1 second of invincibility after been hit.
    BEEN_HIT_TIME = 1
    
    # These three constants affect how the sprite moves.
    AFFECTED_BY_GRAVITY = True
    AFFECTED_BY_BLOCKERS = True
    REVERSED_BY_BLOCKERS = False
    
    MAX_FALL_SPEED = 600
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moving = self.WALKING
        self.direction = self.RIGHT
        self.is_dead = False
        self.been_hit = False
        self.dy = 0
        self.x_multiplier = 1
        
    def hit(self, other):
        """ This is a lame, unsophisticated way to do attacks."""
        if other.been_hit <= 0:
            other.health -= self.attack / other.defense
            other.been_hit = self.BEEN_HIT_TIME
            if other.health <= 0:
                other.is_dead = True
        
    def update_hit_timer(self, dt):
        self.been_hit = max(self.been_hit - dt, 0)

    def react_to_gravity(self, dt, game):
        """Adjust y direction and position based on game's gravity."""
        self.dy = min(self.MAX_FALL_SPEED, self.dy + game.GRAVITY * dt)
        self.rect.y += self.dy * dt


    def react_to_blockers(self, dt, game, last_position, new):
        """React to any blockers that are nearby."""
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last_position.right <= cell.left and new.right > cell.left:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.right = cell.left
                    if self.REVERSED_BY_BLOCKERS:
                        self.direction *=-1
            if 'r' in blockers and last_position.left >= cell.right and new.left < cell.right:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.left = cell.right
                    if self.REVERSED_BY_BLOCKERS:
                        self.direction *=-1
            if 't' in blockers and last_position.bottom <= cell.top and new.bottom > cell.top:
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    self.resting = True
                    self.double_jumped = False
                    new.bottom = cell.top
                    if self.AFFECTED_BY_GRAVITY:
                        self.dy = game.GRAVITY * dt 
            if 'b' in blockers and last_position.top >= cell.bottom and new.top < cell.bottom:
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    new.top = cell.bottom
                    if self.AFFECTED_BY_GRAVITY:
                        self.dy = 0


    def move_x(self, dt):
        """Move in the x direction."""
        return self.direction * self.SPEED * self.moving * self.x_multiplier * dt

    def move(self, dt, game):
        """Movement and collision stuff"""
        last_position = self.rect.copy()
        if self.AFFECTED_BY_GRAVITY:
            self.react_to_gravity(dt, game)
        
        self.rect.x += int(self.move_x(dt))
        
        new = self.rect
        self.resting = False
        if self.AFFECTED_BY_BLOCKERS:
            self.react_to_blockers(dt, game, last_position, new)
        
        return new