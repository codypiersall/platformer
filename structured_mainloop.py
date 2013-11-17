import pygame

class Player(pygame.sprite.Sprite):
    SPEED = 300
    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load('frog.png')
        self.rect = pygame.rect.Rect((320, 240), self.image.get_size())

    def update(self, dt):
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= self.SPEED * dt
        if key[pygame.K_RIGHT]:
            self.rect.x += self.SPEED * dt
        if key[pygame.K_UP]:
            self.rect.y -= self.SPEED * dt
        if key[pygame.K_DOWN]:
            self.rect.y += self.SPEED * dt
        
class Game():
    def main(self, screen):
        clock = pygame.time.Clock()
        
        image = pygame.image.load('frog.png')
        sprites = pygame.sprite.Group()
        self.player = Player(sprites)
        while True:
            dt = clock.tick(30) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            
            sprites.update(dt)
            screen.fill((200,200,200))
            sprites.draw(screen)
            pygame.display.flip()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    game = Game()
    game.main(screen)