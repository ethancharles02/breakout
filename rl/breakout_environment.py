import gymnasium as gym
import numpy as np
import math
from gymnasium import spaces
from breakout_game import SCREEN_WIDTH, SCREEN_HEIGHT, BreakoutGame, BreakoutBall, BreakoutBlock, BreakoutPlayer, CollisionManager

class BreakoutEnv(gym.Env):
    def __init__(self, display_graphics: bool = False):
        super().__init__()

        # Observe the x position of the paddle, x, y position of ball, and ball dx/dy
        # We'll normalize observations (positions -> [0,1], velocities -> [-1,1])
        self.ball_start_speed = 200
        low_bounds = np.array([0.0, 0.0, 0.0, -1.0, -1.0], dtype=np.float32)
        high_bounds = np.array([1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=low_bounds, high=high_bounds, dtype=np.float32)

        # Movement is stay, left, or right
        self.action_space = spaces.Discrete(3)

        # Number of steps the simulation can take. At a dt of 0.008, this is
        # approximately a minute
        self.step_limit = 10000
        self.simulation_state = self._setup_simulation(display_graphics)
        # maximum expected ball speed for velocity normalization
        self._max_ball_speed = 800.0

    def _setup_simulation(self, display_graphics: bool = False):
        set_dt = 0.008

        block_rows = 5
        block_cols = 10
        self.total_blocks = block_cols * block_rows
        block_width = 100
        block_height = 30
        dx = (SCREEN_WIDTH - (block_cols * block_width)) / (block_cols + 1)
        dx_width = dx + block_width
        dy = block_height + 30
        blocks = [BreakoutBlock(dy + y * dy, dx + x * dx_width, block_width, block_height) for x in range(block_cols) for y in range(block_rows)]

        player_width = 100
        player_height = 5
        player_x = (SCREEN_WIDTH / 2) - (player_width / 2)
        player_y = SCREEN_HEIGHT - (player_height + 10)
        player_speed = 500
        player = BreakoutPlayer(player_y, player_x, player_width, player_height, player_speed)

        ball_radius = 7
        ball_x = SCREEN_WIDTH / 2
        ball_y = SCREEN_HEIGHT / 2
        ball_dx = 0
        ball_dy = self.ball_start_speed
        balls = [BreakoutBall(ball_x, ball_y, ball_dx, ball_dy, ball_radius)]

        collision_grid_shape = (math.ceil(SCREEN_WIDTH / (ball_radius * 2)), math.ceil(SCREEN_HEIGHT / (ball_radius * 2)))
        collision_manager = CollisionManager(player, balls, blocks, collision_grid_shape)

        game = BreakoutGame(False, blocks, balls, player, collision_manager, set_dt=set_dt)
        if display_graphics:
            game.display_graphics = True
            game.fps_limit = 120
        return game

    def run_visual_simulation(self):
        self.simulation_state.display_graphics = True
        self.simulation_state.run_till_close()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        display_graphics = self.simulation_state.display_graphics
        self.simulation_state = self._setup_simulation(display_graphics)
        observation = self._get_observation()
        info = {}
        return observation, info

    def step(self, action: int):
        self.simulation_state.run_step(action)
        observation = self._get_observation()
        reward = self._calculate_reward()
        terminated = self._is_terminated()
        truncated = self._is_truncated()
        info = {}

        return observation, reward, terminated, truncated, info

    def _get_observation(self):
        paddle_x = float(self.simulation_state.player.left)
        ball_x = 0.0
        ball_y = 0.0
        ball_dx = 0.0
        ball_dy = 0.0
        if len(self.simulation_state.balls) > 0:
            b = self.simulation_state.balls[0]
            ball_x = float(b.x)
            ball_y = float(b.y)
            ball_dx = float(b.dx)
            ball_dy = float(b.dy)

        # Normalize positions to [0,1], velocities to [-1,1]
        norm_paddle_x = paddle_x / float(SCREEN_WIDTH)
        norm_ball_x = ball_x / float(SCREEN_WIDTH)
        norm_ball_y = ball_y / float(SCREEN_HEIGHT)
        maxs = max(self._max_ball_speed, 1.0)
        norm_dx = ball_dx / maxs
        norm_dy = ball_dy / maxs

        return np.array([norm_paddle_x, norm_ball_x, norm_ball_y, norm_dx, norm_dy], dtype=np.float32)

    def _calculate_reward(self):
        # Reward for breaking blocks (sparse), plus shaping terms to encourage
        # tracking the ball and keeping it in play.
        broken_blocks = self.simulation_state.last_steps_block_count - len(self.simulation_state.blocks)
        reward = float(broken_blocks)

        # Small negative per-step penalty to discourage inaction
        reward += -0.001

        # Penalize distance between paddle center and ball x (encourages tracking)
        if len(self.simulation_state.balls) > 0:
            paddle_center = self.simulation_state.player.left + self.simulation_state.player.width / 2
            ball_x = self.simulation_state.balls[0].x
            dist = abs(paddle_center - ball_x)
            reward += -0.01 * dist

        # Terminal rewards
        if self.simulation_state.game_over:
            reward += -5.0
        elif self.simulation_state.game_win:
            reward += 5.0

        return reward

    def _is_terminated(self):
        return self.simulation_state.game_over or self.simulation_state.game_win

    def _is_truncated(self):
        # For a dt of 0.008, this is approximately 1 minute
        return self.simulation_state.game_step >= self.step_limit

    def close(self):
        self.simulation_state.close()