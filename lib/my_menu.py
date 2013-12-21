import pygame

pygame.init()
if not pygame.display.get_init():
    pygame.display.init()

if not pygame.font.get_init():
    pygame.font.init()
    
class Menu(object):
    FONT = pygame.font.Font('../coders_crux.ttf', 32)
    
    
    def __init__(self, screen, items, font=FONT):
        self.items = items
        self.selected = 0
        self.surfaces = []
        self.font = font
        self.draw(screen)
        self.mainloop()
        
    def draw(self, screen):
        self.surfaces.append(self.font.render(self.items[0], 1, (255, 255, 255)))
        screen.fill((0, 0, 0))
        screen.blit(self.surfaces[0], (25, 25))
    
    def mainloop(self):
        pygame.display.update()
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        return
    
if __name__ == '__main__':
    screen = pygame.display.set_mode((640, 480))
    menu = Menu(screen, 'this that theother'.split())
    