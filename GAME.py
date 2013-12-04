import pygame
import tmx
import pyganim

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
    SPEED = 200
    JUMP_IMPULSE = -700
    COOLDOWN_TIME = 0.5
    MAX_HEALTH = 2
    
    # Directions
    LEFT = 'left'
    RIGHT = 'right'
    
    # moving 
    STILL = 'still'
    WALKING = 'walking'
    
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
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.gun_cooldown = 0
        self.double_jumped = False
        self.health = self.MAX_HEALTH
        self.direction = self.RIGHT
        self.moving = self.STILL
        self.walk_left_anim.play()
        self.image = self.walk_left_anim.getCurrentFrame()
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.jump = False
        
    def update(self, dt, game):
        global m
        global n
        # last position
        last = self.rect.copy()
        
        self.image = self.animations[self.direction][self.moving].getCurrentFrame()
        
        if self.direction == self.LEFT:
            if self.moving == self.WALKING:
                self.rect.x -= int(self.SPEED * dt)
                
        elif self.direction == self.RIGHT:
            if self.moving == self.WALKING:
                self.rect.x += int(self.SPEED * dt)
        
        key = pygame.key.get_pressed()
        if self.jump:
            if self.resting:
                self.dy = self.JUMP_IMPULSE
                game.jump.play()
                self.double_jumped=False
            elif self.dy > 60 and not self.double_jumped:
                self.dy = self.JUMP_IMPULSE
                self.double_jumped = True
                game.jump.play()
            self.jump = False
            
        if key[pygame.K_LSHIFT] and not self.gun_cooldown:
            if self.direction == self.RIGHT:
                Bullet(self.rect.center, 1, game.sprites)
            else:
                Bullet(self.rect.center, -1, game.sprites)
            self.gun_cooldown = self.COOLDOWN_TIME
            game.shoot.play()
            
        self.gun_cooldown = max(0, self.gun_cooldown - dt)
        self.dy = min(game.MAX_FALL_SPEED, self.dy + game.GRAVITY * dt)
        
        self.rect.y += self.dy * dt
        new = self.rect
        self.resting = False
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if 'r' in blockers and last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if 't' in blockers and last.bottom <= cell.top and new.bottom >= cell.top:
                self.resting = True
                self.double_jumped = False
                new.bottom = cell.top
                self.dy = 0
            if 'b' in blockers and last.top >= cell.bottom and new.top < cell.bottom:
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
    
    def main(self, screen):
        clock = pygame.time.Clock()
        
        background = pygame.image.load('images/background.png')
        background = pygame.transform.scale(background, SCREEN_SIZE)
        
        self.tilemap = tmx.load('maps/map1.tmx', screen.get_size())
        
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
                        player.walk_right_anim.stop()
                        player.walk_left_anim.play()
                        
                    elif event.key == pygame.K_RIGHT:
                        player.moving = player.WALKING
                        player.direction = player.RIGHT            
                        player.walk_left_anim.stop()
                        player.walk_right_anim.play()
                        
                    elif event.key == pygame.K_SPACE:
                        player.jump = True
                        
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        player.walk_left_anim.stop()
                        if key[pygame.K_RIGHT]: 
                            player.moving = player.WALKING
                            player.direction = player.RIGHT
                            player.walk_right_anim.play()
                        else:
                            player.moving = player.STILL
                        
                    elif event.key == pygame.K_RIGHT:
                        player.walk_right_anim.stop()
                        if key[pygame.K_LEFT]: 
                            player.moving = player.WALKING
                            player.direction = player.LEFT
                            player.walk_left_anim.play()
                        else:
                            player.moving = player.STILL
                        player.walk_right_anim.stop()

            
            self.tilemap.update(dt, self)
            screen.blit(background, (0,0))
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
        
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    game = Game()
    game.main(screen)