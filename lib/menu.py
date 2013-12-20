'''
@author: avalanchy (at) google mail dot com
@version: 0.1; python 2.7; pygame 1.9.2pre; SDL 1.2.14; MS Windows XP SP3
@date: 2012-04-08
@license: This document is under GNU GPL v3

README on the bottom of document.

@font: from http://www.dafont.com/coders-crux.font
      more abuot license you can find in data/coders-crux/license.txt
'''

import pygame
from pygame.locals import *

if not pygame.display.get_init():
    pygame.display.init()

if not pygame.font.get_init():
    pygame.font.init()

import glob
from os import path

class Menu(object):
    rozmiar_fontu = 32
    font_path = 'coders_crux.ttf'
    font = pygame.font.Font
    dest_surface = pygame.Surface
    ilosc_pol = 0
    kolor_tla = (51,51,51)
    kolor_tekstu =  (255, 255, 153)
    kolor_zaznaczenia = (153,102,255)
    pozycja_zaznaczenia = 0
    pozycja_wklejenia = (0,0)
    menu_width = 0
    menu_height = 0

    class Pole:
        tekst = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        zaznaczenie_rect = pygame.Rect

    def move_menu(self, top, left):
        self.pozycja_wklejenia = (top,left) 

    def set_colors(self, text, selection, background):
        self.kolor_tla = background
        self.kolor_tekstu =  text
        self.kolor_zaznaczenia = selection
        
    def set_fontsize(self,font_size):
        self.rozmiar_fontu = font_size
        
    def set_font(self, path):
        self.font_path = path
        
    def get_position(self):
        return self.pozycja_zaznaczenia
    
    def init(self, lista, dest_surface):
        self.lista = lista
        self.pola = []
        self.dest_surface = dest_surface
        self.ilosc_pol = len(self.lista)
        self.stworz_strukture()        
        
    def draw(self,przesun=0):
        if przesun:
            self.pozycja_zaznaczenia += przesun 
            if self.pozycja_zaznaczenia == -1:
                self.pozycja_zaznaczenia = self.ilosc_pol - 1
            self.pozycja_zaznaczenia %= self.ilosc_pol
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.kolor_tla)
        zaznaczenie_rect = self.pola[self.pozycja_zaznaczenia].zaznaczenie_rect
        pygame.draw.rect(menu,self.kolor_zaznaczenia,zaznaczenie_rect)

        for i in range(self.ilosc_pol):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.pozycja_wklejenia)
        return self.pozycja_zaznaczenia

    def stworz_strukture(self):
        przesuniecie = 0
        self.menu_height = 0
        self.font = pygame.font.Font(self.font_path, self.rozmiar_fontu)
        for i in range(self.ilosc_pol):
            self.pola.append(self.Pole())
            self.pola[i].tekst = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].tekst, 1, self.kolor_tekstu)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            przesuniecie = int(self.rozmiar_fontu * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = przesuniecie
            self.pola[i].pole_rect.top = przesuniecie+(przesuniecie*2+height)*i

            width = self.pola[i].pole_rect.width+przesuniecie*2
            height = self.pola[i].pole_rect.height+przesuniecie*2            
            left = self.pola[i].pole_rect.left-przesuniecie
            top = self.pola[i].pole_rect.top-przesuniecie

            self.pola[i].zaznaczenie_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.pozycja_wklejenia
        self.pozycja_wklejenia = (x+mx, y+my) 


if __name__ == "__main__":
    import sys
    surface = pygame.display.set_mode((854,480)) #0,6671875 and 0,(6) of HD resoulution
    surface.fill((51,51,51))
    '''First you have to make an object of a *Menu class.
    *init take 2 arguments. List of fields and destination surface.
    Then you have a 4 configuration options:
    *set_colors will set colors of menu (text, selection, background)
    *set_fontsize will set size of font.
    *set_font take a path to font you choose.
    *move_menu is quite interesting. It is only option which you can use before 
    and after *init statement. When you use it before you will move menu from 
    center of your surface. When you use it after it will set constant coordinates. 
    Uncomment every one and check what is result!
    *draw will blit menu on the surface. Be careful better set only -1 and 1 
    arguments to move selection or nothing. This function will return actual 
    position of selection.
    *get_postion will return actual position of selection. '''
    menu = Menu()#necessary
    #menu.set_colors((255,255,255), (0,0,255), (0,0,0))#optional
    #menu.set_fontsize(64)#optional
    #menu.set_font('data/couree.fon')#optional
    #menu.move_menu(100, 99)#optional
    menu.init(['Start','Options','Quit'], surface)#necessary
    #menu.move_menu(0, 0)#optional
    menu.draw()#necessary
    
    pygame.key.set_repeat(199,69)#(delay,interval)
    pygame.display.update()
    while 1:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    menu.draw(-1) #here is the Menu class function
                if event.key == K_DOWN:
                    menu.draw(1) #here is the Menu class function
                if event.key == K_RETURN:
                    if menu.get_position() == 2:#here is the Menu class function
                        pygame.display.quit()
                        sys.exit()                        
                if event.key == K_ESCAPE:
                    pygame.display.quit()
                    sys.exit()
                pygame.display.update()
            elif event.type == QUIT:
                pygame.display.quit()
                sys.exit()
        pygame.time.wait(8)
        
def level_menu(screen, default_level='../maps/map1.tmx'):
    levels_menu = Menu()
    levels = glob.glob('../maps/*.tmx')
    display = [path.splitext(path.basename(l))[0] for l in levels]
    levels_menu.init(display + ['Back'], screen)
    
    while True:
        screen.fill((51, 51, 51))
        levels_menu.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    levels_menu.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    levels_menu.draw(1) #here is the Menu class function
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if levels_menu.get_position() == len(levels): #here is the Menu class function
                        return default_level
                    else:
                        return levels[levels_menu.get_position()]
                elif event.key == pygame.K_ESCAPE:
                    return default_level
                pygame.display.update()
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)

