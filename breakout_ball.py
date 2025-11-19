import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import math

class BreakoutBall:
    def __init__(self, x: float, y: float, dx: float, dy: float, radius: float = 30):
        self.radius = radius
        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y
        self.dx = dx
        self.init_dx = dx
        self.dy = dy
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, pygame.Color(0, 255, 0), (self.x, self.y), self.radius)
    
    def update(self, dt: float):
        self.x0 = self.x
        self.y0 = self.y
        self.x += self.dx * dt
        self.y += self.dy * dt
        
        # TODO this could be made smarter. If dt is very large, the ball will just end up in the corner
        if self.x - self.radius < 0:
            self.x = self.radius
            self.dx = abs(self.dx)
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.dx = -abs(self.dx)
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.dy = abs(self.dy)
        elif self.y + self.radius > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - self.radius
            self.dy = -abs(self.dy)
    
    def get_speed(self):
        return math.dist((self.dx, self.dy), (0, 0))