import pygame
import math
from .objects.breakout_block import BreakoutBlock
from .objects.breakout_player import BreakoutPlayer
from .objects.breakout_ball import BreakoutBall
from .objects.collision import CollisionManager
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT

class BreakoutGame:
    def __init__(self,
                 display_graphics: bool,
                 blocks: list[BreakoutBlock],
                 balls: list[BreakoutBall],
                 player: BreakoutPlayer,
                 collision_manager: CollisionManager,
                 max_dt: float = None,
                 set_dt: float = None,
                 fps_limit: int = None,
                 print_fps: bool = False
                 ):
        self._display_graphics = display_graphics
        self.blocks = blocks
        self.balls = balls
        self.player = player
        self.collision_manager = collision_manager
        self.max_dt = max_dt
        self.set_dt = set_dt
        self._fps_limit = fps_limit
        self.print_fps = print_fps
        self.game_step = 0
        self.game_over = False
        self.game_win = False
        self.last_steps_block_count = len(blocks)

        pygame.init()
        if self._fps_limit is not None:
            self.clock = pygame.time.Clock()

        if display_graphics:
            self.run_step: function = self.run_step_with_graphics
            # pygame setup
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.run_step: function = self.run_step_no_graphics

        self.running = True

    @property
    def display_graphics(self) -> bool:
        return self._display_graphics

    @display_graphics.setter
    def display_graphics(self, value: bool):
        if value:
            self.run_step: function = self.run_step_with_graphics
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.run_step: function = self.run_step_no_graphics
        self._display_graphics = value

    @property
    def fps_limit(self) -> bool:
        return self._fps_limit

    @fps_limit.setter
    def fps_limit(self, value: int):
        if value is not None:
            self.clock = pygame.time.Clock()
        self._fps_limit = value

    def draw_objects(self):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("white")

        for block in self.blocks:
            block.draw(self.screen)

        self.player.draw(self.screen)

        for ball in self.balls:
            ball.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

    def handle_quit(self):
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        if self.game_over:
            self.running = False

        if self.game_win:
            self.running = False

    def get_dt(self):
        if self.set_dt is None and self._fps_limit is None:
            raise Exception("The game must have either an fps limit or a static change in time (dt)")
        if self._fps_limit is not None:
            dt = self.clock.tick(self._fps_limit) / 1000
        if self.set_dt is not None:
            dt = 0.008
        if self.print_fps:
            if self.game_step % 10 == 0:
                print(f"FPS: {dt**-1}", end="\r")
        if self.max_dt is not None:
            if dt > self.max_dt:
                dt = self.max_dt

        return dt

    def run_updates(self, dt: float, override_player_action: int = None):
        self.player.update(dt, override_player_action)
        ball_deletion_list = []
        for ball in self.balls:
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
            if ball.update(dt):
                ball_deletion_list.append(ball)

        for ball in ball_deletion_list:
            self.balls.remove(ball)

        if len(self.balls) == 0:
            self.game_over = True

        if len(self.blocks) == 0:
            self.game_win = True

        self.last_steps_block_count = len(self.blocks)
        self.player.last_step_collisions = self.player.collisions
        # Checks for collisions between objects
        self.collision_manager.update(dt)

    def run_step_with_graphics(self, override_player_action: int = None):
        self.handle_quit()
        self.draw_objects()
        dt = self.get_dt()
        self.run_updates(dt, override_player_action)
        self.game_step += 1

    def run_step_no_graphics(self, override_player_action: int = None):
        self.handle_quit()
        dt = self.get_dt()
        self.run_updates(dt, override_player_action)
        self.game_step += 1


    def run_till_close(self):
        while self.running:
            self.run_step()
        self.close()

    def close(self):
        pygame.quit()


def main():
    # This limits the game so that low framerate will actually run the game slower
    # max_dt = 0.017
    set_dt = 0.008

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
    balls = [BreakoutBall(ball_x, ball_y, ball_dx + 0.1 * i, ball_dy, ball_radius) for i in range(-num_balls // 2, num_balls // 2, 1)]
    # balls = [BreakoutBall(550, 500, 50, 50, ball_radius)]
    # ball = BreakoutBall()

    collision_grid_shape = (math.ceil(SCREEN_WIDTH / (ball_radius * 2)), math.ceil(SCREEN_HEIGHT / (ball_radius * 2)))
    collision_manager = CollisionManager(player, balls, blocks, collision_grid_shape)

    game = BreakoutGame(True, blocks, balls, player, collision_manager, fps_limit=120)
    # game = BreakoutGame(True, blocks, balls, player, collision_manager, set_dt=set_dt)

    game.run_till_close()