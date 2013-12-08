import glob
import sys

import pygame
import tmx
import pyganim
import menu

SCREEN_SIZE = (640, 480)

# colors
GREEN = pygame.Color(0, 200, 0)
YELLOW = pygame.Color(150, 150, 0)
RED = pygame.Color(100, 0, 0)
DARK_GREY = pygame.Color(50, 50, 50)

class Bullet(pygame.sprite.Sprite):
    image = pygame.image.load('images/Masamune.gif')
    image_right = pygame.transform.rotate(image, 270)
    image_left = pygame.transform.flip(image_right, True, False)
    SPEED = 400
    # lifespan of bullet in seconds
    LIFESPAN = 1
    
    def __init__(self, location, direction, *groups):
        super().__init__(*groups)
        if direction > 0:
            self.image = self.image_right
            self.rect = pygame.rect.Rect(location, self.image.get_size())
        else:
            self.image = self.image_left
            x_ = self.image.get_size()[0]
            self.rect = pygame.rect.Rect((location[0] - x_, location[1]), self.image.get_size())
        self.direction = direction
        self.lifespan = self.LIFESPAN
        
    def update(self, dt, game):
        self.lifespan -= dt
        if self.lifespan < 0:
            self.kill()
            return
        self.rect.x += self.direction * self.SPEED * dt
        
        if pygame.sprite.spritecollide(self, game.enemies, True):
            self.kill()
            game.explosion.play()
            
