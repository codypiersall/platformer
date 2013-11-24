import pygame
import tmx

SCREEN_SIZE = (640, 480)
GRAVITY = 2400
MAX_FALL_SPEED = 500

class Player(pygame.sprite.Sprite):
    SPEED = 200
    JUMP_IMPULSE = -700
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load('frog.gif')
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.dy = 0
        
    def update(self, dt, game):
        # last position
        last = self.rect.copy()
        
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= int(self.SPEED * dt)
        if key[pygame.K_RIGHT]:
            self.rect.x += int(self.SPEED * dt)
 
        # JUMP!
        if self.resting and key[pygame.K_SPACE]:
            self.dy = self.JUMP_IMPULSE
        self.dy = min(MAX_FALL_SPEED, self.dy + GRAVITY * dt)
        
        self.rect.y += self.dy * dt
        
        new = self.rect
        self.resting = False
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom > cell.top:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                self.dy = 0
        
        game.tilemap.set_focus(new.x, new.y)
        
class Game():
    def main(self, screen):
        clock = pygame.time.Clock()
        
        background = pygame.image.load('Castle.gif')
        background = pygame.transform.scale(background, SCREEN_SIZE)
        
        self.tilemap = tmx.load('map.tmx', screen.get_size())
        
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)

        while True:
            dt = clock.tick(60) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            
            self.tilemap.update(dt, self)
            screen.blit(background, (0,0))
            self.tilemap.draw(screen)
            pygame.display.flip()
    
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    game = Game()
    game.main(screen)