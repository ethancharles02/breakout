import pygame

class BreakoutRectangle:
    def __init__(self, top: float, left: float, width: int = 100, height: int = 30):        
        self._top = top
        self._left = left
        self._rect = pygame.Rect(left, top, width, height)
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, pygame.Color(255, 0, 0), self._rect)
    
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