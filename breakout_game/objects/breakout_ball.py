import pygame
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT
import math

class BreakoutBall:
    def __init__(self, x: float, y: float, dx: float, dy: float, radius: float = 7):
        """Initializes a breakout ball

        Arguments:
            x {float} -- X pos
            y {float} -- Y pos
            dx {float} -- Velocity in x direction
            dy {float} -- Velocity in y direction

        Keyword Arguments:
            radius {float} -- Radius of the ball (default: {7})
        """
        self.radius = radius
        self.x = x
        self.y = y
        self.x0 = x
        self.y0 = y
        self.dx = dx
        self.init_dx = dx
        self.dy = dy
        self.last_collision_point = [-1, -1]
        self.dead = False

    def draw(self, surface: pygame.Surface):
        """Draws the ball to the pygame surface

        Arguments:
            surface {pygame.Surface} -- Surface to draw to
        """
        pygame.draw.circle(surface, pygame.Color(0, 255, 0), (self.x, self.y), self.radius)

    def update(self, dt: float):
        """Updates the balls position and handles collision outside of bounds

        Arguments:
            dt {float} -- Change in time
        """
        self.x0 = self.x
        self.y0 = self.y
        self.x += self.dx * dt
        self.y += self.dy * dt

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
            self.dead = True
            # self.y = SCREEN_HEIGHT - self.radius
            # self.dy = -abs(self.dy)
        return self.dead

    def get_speed(self) -> float:
        """Gets the speed of the ball

        Returns:
            float -- Speed of the ball
        """
        return math.dist((self.dx, self.dy), (0, 0))