def player_menu(screen, players):
    options_menu = Menu()
    options_menu.init(['1', '2', 'Back'], screen)    
    
    while True:
        screen.fill((51,51,51))
        options_menu.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    options_menu.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    options_menu.draw(1) #here is the Menu class function
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if options_menu.get_position() == 0:
                        return '1'
                    elif options_menu.get_position() == 1:
                        return '2'

                    elif options_menu.get_position() == 2: #here is the Menu class function
                        return players

                elif event.key == pygame.K_ESCAPE:
                    return players
            
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)

def options_menu(screen, level, players):
    """Options for the game """
    options_menu = Menu()
    options_menu.init(['Levels', 'Players', 'Back'], screen)    
    
    while True:
        screen.fill((51,51,51))
        options_menu.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    options_menu.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    options_menu.draw(1) #here is the Menu class function
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if options_menu.get_position() == 0:
                        level = level_menu(screen, level)
                    elif options_menu.get_position() == 1:
                        players = player_menu(screen, players)

                    elif options_menu.get_position() == 2: #here is the Menu class function
                        return level, players

                elif event.key == pygame.K_ESCAPE:
                    return level, players
            
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)
        
def main_menu(screen, Game, default_level, default_players):
    main_menu = Menu()
    main_menu.init(['Start', 'Options', 'Quit'], screen)
    pygame.key.set_repeat(199, 69) #(delay,interval)
    
    # set the defaults
    level = default_level
    players = default_players
    while True:
        screen.fill((51, 51, 51))
        main_menu.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    main_menu.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    main_menu.draw(1) #here is the Menu class function
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if main_menu.get_position() == 0:
                        pygame.key.set_repeat()
                        game = Game()
                        game.main(screen, level, players)
                        
                    elif main_menu.get_position() == 1:
                        level, players = options_menu(screen, level, players)

                    elif main_menu.get_position() == 2: #here is the Menu class function
                        pygame.display.quit()
                        return

                elif event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    return
            
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)
