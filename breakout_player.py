import pygame
from constants import SCREEN_WIDTH
from breakout_rectangle import BreakoutRectangle

class BreakoutPlayer(BreakoutRectangle):
    def __init__(self, top: float, left: float, width: int = 100, height: int = 5, speed: float = 500):
        self.speed = speed
        
        self._top = top
        self._left = left
        self._rect = pygame.Rect(left, top, width, height)
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, pygame.Color(0, 0, 255), self._rect)
    
    def update(self, dt: float):
        keys = pygame.key.get_pressed()
        direction = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction = 1
        
        self.left += self.speed * direction * dt
        if self.left <= 0:
            self.left = 0
        elif self.left >= SCREEN_WIDTH - self.width:
            self.left = SCREEN_WIDTH - self.width
            
    @property
    def top(self):
        return self._top
    @top.setter
    def top(self, value: float):
        self._top = value
        self._rect.top = self._top
    
    @property
    def left(self):
        return self._left
    @left.setter
    def left(self, value: float):
        self._left = value
        self._rect.left = self._left
    
    @property
    def width(self):
        return self._rect.width
    @width.setter
    def width(self, value: int):
        self._rect.width = value
    
    @property
    def height(self):
        return self._rect.height
    @height.setter
    def height(self, value: int):
        self._rect.height = value