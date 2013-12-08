import pygame

class KeyMap(object):
    """Maps keys for different players"""
    def __init__(self, left, right, jump, shoot):
        self.LEFT = left
        self.RIGHT = right
        self.JUMP = jump
        self.SHOOT = shoot
        
km1 = KeyMap(pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_LSHIFT)
km2 = KeyMap(pygame.K_a, pygame.K_d, pygame.K_TAB, pygame.K_BACKQUOTE)