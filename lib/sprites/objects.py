from __future__ import division
import pygame
from .base import BaseSprite
from .. import images


class Bullet(BaseSprite):
    SPEED = 500
    # lifespan of bullet in seconds
    LIFESPAN = 1
    AFFECTED_BY_BLOCKERS = False
    AFFECTED_BY_GRAVITY = False

    def __init__(self, location, direction, image_path, *groups):
        super(Bullet, self).__init__(*groups)
        self.image_left = images.load(image_path, convert=False)
        self.image_right = images.load(image_path, flip=(True, False), convert=False)

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
        self.move(dt, game)

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


