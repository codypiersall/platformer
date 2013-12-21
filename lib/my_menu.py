import pygame

pygame.init()
if not pygame.display.get_init():
    pygame.display.init()

if not pygame.font.get_init():
    pygame.font.init()
    
class Menu(object):
    FONT = pygame.font.Font('../coders_crux.ttf', 32)
    SPACE = 10
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    
    def __init__(self, screen, items, font=FONT):
        self.screen = screen
        self.items = items
        self.selected = 0
        self.surfaces = []
        self.font = font
        self.initial_repeat = pygame.key.get_repeat()
        print(self.initial_repeat)
        pygame.key.set_repeat(200, 70)
        self.draw()
        self.mainloop()
        
    def draw(self):
        self.surfaces.extend([self.font.render(str(i), 1, (255, 255, 255)) for i in self.items])
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.surfaces[0], (25, 25))
        self.screen.blit(self.surfaces[1], (25, 75))
    
    def change_select(self, direction):
        if direction == self.UP:
            if self.selected == 0:
                self.selected = len(self.items) - 1
            else:
                self.selected -= 1
                
        elif direction == self.DOWN:
            if self.selected == len(self.items) - 1:
                self.selected = 0
            else:
                self.selected += 1
        
        print(self.selected)
    

    def seeya(self):
        """Clean up code when the menu is destroyed."""
        if self.initial_repeat == (0, 0):
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(self.initial_repeat)

    def mainloop(self):
        pygame.display.update()
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.seeya()
                    return
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.seeya()
                        return
                    
                    elif e.key == self.UP or e.key == self.DOWN:
                        self.change_select(e.key)
            
            self.draw()
            
if __name__ == '__main__':
    screen = pygame.display.set_mode((640, 480))
    menu = Menu(screen, 'this that theother'.split())
    