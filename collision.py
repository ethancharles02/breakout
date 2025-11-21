from breakout_ball import BreakoutBall
from breakout_block import BreakoutBlock
from breakout_player import BreakoutPlayer
from breakout_rectangle import BreakoutRectangle
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from enum import Enum
import math

class CollisionType(Enum):
    X = 0
    Y = 1
    CORNER = 2

class CollisionInfo:
    def __init__(self,
                 is_collision: bool = None,
                 t_impact: float = None,
                 contact_point: list[float] = None,
                 unit_vector: float = None,
                 collision_type: CollisionType = None):
        self.is_collision = is_collision
        self.t_impact = t_impact
        self.contact_point = contact_point
        self.unit_vector = unit_vector
        self.collision_type = collision_type

class CollisionGrid:
    def __init__(self, collision_grid_shape: tuple[int], width: int, height: int):
        """The collision grid is an optimization tool that removes the need to
        check for collision between all objects. Instead, the object will look
        to its nearest grid neighbors to check for collision

        Arguments:
            collision_grid_shape {tuple[int]} -- The shape of the grid (x, y)
            width {int} -- Width of the screen
            height {int} -- Height of the screen
        """
        self.collision_grid_shape = collision_grid_shape
        self.collision_grid = [[set() for _ in range(collision_grid_shape[1])] for _ in range(collision_grid_shape[0])]
        self.grid_dx = width / collision_grid_shape[0]
        self.grid_dy = height / collision_grid_shape[1]
        # Dictionary for holding object data of left, right, top, and bottom
        # locations on the grid
        self.obj_dict = {}

    def is_obj_boundary_changed(self, rectangle: BreakoutRectangle,
                                left: int, right: int,
                                top: int, bot: int) -> bool:
        """Checks whether the given object has a changed boundary in the collision
        grid. Coordinates are all inclusive

        Arguments:
            rectangle {BreakoutRectangle} -- Rectangle object to check
            left {int} -- left coordinate
            right {int} -- right coordinate
            top {int} -- top coordinate
            bot {int} -- bottom coordinate

        Returns:
            bool -- Whether or not the boundary changed and needs to be updated
        """
        is_not_changed = \
            self.obj_dict[rectangle][0] == left and \
            self.obj_dict[rectangle][1] == right and \
            self.obj_dict[rectangle][2] == top and \
            self.obj_dict[rectangle][3] == bot
        return not is_not_changed

    def is_coord_in_range(self, coord: tuple[int],
                                left: int, right: int,
                                top: int, bot: int) -> bool:
        """Checks if a coordinate is in a range (all inclusive)

        Arguments:
            coord {tuple[int]} -- Coordinate
            left {int} -- Left
            right {int} -- Right
            top {int} -- Top
            bot {int} -- Bottom

        Returns:
            bool -- In range or not
        """
        return left <= coord[0] <= right and top <= coord[1] <= bot

    def get_possible_collisions(self, ball: BreakoutBall, manhat_dist: int = 1) -> set:
        """Gets a set of objects that the given ball could collide with

        Arguments:
            ball {BreakoutBall} -- Object to check for

        Keyword Arguments:
            manhat_dist {int} -- Distance around the grid to search (1 means it
            searches in a 3x3 grid) (default: {1})

        Returns:
            set -- Set of possible collision objects
        """
        ball_grid_x = int(ball.x // self.grid_dx)
        ball_grid_y = int(ball.y // self.grid_dy)
        # Clamps them to the expected bounds
        left = self.clamp_val(ball_grid_x - manhat_dist, True)
        right = self.clamp_val(ball_grid_x + manhat_dist, True)
        top = self.clamp_val(ball_grid_y - manhat_dist, False)
        bot = self.clamp_val(ball_grid_y + manhat_dist, False)

        possible_collisions = set()
        for x in range(left, right + 1):
            for y in range(top, bot + 1):
                possible_collisions.update(self.collision_grid[x][y])

        return possible_collisions

    def remove(self, rectangle: BreakoutRectangle):
        """Removes a given rectangle from the collision grid

        Arguments:
            rectangle {BreakoutRectangle} -- Rectangle to remove
        """
        if rectangle in self.obj_dict:
            for x in range(self.obj_dict[rectangle][0], self.obj_dict[rectangle][1] + 1):
                for y in range(self.obj_dict[rectangle][2], self.obj_dict[rectangle][3] + 1):
                    self.collision_grid[x][y].remove(rectangle)

    def clamp_val(self, val: int, is_x: bool) -> int:
        """Clamps the value to be within the collision grid bounds

        Arguments:
            val {int} -- Value to clamp
            is_x {bool} -- Whether or not it is an x coordinate

        Returns:
            int -- Clamped value
        """
        if is_x:
            val = min(max(val, 0), self.collision_grid_shape[0] - 1)
        else:
            val = min(max(val, 0), self.collision_grid_shape[1] - 1)
        return val

    def update_grid_for_rect(self, rectangle: BreakoutRectangle):
        """Updates the grid with the given rectangle, adding it to any corresponding
        grid spaces

        Arguments:
            rectangle {BreakoutRectangle} -- Rectangle to update the grid for
        """
        left = int(rectangle.left // self.grid_dx)
        right = math.ceil((rectangle.left + rectangle.width) / self.grid_dx)
        top = int(rectangle.top // self.grid_dy)
        bot = math.ceil((rectangle.top + rectangle.height) / self.grid_dy)
        left = self.clamp_val(left, True)
        right = self.clamp_val(right, True)
        top = self.clamp_val(top, False)
        bot = self.clamp_val(bot, False)

        # If it is already in the dictionary, check if it needs to be updated
        if rectangle in self.obj_dict:
            if self.is_obj_boundary_changed(rectangle, left, right, top, bot):
                left_min = min(left, self.obj_dict[rectangle][0])
                right_max = max(right, self.obj_dict[rectangle][1])
                top_min = min(top, self.obj_dict[rectangle][2])
                bot_max = max(bot, self.obj_dict[rectangle][3])
            else:
                return
        else:
            left_min = left
            right_max = right
            top_min = top
            bot_max = bot
            self.obj_dict[rectangle] = [0, 0, 0, 0]

        # Add/remove the object from the affected area
        for x in range(left_min, right_max + 1):
            for y in range(top_min, bot_max + 1):
                # Goes through the whole affected area and adds rectangles to
                # the new area while removing them from the old area
                if self.is_coord_in_range((x, y), left, right, top, bot):
                    self.collision_grid[x][y].add(rectangle)
                elif rectangle in self.collision_grid[x][y]:
                    self.collision_grid[x][y].remove(rectangle)

        self.obj_dict[rectangle][0] = left
        self.obj_dict[rectangle][1] = right
        self.obj_dict[rectangle][2] = top
        self.obj_dict[rectangle][3] = bot

class CollisionManager:
    def __init__(self, player: BreakoutPlayer, balls: list[BreakoutBall],
                 blocks: list[BreakoutBlock], collision_grid_shape: tuple[int]):
        """The collision manager is the main class for handling collision

        Arguments:
            player {BreakoutPlayer} -- Player
            balls {list[BreakoutBall]} -- List of balls
            blocks {list[BreakoutBlock]} -- List of blocks
            collision_grid_shape {tuple[int]} -- Shape of the collision grid (x, y)
        """
        self.player = player
        self.balls = balls
        self.blocks = blocks
        self.collision_grid = CollisionGrid(collision_grid_shape, SCREEN_WIDTH, SCREEN_HEIGHT)
        for block in blocks:
            self.collision_grid.update_grid_for_rect(block)

    def _find_corner_collision(self, p0: list[float], v: list[float],
                               corner: list[float], radius: float, dt: float) -> tuple[float, tuple[float], tuple[float]]:
        """Finds the time, location, and relative angle of collision

        Arguments:
            p0 {list[float]} -- Start point to check from
            v {list[float]} -- Velocity of the point
            corner {list[float]} -- Corner to check collision with
            radius {float} -- Radius of the ball
            dt {float} -- Change in time from starting point to ending point

        Returns:
            tuple[float, tuple[float], tuple[float]] -- Time, location, relative
            angle towards the collision point
        """
        x0, y0 = p0
        dx, dy = v
        xc, yc = corner

        # Compute coefficients for: ‖(p0 + v·t) – corner‖^2 = r^2
        xn = x0 - xc
        yn = y0 - yc

        a = dx*dx + dy*dy
        b = 2 * (dx*xn + dy*yn)
        c = xn*xn + yn*yn - radius*radius

        # Solve quadratic a t^2 + b t + c = 0
        discriminant = b*b - 4*a*c

        if a == 0:
            # The ball is not moving (or moving zero speed) – no “sweep”
            return None, None, None

        if discriminant < 0:
            # no real roots → no time when centre is exactly radius away from corner
            return None, None, None

        sqrtD = math.sqrt(discriminant)
        t1 = (-b - sqrtD) / (2*a)
        t2 = (-b + sqrtD) / (2*a)

        if math.isclose(t1, 0, abs_tol=1e-13):
            t1 = dt
        elif math.isclose(t2, 0, abs_tol=1e-13):
            t2 = dt

        # We want the **earliest** t in [0, dt]
        t_candidates = [t for t in (t1, t2) if 0 <= t <= dt]
        if not t_candidates:
            return None, None, None

        t_impact = min(t_candidates)

        # Centre position at impact
        cx_imp = x0 + dx * t_impact
        cy_imp = y0 + dy * t_impact
        # centre_imp = (cx_imp, cy_imp)

        # Normal vector from corner to centre at impact
        nx = cx_imp - xc
        ny = cy_imp - yc
        length_n = math.hypot(nx, ny)
        if length_n == 0:
            # Exactly overlapping corner centre (rare edge‐case) — normal undefined
            # You may choose some fallback normal (e.g., invert velocity) or skip
            raise NotImplementedError

        # Unit normal
        unx = nx / length_n
        uny = ny / length_n
        unit_vector = (unx, uny)

        # Contact point on the ball/wall boundary: corner + radius * unit‐normal
        contact_x = xc + unx * radius
        contact_y = yc + uny * radius
        contact_point = (contact_x, contact_y)

        return t_impact, contact_point, unit_vector

    def _handle_corner_collision(self, ball: BreakoutBall, collision_info: CollisionInfo, dt: float):
        """Updates a ball based on the given collision info from a corner
        collision

        Arguments:
            ball {BreakoutBall} -- Ball to update
            collision_info {CollisionInfo} -- Collision info
            dt {float} -- Time change since x0, y0 of the ball
        """
        # Get the angle info
        angle = math.atan2(collision_info.unit_vector[1], collision_info.unit_vector[0])
        ball_angle = (math.atan2(ball.dy, ball.dx)) + math.pi
        angle_diff = angle - ball_angle
        new_angle = angle + angle_diff

        # Set ball coords and speeds
        ball.x = collision_info.contact_point[0]
        ball.y = collision_info.contact_point[1]
        ball_speed = ball.get_speed()
        ball.dx = math.cos(new_angle) * ball_speed
        ball.dy = math.sin(new_angle) * ball_speed

        # Update the ball for the leftover time since its impact
        time_left = dt - collision_info.t_impact
        ball.update(time_left)

    def _handle_block_collision(self, ball: BreakoutBall,
                                block: BreakoutBlock, dt: float) -> bool:
        """Handles general collisions between and given ball and block

        Arguments:
            ball {BreakoutBall} -- Ball to handle
            block {BreakoutBlock} -- Block to handle
            dt {float} -- Change in time since x0, y0 of the ball

        Returns:
            bool -- Whether or not there was a collision and the block should be
            deleted
        """
        collision_info = self._check_rect_collision(ball, block, dt)
        delete_block = False
        if collision_info.is_collision:
            time_left = dt - collision_info.t_impact
            # Handle corner collisions
            if collision_info.collision_type == CollisionType.CORNER:
                delete_block = True
                self._handle_corner_collision(ball, collision_info, dt)
            else:
                # Handle normal planar collisions
                coll_x = collision_info.contact_point[0]
                coll_y = collision_info.contact_point[1]
                delete_block = True
                if collision_info.collision_type == CollisionType.X:
                    if ball.x0 < coll_x:
                        ball.dx = -abs(ball.dx)
                    else:
                        ball.dx = abs(ball.dx)
                    ball.x = coll_x
                    ball.y = coll_y
                    ball.update(time_left)
                elif collision_info.collision_type == CollisionType.Y:
                    ball.x = coll_x
                    ball.y = coll_y
                    if ball.y0 < coll_y:
                        ball.dy = -abs(ball.dy)
                    else:
                        ball.dy = abs(ball.dy)
                    ball.update(time_left)
                return True
            # Recurses in the event that a collision update may have immediately
            # led to another collision
            if time_left > 0:
                self.handle_ball_collisions(ball, time_left)
        return delete_block

    def _handle_player_collision(self, ball: BreakoutBall, player: BreakoutPlayer, dt: float):
        """Handles collision between a ball and the player

        Arguments:
            ball {BreakoutBall} -- Ball to check for collision
            player {BreakoutPlayer} -- Player to check for collision
            dt {float} -- Change in time
        """
        collision_info = self._check_rect_collision(ball, player, dt, True)
        # We only care about vertical collisions
        if collision_info.is_collision:
            coll_x = collision_info.contact_point[0]
            coll_y = collision_info.contact_point[1]
            # If the ball hit the top of the player
            time_left = dt - collision_info.t_impact
            if collision_info.collision_type == CollisionType.Y:
                ball_speed = ball.get_speed()
                ball.x = coll_x
                ball.y = coll_y
                # Calculates the x position relative to the player
                rel_x = ball.x - (player.left + player.width / 2)
                angle = math.pi / 4
                # Scales it such the the very left side of the player is -1 and right is 1
                x_scalar = rel_x / (player.width / 2)
                new_angle = (-math.pi / 2) + angle * x_scalar
                # Applies the scalar to the x speed of the ball (hitting the left
                # of the player forces the ball to move left while right moves right)
                ball.dx = math.cos(new_angle) * ball_speed
                ball.dy = math.sin(new_angle) * ball_speed
                ball.update(time_left)

    def _get_collision_type(self, ball: BreakoutBall, rect: BreakoutRectangle,
                            dt: float, is_player: bool = False) -> tuple[CollisionType, tuple[float], float]:
        """Gets the specific type of collision between a ball and rectangle

        Arguments:
            ball {BreakoutBall} -- Ball to get collision type for
            rect {BreakoutRectangle} -- Rectangle
            dt {float} -- Change in time

        Keyword Arguments:
            is_player {bool} -- Whether or not the rectangle is a player
            (default: {False})

        Returns:
            tuple[CollisionType, tuple[float], float] -- Collision type, contact
            point if applicable, exact time of collision relative to x0, y0 if
            applicable
        """
        if ball.dx == 0:
            dtx = -1
        else:
            if ball.x0 < rect.left:
                x_contact = rect.left - ball.radius
            else:
                x_contact = (rect.left + rect.width) + ball.radius
            # Gets the relative time at which the ball would get to that point
            dtx = (x_contact - ball.x0) / (ball.dx)

        if ball.dy == 0:
            dty = -1
        else:
            if ball.y0 < rect.top:
                y_contact = rect.top - ball.radius
            else:
                y_contact = (rect.top + rect.height) + ball.radius
            # Gets the relative time at which the ball would get to that point
            dty = (y_contact - ball.y0) / (ball.dy)

        if is_player:
            if dty >= 0 and ((dtx >= 0 and dty < dtx) or dtx < 0):
                x_contact = ball.x0 + ball.dx * dty
                return CollisionType.Y, (x_contact, y_contact), dty
            return CollisionType.Y, (ball.x, rect.top - ball.radius), dt

        if 0 <= dty <= dt or 0 <= dtx <= dt:
            # The x collision happened first
            if dty < 0 or (dtx < dty and dtx >= 0):
                y_contact = ball.y0 + ball.dy * dtx
                if rect.top <= y_contact <= rect.top + rect.height:
                    return CollisionType.X, (x_contact, y_contact), dtx
                else:
                    return CollisionType.CORNER, (x_contact, y_contact), None
            # The y collision happened first
            elif dty >= 0:
                x_contact = ball.x0 + ball.dx * dty
                if rect.left <= x_contact <= rect.left + rect.width:
                    return CollisionType.Y, (x_contact, y_contact), dty
                else:
                    return CollisionType.CORNER, (x_contact, y_contact), None
            else:
                return CollisionType.CORNER, (None, None), None
        else:
            return CollisionType.CORNER, (None, None), None

    def _check_rect_collision(self, ball: BreakoutBall, rect: BreakoutRectangle,
                              dt: float, is_player: bool = False) -> CollisionInfo:
        """Checks for a collision between ball and rectangle and returns
        CollisionInfo if there is one

        Arguments:
            ball {BreakoutBall} -- Ball to check
            rect {BreakoutRectangle} -- Rectangle to check
            dt {float} -- Change in time

        Keyword Arguments:
            is_player {bool} -- Whether or not the rectangle is a player
            (default: {False})

        Returns:
            CollisionInfo -- Info to return
        """
        ball_in_x_range = ball.x + ball.radius >= rect.left and ball.x - ball.radius <= rect.left + rect.width
        ball_in_y_range = ball.y + ball.radius >= rect.top and ball.y - ball.radius <= rect.top + rect.height
        collision_result = CollisionInfo(contact_point=[0, 0])
        # Gets relative collision point on the ball
        if ball_in_x_range and ball_in_y_range:
            coll_type, coll_coord, t_impact = self._get_collision_type(ball, rect, dt, is_player)
            collision_result.collision_type = coll_type
            if coll_type == CollisionType.X:
                collision_result.is_collision = True
                collision_result.t_impact = t_impact
                collision_result.contact_point = coll_coord
            elif coll_type == CollisionType.Y:
                collision_result.is_collision = True
                collision_result.t_impact = t_impact
                collision_result.contact_point = coll_coord
            else:
                # Loops through each corner of the rectangle to check for
                # collision within time
                top_right = (rect.left + rect.width, rect.top)
                bottom_right = (rect.left + rect.width, rect.top + rect.height)
                top_left = (rect.left, rect.top)
                bottom_left = (rect.left, rect.top + rect.height)
                for corner in [top_right, bottom_right, top_left, bottom_left]:
                    t_impact, contact_point, unit_vector = self._find_corner_collision((ball.x0, ball.y0), (ball.dx, ball.dy), corner, ball.radius, dt)
                    if t_impact is not None:
                        # Saves and checks the previous collision corner. Due to the
                        # collision recursion, this can get triggered again
                        if [corner[0], corner[1]] != ball.last_collision_point:
                            ball.last_collision_point = [corner[0], corner[1]]
                            collision_result.is_collision = True
                            collision_result.t_impact = t_impact
                            collision_result.contact_point = contact_point
                            collision_result.unit_vector = unit_vector
                            return collision_result
        return collision_result

    def handle_ball_collisions(self, ball: BreakoutBall, dt: float):
        """Handles all possible collisions with a given ball, removing blocks
        that it collides with and updating the ball's position and velocity

        Arguments:
            ball {BreakoutBall} -- Ball to handle
            dt {float} -- Change in time
        """
        possible_collisions = self.collision_grid.get_possible_collisions(ball)
        for possible_collision in possible_collisions:
            if isinstance(possible_collision, BreakoutPlayer):
                self._handle_player_collision(ball, possible_collision, dt)
            else:
                result = self._handle_block_collision(ball, possible_collision, dt)
                if result:
                    self.blocks.remove(possible_collision)
                    self.collision_grid.remove(possible_collision)

    def update(self, dt: float):
        """Updates all collision related objects from the given change in time

        Arguments:
            dt {float} -- Change in time
        """
        for block in self.blocks:
            self.collision_grid.update_grid_for_rect(block)
        self.collision_grid.update_grid_for_rect(self.player)

        for ball in self.balls:
            self.handle_ball_collisions(ball, dt)