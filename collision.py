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
        self.collision_grid_shape = collision_grid_shape
        self.collision_grid = [[set() for _ in range(collision_grid_shape[1])] for _ in range(collision_grid_shape[0])]
        self.grid_dx = width / collision_grid_shape[0]
        self.grid_dy = height / collision_grid_shape[1]
        # Dictionary for holding object data of left, right, top, and bottom
        # locations on the grid
        self.obj_dict = {}
    
    def is_obj_boundary_changed(self, rectangle: BreakoutRectangle,
                                left: int, right: int,
                                top: int, bot: int):
        is_not_changed = \
            self.obj_dict[rectangle][0] == left and \
            self.obj_dict[rectangle][1] == right and \
            self.obj_dict[rectangle][2] == top and \
            self.obj_dict[rectangle][3] == bot
        return not is_not_changed
    
    def is_coord_in_range(self, coord: tuple[int],
                                left: int, right: int,
                                top: int, bot: int):
        return left <= coord[0] <= right and top <= coord[1] <= bot
    
    def get_possible_collisions(self, ball: BreakoutBall, manhat_dist: int = 1) -> set:
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
        if rectangle in self.obj_dict:
            for x in range(self.obj_dict[rectangle][0], self.obj_dict[rectangle][1] + 1):
                for y in range(self.obj_dict[rectangle][2], self.obj_dict[rectangle][3] + 1):
                    self.collision_grid[x][y].remove(rectangle)
    
    def clamp_val(self, val: int, is_x: bool) -> int:
        if is_x:
            val = min(max(val, 0), self.collision_grid_shape[0] - 1)
        else:
            val = min(max(val, 0), self.collision_grid_shape[1] - 1)
        return val
    
    def update_grid_for_rect(self, rectangle: BreakoutRectangle):
        left = int(rectangle.left // self.grid_dx)
        right = math.ceil((rectangle.left + rectangle.width) / self.grid_dx)
        top = int(rectangle.top // self.grid_dy)
        bot = math.ceil((rectangle.top + rectangle.height) / self.grid_dy)
        left = self.clamp_val(left, True)
        right = self.clamp_val(right, True)
        top = self.clamp_val(top, False)
        bot = self.clamp_val(bot, False)
        
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
    def __init__(self, player: BreakoutPlayer, balls: list[BreakoutBall], blocks: list[BreakoutBlock], collision_grid_shape: tuple[int]):
        self.player = player
        self.balls = balls
        self.blocks = blocks
        self.collision_grid = CollisionGrid(collision_grid_shape, SCREEN_WIDTH, SCREEN_HEIGHT)
        for block in blocks:
            self.collision_grid.update_grid_for_rect(block)
    
    def _find_corner_collision(self, p0, v, corner, radius, dt):
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
    
    def _handle_corner_collision(self, ball: BreakoutBall, collision_info: CollisionInfo, dt):
        angle = math.atan2(collision_info.unit_vector[1], collision_info.unit_vector[0])
        ball_angle = (math.atan2(ball.dy, ball.dx)) + math.pi
        angle_diff = angle - ball_angle
        new_angle = angle + angle_diff
        ball.x = collision_info.contact_point[0]
        ball.y = collision_info.contact_point[1]
        ball_speed = ball.get_speed()
        ball.dx = math.cos(new_angle) * ball_speed
        ball.dy = math.sin(new_angle) * ball_speed
        time_left = dt - collision_info.t_impact
        ball.update(time_left)
        
    def _handle_rect_collision(self, ball: BreakoutBall, block: BreakoutBlock, dt: float):
        collision_info = self._check_rect_collision(ball, block, dt)
        delete_block = False
        if collision_info.collision_type == CollisionType.CORNER:
            if collision_info.is_collision:
                delete_block = True
                self._handle_corner_collision(ball, collision_info, dt)
        else:
            if collision_info.is_collision:
                coll_x = collision_info.contact_point[0]
                coll_y = collision_info.contact_point[1]
                delete_block = True
                time_left = dt - collision_info.t_impact
                if collision_info.collision_type == CollisionType.X:
                    ball.x = coll_x
                    ball.y = coll_y
                    ball.dx = -ball.dx
                    ball.update(time_left)
                elif collision_info.collision_type == CollisionType.Y:
                    ball.x = coll_x
                    ball.y = coll_y
                    ball.dy = -ball.dy
                    ball.update(time_left)
                return True
        return delete_block
    
    def _handle_player_collision(self, ball: BreakoutBall, player: BreakoutPlayer, dt: float):
        collision_info = self._check_rect_collision(ball, player, dt, True)
        # if collision_info.collision_type == CollisionType.CORNER:
        #     self._handle_corner_collision(ball, collision_info, dt)
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
            # If the ball hit the side of the player
            # elif collision_info.collision_type == CollisionType.X:
            #     ball.x = coll_x
            #     ball.y = coll_y
            #     ball.dx = -ball.dx
            #     ball.update(time_left)
    
    def _get_collision_type(self, ball: BreakoutBall, rect: BreakoutRectangle, dt: float, is_player: bool = False):
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
        
        if dty < 0 and dtx < 0:
            raise Exception("Expected a collision to have happened")

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
            return CollisionType.CORNER, None, None
            
    
    def _check_rect_collision(self, ball: BreakoutBall, rect: BreakoutRectangle, dt: float, is_player: bool = False) -> CollisionInfo:
        ball_in_x_range = ball.x + ball.radius > rect.left and ball.x - ball.radius < rect.left + rect.width
        ball_in_y_range = ball.y + ball.radius > rect.top and ball.y - ball.radius < rect.top + rect.height
        collision_result = CollisionInfo(contact_point=[0, 0])
        # Gets relative collision point on the ball
        if ball_in_x_range and ball_in_y_range:
            # TODO there might be another error related to corners. It might be that it sends it to the corner even when the ball might not be hitting the corner. Check for it
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
                # Top right corner
                if coll_coord[0] > rect.left + rect.width and coll_coord[1] < rect.top:
                    corner = (rect.left + rect.width, rect.top)
                # Bottom right corner
                elif coll_coord[0] > rect.left + rect.width and coll_coord[1] > rect.top + rect.height:
                    corner = (rect.left + rect.width, rect.top + rect.height)
                # Top left corner
                elif coll_coord[0] < rect.left and coll_coord[1] < rect.top:
                    corner = (rect.left, rect.top)
                # Bottom left corner
                elif coll_coord[0] < rect.left and coll_coord[1] > rect.top + rect.height:
                    corner = (rect.left, rect.top + rect.height)
                else:
                    raise Exception("Ball wasn't in corner range?")
                
                distance = math.dist(corner, (ball.x, ball.y))
                if distance < ball.radius:
                    t_impact, contact_point, unit_vector = self._find_corner_collision((ball.x0, ball.y0), (ball.dx, ball.dy), corner, ball.radius, dt)
                    if t_impact is None:
                        return collision_result
                    
                    collision_result.is_collision = True
                    collision_result.t_impact = t_impact
                    collision_result.contact_point = contact_point
                    collision_result.unit_vector = unit_vector
                    return collision_result
        return collision_result
    
    def update(self, dt: float):
        for block in self.blocks:
            self.collision_grid.update_grid_for_rect(block)
        self.collision_grid.update_grid_for_rect(self.player)
        
        for ball in self.balls:
            possible_collisions = self.collision_grid.get_possible_collisions(ball)
            for possible_collision in possible_collisions:
                if isinstance(possible_collision, BreakoutPlayer):
                    self._handle_player_collision(ball, possible_collision, dt)
                else:
                    if self._handle_rect_collision(ball, possible_collision, dt):
                        self.blocks.remove(possible_collision)
                        self.collision_grid.remove(possible_collision)