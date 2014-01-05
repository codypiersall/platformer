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
    """
    Class for building a menu.  Initialize it with a Pygame surface object,
    list of menu items (it's just a list of strings), a Pygame font object,
    and a dict of settings.  The idea behind this class is that menus are 
    for changing settings, which will be given to other Pygame objects.
    
    
    """
    SPACE = 10
    UP = pygame.K_UP
    DOWN = pygame.K_DOWN
    RETURN = pygame.K_RETURN
    BG_COLOR = (0,0,0)
    FONT_COLOR = (255,0,0)
    SELECTOR_COLOR = (0,255,0)
    DEFAULT_SETTINGS = {'players': 1, 'level': 'maps/map1.tmx', 'character': 'frog'}
    
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
    
    def add_item(self, item):
        """Add another item to the menu.  `item` should just be a string."""
        self.items.append(item)
    
    def add_submenu(self, index, items):
        """
        Create a new Menu instance, initialized with items, that can be
        accessed by clicking on the index of the current menu.
        
        This makes the font and the settings refer to the same object,
        so a submenu can change settings too.
        
        example:
        ```
        main_menu = Menu(screen, ['Start', 'Options', 'Back'], some_font)
        options_menu = main_menu.add_submenu(1, ['Levels', 'Character Select'])
        ```
        
        this will create a menu with "Start", "Options", and "Back" items first;
        then clicking "Options" will start the `options_menu` main loop.
        """
        
        submenu = Menu(self.screen, items, self.font, self.settings)
        
        self.__add_action(index, submenu)
        return submenu
    
    def change_settings(self, index, setting, value):
        """
        When a menu item associated with the given index is clicked,
        change the setting indicated to value.
        """
        self.__add_action(index, ('settings', setting, value))
    
    def draw(self):
        """Menu layout and whatnot."""
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
        """Change the current menu selection."""
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


    def _reset_repeat(self):
        """Change key repeat back to what it was before the menu was called."""
        if self.initial_repeat == (0, 0):
            pygame.key.set_repeat()
        else:
            pygame.key.set_repeat(*self.initial_repeat)

    def seeya(self):
        """Clean up code when the menu is destroyed."""
        self._reset_repeat()
    
    def on_enter(self):
        """Determine what to do when the enter key is pressed."""
        
        action = self.actions[self.selected]
        if isinstance(action, Menu):
            action.mainloop()
            
        elif action == 'return':
            # hokey way of getting back to the main loop.  I'm not proud
            # of this.
            raise ReturnError
        
        elif isinstance(action, (tuple, list)):
            if action[0] == 'settings':
                self.settings[action[1]] = action[2]
                print(self.settings)
                raise ReturnError
            
            if action[0] == 'start':
                game = action[1]()
                self._reset_repeat()
                game.main(self.screen, self.settings)
                pygame.key.set_repeat(*self.repeat)
    
    def add_start_action(self, index, Game):
        """Resets key repeat and calls `Game.main(self.screen, self.settings)`"""
        self.__add_action(index, ('start', Game))
        
    def add_back_action(self, index):
        """ 
        Whenever `index` is selected, go to the previous mainloop.
        """
        self.__add_action(-1, 'return')
        
    def __add_action(self, index, action):
        """
        Internal method used for adding an action to a menu item.
        This should not be called directly.
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
    main_menu.add_start_action(0, Game)
    main_menu.add_back_action(-1)

    options_menu = main_menu.add_submenu(1,['Levels', 'Number of Players', 'Character Select', 'Back'])
    options_menu.add_back_action(-1)
    
    levels = glob.glob(level_glob)
    level_items = [os.path.splitext(os.path.basename(l))[0] for l in levels] + ['Back']
    levels_menu = options_menu.add_submenu(0, level_items)
    
    players_menu = options_menu.add_submenu(1, [1, 2, 'Back'])
    
    
    
    levels_menu.add_back_action(-1)
    players_menu.add_back_action(-1)

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
    menu.__add_action(-1, 'return')
    menu.mainloop()
    
    