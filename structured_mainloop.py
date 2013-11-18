import pygame

SCREEN_SIZE = (640, 480)

class Player(pygame.sprite.Sprite):
    SPEED = 200
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load('frog.gif')
        self.rect = pygame.rect.Rect((320, 240), self.image.get_size())

    def update(self, dt, game):
        # last position
        last = self.rect.copy()
        
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= self.SPEED * dt
        if key[pygame.K_RIGHT]:
            self.rect.x += self.SPEED * dt
        if key[pygame.K_UP]:
            self.rect.y -= self.SPEED * dt
        if key[pygame.K_DOWN]:
            self.rect.y += self.SPEED * dt
            
        for cell in pygame.sprite.spritecollide(self, game.walls, False):
            self.rect = last
        
class Game():
    def main(self, screen):
        clock = pygame.time.Clock()
        
        background = pygame.image.load('Castle.gif')
        background = pygame.transform.scale(background, SCREEN_SIZE)
        sprites = pygame.sprite.Group()
        self.player = Player(sprites)
        self.walls = pygame.sprite.Group()
        block = pygame.image.load('Chest.gif')
        for x in range(0, 640, 32):
            for y in range(0, 480, 32):
                if x in (0, 640-32) or y in (0, 480-32):
                    wall = pygame.sprite.Sprite(self.walls)
                    wall.image = block
                    wall.rect = pygame.rect.Rect((x,y), block.get_size())
        
        while True:
            dt = clock.tick(30) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            
            sprites.update(dt, self)
            screen.blit(background, (0,0))
            sprites.draw(screen)
            pygame.display.flip()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    game = Game()
    game.main(screen)