class Enemy(pygame.sprite.Sprite):
    SPEED = 100
    image_left = pygame.image.load('images/Sentry-left.gif')
    image = image_left
    image_right = pygame.transform.flip(image_left, True, False)
    
    def __init__(self, location, *groups):
        super().__init__(*groups)
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = 1
        
    def update(self, dt, game):
        self.rect.x += int(self.direction * self.SPEED * dt)
        
        if self.direction > 0:
            self.image = self.image_right
        else:
            self.image = self.image_left
        for cell in game.tilemap.layers['triggers'].collide(self.rect, 'reverse'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break
        
        if self.rect.colliderect(game.player.rect):
            game.player.health -= dt
            if game.player.health < 0:
                game.player.is_dead = True

class Player(pygame.sprite.Sprite):
    # Player's left and right speed in pixels per second
    SPEED = 200

    # Player's jumping speed in pixels per second.
    JUMP_SPEED = -700
    
    # How much time passes between shots in seconds.
    COOLDOWN_TIME = 0.5
    
    # Player's maximum health
    MAX_HEALTH = 2
    
    # Directions
    LEFT = -1
    RIGHT = 1
    
    # moving constants
    STILL = 0
    WALKING = 1
    
    walk_left_anim = pyganim.PygAnimation([('images/frog-walk-01.gif', .1),
                                           ('images/frog-walk-02.gif', .1),
                                           ('images/frog-walk-03.gif', .1),
                                           ('images/frog-walk-04.gif', .1),
                                           ('images/frog-walk-05.gif', .1),
                                           ('images/frog-walk-00.gif', .1)
                                          ])
    
    
    walk_right_anim = walk_left_anim.getCopy()
    walk_right_anim.flip(True, False)
    walk_right_anim.makeTransformsPermanent()

    face_left = pyganim.PygAnimation([('images/frog-walk-00.gif', 10)])

    face_right = face_left.getCopy()
    face_right.flip(True, False)
    face_right.makeTransformsPermanent()
    
    animations = {LEFT:  {STILL: face_left,
                          WALKING: walk_left_anim},
                  RIGHT: {STILL: face_right,
                          WALKING: walk_right_anim}
                 }
    
    def __init__(self, location, *groups):
        super().__init__(*groups)
        
        # True if the player is on a surface, else False.
        self.resting = False
        
        # Set to True only when player dies.
        self.is_dead = False
        
        # gun_cooldown is the time left before the player can shoot again.
        self.gun_cooldown = 0
        
        # Whether the player has used the double jump.
        self.double_jumped = False
        
        # player's health; currently, it goes down based on how long 
        # the player collides with the enemy.
        self.health = self.MAX_HEALTH
        
        # self.direction and self.moving are for determining which way
        # the player is facing (either self.LEFT or self.RIGHT) and
        # whether the player is moving (either self.STILL or self.WALK)
        self.direction = self.RIGHT
        self.moving = self.STILL
        
        # the current animation that is playing
        self.current_animation = self.face_right
        
        # TODO: Find out what is actually displaying the image.
        # I think the image gets blitted by the tmx module?
        self.image = self.face_right.getCurrentFrame()
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        
        # Whether the character should try to jump.  This gets set to True
        # when the player hits the jump button (default space) but does not 
        # necessarily mean the player can actually jump.
        self.jump = False
        
        # whether the player should try to shoot.
        self.shoot = False
        
        # Vertical velocity.  This gets changed by either falling or jumping.
        self.dy = 0
        

    def animate(self):
        """Animate the player based on direction and movement.
           
        If the animation that should be playing is already playing, this basically does nothing."""
        last_anim = self.current_animation
        next_anim = self.animations[self.direction][self.moving]
        if next_anim != last_anim:
            last_anim.stop()
            next_anim.play()
            self.current_animation = next_anim

        self.image = next_anim.getCurrentFrame()



    def try_to_jump(self, game):
        if self.jump:
            if self.resting:
                self.dy = self.JUMP_SPEED
                game.jump.play()
                self.double_jumped = False
            elif self.dy > 60 and not self.double_jumped:
                self.dy = self.JUMP_SPEED
                self.double_jumped = True
                game.jump.play()
            self.jump = False


    def try_to_shoot(self, game):
        if self.shoot:
            if not self.gun_cooldown:
                game.shoot.play()
                Bullet(self.rect.center, self.direction, game.sprites)
                self.gun_cooldown = self.COOLDOWN_TIME
            self.shoot = False

    def do_actions(self, game):
        self.try_to_jump(game)
        self.try_to_shoot(game)

    def update(self, dt, game):
        
        # finds the right animation and displays it.
        self.animate()
        
        # jump, shoot, whatever.
        self.do_actions(game)
        
        last_position = self.rect.copy()            
        self.rect.x += int(self.direction * self.SPEED * self.moving * dt)        
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        self.dy = min(game.MAX_FALL_SPEED, self.dy + game.GRAVITY * dt)
        
        self.rect.y += self.dy * dt
        new = self.rect
        self.resting = False
        # last_position position
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last_position.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last_position.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last_position.bottom <= cell.top and new.bottom > cell.top:
                self.resting = True
                self.double_jumped = False
                new.bottom = cell.top
                self.dy = game.GRAVITY * dt
            if 'b' in blockers and last_position.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                self.dy = 0
        
        game.tilemap.set_focus(new.x, new.y)
        if new.x < -10 or new.y > game.tilemap.px_height:
            self.is_dead = True

class Game():
    GRAVITY = 2400
    MAX_FALL_SPEED = 700
    FPS = 60
    LIFEBAR_LENGTH = 250
    LIFEBAR_WIDTH = 10
    
    def main(self, screen, level):
        clock = pygame.time.Clock()
        
        background = pygame.image.load('images/background.png')
        background = pygame.transform.scale(background, SCREEN_SIZE)
        
        self.tilemap = tmx.load(level, screen.get_size())
        
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        # make an alias for player so I don't have to type all the time.
        player = self.player
        self.tilemap.layers.append(self.sprites)
        
        # sound effects
        self.jump = pygame.mixer.Sound('sounds/jump.wav')
        self.shoot = pygame.mixer.Sound('sounds/shoot.wav')
        self.explosion = pygame.mixer.Sound('sounds/explosion.wav')
        
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy'):
            Enemy((enemy.px, enemy.py), self.enemies)
        
        self.tilemap.layers.append(self.enemies)
        
        while True:
            dt = clock.tick(self.FPS) / 1000
            key = pygame.key.get_pressed()
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    return
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                        
                    elif event.key == pygame.K_LEFT:
                        player.moving = player.WALKING
                        player.direction = player.LEFT
                        
                    elif event.key == pygame.K_RIGHT:
                        player.moving = player.WALKING
                        player.direction = player.RIGHT            
                        
                    elif event.key == pygame.K_SPACE:
                        player.jump = True
                        
                    elif event.key == pygame.K_LSHIFT:
                        player.shoot = True
                        
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        if key[pygame.K_RIGHT]: 
                            player.moving = player.WALKING
                            player.direction = player.RIGHT
                        else:
                            player.moving = player.STILL
                        
                    elif event.key == pygame.K_RIGHT:
                        if key[pygame.K_LEFT]: 
                            player.moving = player.WALKING
                            player.direction = player.LEFT
                        else:
                            player.moving = player.STILL

            
            screen.blit(background, (0,0))
            self.tilemap.update(dt, self)
            self.tilemap.draw(screen)
            
            self.draw_lifebar(screen, self.player.health, self.player.MAX_HEALTH)
            pygame.display.flip()
            if self.player.is_dead:
                return
    
    def draw_lifebar(self, screen, health, max_health):
        # outline for lifebar
        pygame.draw.rect(screen, DARK_GREY, (10,10, self.LIFEBAR_LENGTH, 20))
        
        ratio = health / max_health
        if ratio < 0.15:
            color = RED
        elif ratio < .7:
            color = YELLOW
        else:
            color = GREEN
        
        
        length = (self.LIFEBAR_LENGTH - 3) * health/max_health 
        pygame.draw.rect(screen, color, (12,12, (length), 16))

def level_menu(screen, default_level='map1.tmx'):
    m = menu.Menu()
    levels = glob.glob('maps/*.tmx')
    m.init(levels + ['Back'], screen)
    
    while True:
        screen.fill((51, 51, 51))
        m.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    m.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    m.draw(1) #here is the Menu class function
                elif event.key == pygame.K_RETURN:
                    if m.get_position() == len(levels): #here is the Menu class function
                        return default_level
                    else:
                        return levels[m.get_position()]
                elif event.key == pygame.K_ESCAPE:
                    return default_level
                pygame.display.update()
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)
    
def main_menu(screen):
    m = menu.Menu()
    m.init(['Start', 'Levels', 'Quit'], screen)
    pygame.key.set_repeat(199, 69) #(delay,interval)
    level = 'maps/map1.tmx'
    while True:
        screen.fill((51, 51, 51))
        m.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    m.draw(-1) #here is the Menu class function
                elif event.key == pygame.K_DOWN:
                    m.draw(1) #here is the Menu class function
                elif event.key == pygame.K_RETURN:
                    if m.get_position() == 0:
                        pygame.key.set_repeat()
                        game = Game()
                        game.main(screen, level)
                        
                    elif m.get_position() == 1:
                        level = level_menu(screen, level)

                    elif m.get_position() == 2: #here is the Menu class function
                        pygame.display.quit()
                        return

                elif event.key == pygame.K_ESCAPE:
                    pygame.display.quit()
                    return
            
            elif event.type == pygame.QUIT:
                pygame.display.quit()
                sys.exit()
        
        pygame.time.wait(8)
        
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    main_menu(screen)
    