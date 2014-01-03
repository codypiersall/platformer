"""Enemy classes"""

# third-party imports
import pygame

# first-party imports
from .base import BaseSprite
from .. import images

class Knight(BaseSprite):
    """This sprite just walks until it hits a blocker or a reverser, then turns around."""
    SPEED = 100
    attack = 1
    REVERSED_BY_BLOCKERS = True
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.x_multiplier = 1
        self.direction = self.RIGHT
        image_path = 'images/sprites/enemies/Sentry-left.gif'
        self.image_left = images.load(image_path, convert=False)
        self.image = self.image_left
        self.image_right = images.load(image_path, convert=False, flip=(True, False))
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        
    def set_image(self):
        if self.direction == self.LEFT:
            self.image = self.image_left
        elif self.direction == self.RIGHT:
            self.image = self.image_right
                
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

