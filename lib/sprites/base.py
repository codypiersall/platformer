import pygame

class BaseSprite(pygame.sprite.Sprite):
    RIGHT = 1
    LEFT= -1
    
    # moving constants
    STILL = 0
    WALKING = 1
    RUNNING = 1.5
    NOT_RUNNING = 1.0
    # 1 second of invincibility after been hit.
    BEEN_HIT_TIME = 1
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.moving = self.WALKING
        self.direction = self.RIGHT
        self.is_dead = False
        self.been_hit = False
        self.dy = 0

    def hit(self, other):
        """ This is a lame, unsophisticated way to do attacks."""
        if other.been_hit <= 0:
            other.health -= self.attack / other.defense
            other.been_hit = self.BEEN_HIT_TIME
            if other.health <= 0:
                other.is_dead = True
        
    def update_hit_timer(self, dt):
        self.been_hit = max(self.been_hit - dt, 0)

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
    
class AffectedByGravitySprite(BaseSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def move(self, dt, game):
        """Movement and collision stuff, for sprites affected by gravity"""
        last_position = self.rect.copy()
        self.rect.x += int(self.direction * self.SPEED * self.moving * self.running * dt)
        self.dy = min(game.MAX_FALL_SPEED, self.dy + game.GRAVITY * dt)
        self.rect.y += self.dy * dt
        new = self.rect
        self.resting = False
    
        for cell in game.tilemap.layers['triggers'].collide(new, 'blockers'):
            blockers = cell['blockers']
            if 'l' in blockers and last_position.right <= cell.left and new.right > cell.left:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.right = cell.left
            if 'r' in blockers and last_position.left >= cell.right and new.left < cell.right:
                # this check is important because it lets you walk along blocks.
                if not last_position.bottom == cell.top:
                    new.left = cell.right
            if 't' in blockers and last_position.bottom <= cell.top and new.bottom > cell.top:
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    self.resting = True
                    self.double_jumped = False
                    new.bottom = cell.top
                    self.dy = game.GRAVITY * dt
                    
            if 'b' in blockers and last_position.top >= cell.bottom and new.top < cell.bottom: 
                # this check makes sure you can't cling to blocks that you shouldn't be able to.
                if new.right > cell.left and new.left < cell.right:
                    new.top = cell.bottom
                    self.dy = 0
        
        return new