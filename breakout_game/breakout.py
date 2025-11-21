import pygame
import math
from .objects.breakout_block import BreakoutBlock
from .objects.breakout_player import BreakoutPlayer
from .objects.breakout_ball import BreakoutBall
from .objects.collision import CollisionManager
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT

def main():
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True
    # This limits the game so that low framerate will actually run the game slower
    max_dt = 0.017

    block_rows = 5
    block_cols = 10
    block_width = 100
    block_height = 30
    dx = (SCREEN_WIDTH - (block_cols * block_width)) / (block_cols + 1)
    dx_width = dx + block_width
    # dy = (height - (block_rows * block_height)) / (block_rows + 1)
    dy = block_height + 50
    blocks = [BreakoutBlock(dy + y * dy, dx + x * dx_width, block_width, block_height) for x in range(block_cols) for y in range(block_rows)]
    # blocks = [BreakoutBlock(SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH // 2, block_width, block_height)]
    # blocks = []

    player_width = 100
    player_height = 5
    player_x = (SCREEN_WIDTH / 2) - (player_width / 2)
    player_y = SCREEN_HEIGHT - (player_height + 10)
    player_speed = 500
    player = BreakoutPlayer(player_y, player_x, player_width, player_height, player_speed)

    ball_radius = 7
    ball_x = SCREEN_WIDTH / 2
    # ball_y = SCREEN_HEIGHT / 2
    ball_y = 600
    # ball_x = player_x - 10
    # ball_y = SCREEN_HEIGHT - 100
    ball_dx = 0
    ball_dy = 100
    num_balls = 10000
    # balls = [BreakoutBall(ball_x, ball_y, ball_dx + 0.1 * i, ball_dy, ball_radius) for i in range(-num_balls // 2, num_balls // 2, 1)]
    balls = [BreakoutBall(550, 500, 50, 50, ball_radius)]
    # ball = BreakoutBall()

    collision_grid_shape = (math.ceil(SCREEN_WIDTH / (ball_radius * 2)), math.ceil(SCREEN_HEIGHT / (ball_radius * 2)))
    collision_manager = CollisionManager(player, balls, blocks, collision_grid_shape)

    # i = 0
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("white")

        # surface = pygame.Surface((100, 100))
        for block in blocks:
            block.draw(screen)

        player.draw(screen)

        for ball in balls:
            ball.draw(screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        dt = clock.tick(120) / 1000
        dt = 0.008
        # i += 1
        # if i % 10 == 0:
        #     print(f"FPS: {dt**-1}", end="\r")

        if dt > max_dt:
            dt = max_dt
        player.update(dt)
        for ball in balls:
            # The ball can't move only up/down or left/right
            if math.isclose(ball.dx, 0, abs_tol=1):
                if ball.dx >= 0:
                    ball.dx = 2
                else:
                    ball.dx = -2
            if math.isclose(ball.dy, 0, abs_tol=1):
                if ball.dy >= 0:
                    ball.dy = 2
                else:
                    ball.dy = -2
            ball.update(dt)
        # Checks for collisions between objects
        collision_manager.update(dt)

    pygame.quit()