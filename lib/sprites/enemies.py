"""Enemy classes"""

# third-party imports
import pygame

# first-party imports
from .base import BaseSprite
from .. import images

class Enemy(BaseSprite):
    SPEED = 100
    
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.attack = 1
        self.direction = self.RIGHT
        image_path = 'images/sprites/enemies/Sentry-left.gif'
        self.image_left = images.load(image_path)
        self.image = self.image_left
        self.image_right = images.load(image_path, flip=(True, False))
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        
        
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
                self.hit(player)

