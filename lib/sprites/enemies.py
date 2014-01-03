"""Enemy classes"""

import os
import glob
# third-party imports
import pygame

# first-party imports
from .base import BaseSprite
from .. import pyganim
ENEMIES = os.path.join('images', 'sprites', 'enemies')

class Knight(BaseSprite):
    """This sprite just walks until it hits a blocker or a reverser, then turns around."""
    SPEED = 100
    attack = 1
    REVERSED_BY_BLOCKERS = True

    
    def init_animations(self, enemy):
        print(os.path.join(ENEMIES, enemy,'walk-[0-9][0-9].gif'))
        images = sorted(glob.glob(os.path.join(ENEMIES, enemy, 'walk-[0-9][0-9].gif')))
        print(images)
        self.anim_walk_left = pyganim.PygAnimation([(image, .2) for image in images])
        
        self.anim_walk_right = self.anim_walk_left.getCopy()
        self.anim_walk_right.flip(True, False)
        self.anim_walk_right.makeTransformsPermanent()
        self.image = self.anim_walk_left.getCurrentFrame()
    
    def __init__(self, location, enemy, *groups):
        super().__init__(*groups)
        self.init_animations(enemy)
        self.x_multiplier = 1
        self.direction = self.RIGHT
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        
    def set_image(self):
        if self.direction == self.LEFT:
            self.anim_walk_left.play()
            self.image = self.anim_walk_left.getCurrentFrame()
            self.anim_walk_right.stop()
        elif self.direction == self.RIGHT:
            self.anim_walk_right.play()
            self.image = self.anim_walk_right.getCurrentFrame()
            self.anim_walk_left.stop()
                
    def update(self, dt, game):
        self.move(dt, game)
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        
        self.set_image()
        
        # kill any player the enemy collides with.
        for player in game.players:
            if not player.invincible and self.rect.colliderect(player.rect):
                self.hit(player)

