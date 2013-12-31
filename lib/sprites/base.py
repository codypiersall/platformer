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