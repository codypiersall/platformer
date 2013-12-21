import pygame

class KeyMap(object):
    """Maps keys for different players"""
    def __init__(self, left, right, jump, shoot, invincible):
        self.LEFT = left
        self.RIGHT = right
        self.JUMP = jump
        self.SHOOT = shoot
        self.INVINCIBLE = invincible
        
km1 = KeyMap(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_i)
km2 = KeyMap(pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_TAB, pygame.K_i)
