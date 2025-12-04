import pygame
from ..constants import SCREEN_WIDTH
from .breakout_rectangle import BreakoutRectangle

class BreakoutPlayer(BreakoutRectangle):
    def __init__(self, top: float, left: float, width: int = 100, height: int = 5, speed: float = 500):
        """Constructs a player object

        Arguments:
            top {float} -- Top coordinate
            left {float} -- Left coordinate

        Keyword Arguments:
            width {int} -- Width of player (default: {100})
            height {int} -- Height of player (default: {5})
            speed {float} -- Horizontal speed of player (default: {500})
        """
        self.speed = speed

        self._top = top
        self._left = left
        self._rect = pygame.Rect(left, top, width, height)
        self.last_step_collisions = 0
        self.collisions = 0
        self.last_left_collision = self._left
        self.last_top_collision = self._top

    def draw(self, surface: pygame.Surface):
        """Draws the player to the surface

        Arguments:
            surface {pygame.Surface} -- Surface to draw to
        """
        pygame.draw.rect(surface, pygame.Color(0, 0, 255), self._rect)

    def update(self, dt: float, override_player_action: int = None):
        """Updates the player position

        Arguments:
            dt {float} -- Change in time
        """
        direction = None
        if override_player_action is not None:
            if override_player_action == 1:
                direction = -1
            elif override_player_action == 2:
                direction = 1
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                direction = -1
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                direction = 1

        if direction is not None:
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