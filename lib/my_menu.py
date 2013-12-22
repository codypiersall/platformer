import pygame

pygame.init()
if not pygame.display.get_init():
    pygame.display.init()

if not pygame.font.get_init():
    pygame.font.init()    

# This silly Exception is used to return from a menu.
class ReturnError(Exception):
    pass

class ExitError(Exception):
    pass

class Menu(object):
    SPACE = 10
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    RETURN = pygame.K_RETURN
    BG_COLOR = (0,0,0)
    FONT_COLOR = (255,0,0)
    SELECTOR_COLOR = (0,255,0)
    DEFAULT_SETTINGS = {'players': 1, 'level': 'maps/map1.tmx'}
    
    def __init__(self, screen, items, font, settings=DEFAULT_SETTINGS):
        self.settings = settings
        self.screen = screen
        self.items = items
        self.selected = 0
        self.surfaces = []
        self.font = font
        self.actions = {}
        self.initial_repeat = pygame.key.get_repeat()
        self.repeat = (200, 70)
        self.draw()
    
    def add_item(self, item):
        self.items.append(item)
    
    def add_submenu(self, index, items):
        
        submenu = Menu(self.screen, items, self.font, self.settings)
        
        self.add_action(index, submenu)
        return submenu
    
    def change_settings(self, index, setting, value):
        self.add_action(index, ('settings', setting, value))
    
    def draw(self):
        self.surfaces = [self.font.render(str(i), 1, self.FONT_COLOR) for i in self.items]
        
        num_items = len(self.items)
        ind_height = self.surfaces[0].get_height()
        height = self.surfaces[0].get_height() * num_items + self.SPACE * (num_items - 1)
        width = max(s.get_width() for s in self.surfaces)
        draw_surf  = pygame.Surface((width, height))
        draw_surf.fill(self.BG_COLOR)
        for i, item in enumerate(self.surfaces):
            draw_surf.blit(item, (0, ind_height*i + self.SPACE*i))
        
        menu_x = (self.screen.get_width() - width) / 2
        menu_y = (self.screen.get_height() - height) / 2
        
        sy = menu_y + ind_height*self.selected + self.SPACE * self.selected
        sx = menu_x - 20
        
        self.screen.fill(self.BG_COLOR)
        self.screen.blit(draw_surf, (menu_x, menu_y))
        pygame.draw.polygon(self.screen, self.SELECTOR_COLOR, ([sx,sy], [sx, sy + ind_height], [sx + 10, (2 *sy + ind_height) / 2]))
            
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

    def seeya(self):
        """Clean up code when the menu is destroyed."""
        if self.initial_repeat == (0, 0):
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(*self.initial_repeat)
    
    def on_enter(self):        
        action = self.actions[self.selected]
        if isinstance(action, Menu):
            action.mainloop()
            
        elif action == 'return':
            raise ReturnError
        
        elif isinstance(action, (tuple, list)):
            if action[0] == 'settings':
                self.settings[action[1]] = action[2]
                print(self.settings)
                raise ReturnError
            
            if action[0] == 'start':
                game = action[1]()
                game.main(self.screen, self.settings)
    
    def add_action(self, index, action):
        """
        Supported actions:
            Change a value in the settings dict.
            Change the displayed item.
        """
        if index < 0:
            index = len(self.items) + index
        self.actions.update({index: action})
    
    def mainloop(self):
        pygame.key.set_repeat(*self.repeat)
        pygame.display.update()
        clock = pygame.time.Clock()
        while True:
            clock.tick(30)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    raise ExitError
                
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.seeya()
                        return
                    
                    elif e.key == self.UP or e.key == self.DOWN:
                        self.change_select(e.key)
                    elif e.key == self.RETURN:
                        try:
                            self.on_enter()
                        except ReturnError:
                            return
                        
            self.draw()
            pygame.display.update()

def main_menu(screen, Game, level_glob = 'maps/*.tmx', default_settings={'level': 'maps/map1.tmx', 'players': 1},
              font='coders_crux.ttf'):
    
    import glob
    import os
    font = pygame.font.Font(font, 32)
    main_menu = Menu(screen, 'Start Options Quit'.split(), font=font)
    options_menu = main_menu.add_submenu(1,'Levels Players Back'.split())
    # options_menu = Menu(screen, 'Levels Players Back'.split())
    
    levels = glob.glob(level_glob)
    level_items = [os.path.splitext(os.path.basename(l))[0] for l in levels] + ['Back']
    levels_menu = options_menu.add_submenu(0, level_items)
    
    players_menu = options_menu.add_submenu(1, [1, 2, 'Back'])
    
    main_menu.add_action(0, ('start', Game))
    main_menu.add_action(2, 'return')
    
    options_menu.add_action(-1, 'return')
    
    levels_menu.add_action(-1, 'return')
    players_menu.add_action(-1, 'return')

    [levels_menu.change_settings(i, 'level', levels[i]) for i in range(len(levels))]
    [players_menu.change_settings(i, 'players', i+1) for i in range(2)]

    try:
        main_menu.mainloop()
    except ExitError:
        pygame.quit()
            
if __name__ == '__main__':
    """Minimalist example for creating a menu."""
    screen = pygame.display.set_mode((640, 480))
    font = pygame.font.Font('../coders_crux.ttf', 48)
    menu = Menu(screen, 'Some Good Items Exit'.split(), font)
    menu.add_action(-1, 'return')
    menu.mainloop()
    
    