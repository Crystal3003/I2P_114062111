from collections import deque
from src.core.managers import GameManager
from src.utils import GameSettings
import pygame as pg
from src.interface.components import TextedButton
from src.utils import Logger, load_tmx, Position
import math
from src.maps.navigate_point import NavigatePoint
from src.data.navigator_menu import NavigatorMenu

class Navigator:
    goals: list[NavigatePoint]
    current_goal: NavigatePoint
    def __init__(self, game_manager: GameManager, goals: NavigatePoint | None=None):
        self.active = False
        self.game_manager = game_manager
        self.goals = goals  # (tile_x, tile_y, name)
        self.btn = []

        self.center_x = GameSettings.SCREEN_WIDTH / 2
        self.center_y = GameSettings.SCREEN_HEIGHT / 2

        self.current_goal = None
        self.path = None
        self.path_surface = None

        self.path_img = pg.image.load("assets/images/UI/custom/marker.png")
        self.path_img = pg.transform.scale(
            self.path_img,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.menu = NavigatorMenu(self.goals)
    # ---------------- BFS ----------------

    def walkable(self, x, y) -> bool:
        rect = pg.Rect(
            x * GameSettings.TILE_SIZE,
            y * GameSettings.TILE_SIZE,
            GameSettings.TILE_SIZE,
            GameSettings.TILE_SIZE
        )
        return not self.game_manager.check_collision(rect)

    def bfs_path(self, start, goal):
        """goal 可以是浮點數 tile 座標"""
        gx, gy = goal
        queue = deque([start])
        visited = {start: None}
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]

        best_tile = None
        best_dist = float('inf')

        while queue:
            x, y = queue.popleft()

            # 用 tile 中心算距離
            tx, ty = x + 0.5, y + 0.5
            dist = abs(tx - gx) + abs(ty - gy)

            # 如果距離 <= 1 視為到達附近
            if dist <= 1:
                best_tile = (x, y)
                break

            if dist < best_dist:
                best_dist = dist
                best_tile = (x, y)

            # 往外擴展
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if self.walkable(nx, ny) and (nx, ny) not in visited:
                    visited[(nx, ny)] = (x, y)
                    queue.append((nx, ny))

        if best_tile is None:
            Logger.debug("Path not found")
            return []

        # 回溯路線
        path = []
        cur = best_tile
        while cur is not None:
            path.append(cur)
            cur = visited[cur]
        path.pop(0)
        return path[::-1]

    # ---------------- UI ----------------

    def generate_buttons(self):
        self.btn = []
        if not self.goals:
            return

        for i, goal in enumerate(self.goals):
            name = goal.name
            btn = TextedButton(
                name, 24,
                self.center_x - 200 + (i % 2) * 200,
                self.center_y - 200 + (i // 2) * 100,
                5,
                lambda g=goal: self.on_click_event(g)
            )
            self.btn.append(btn)

        Logger.debug("Navigator buttons generated")

    def on_click_event(self, goal):
        self.current_goal = goal    # (gx, gy, name)
        self.path = None
        self.path_surface = None

    # ---------------- PATH UPDATE ----------------

    def update(self, dt):
        """只負責更新 path，移動不在這裡處理"""
        self.menu.update(dt)

        selected = self.menu.poll_result()
        if selected:
            self.on_click_event(selected)

        if not self.current_goal:
            return

        # 目前玩家所在 tile
        px = self.game_manager.player.position.x // GameSettings.TILE_SIZE
        py = self.game_manager.player.position.y // GameSettings.TILE_SIZE
        # 如果需要計算路徑
        if self.path is None:
            gx, gy = self.current_goal.x, self.current_goal.y
            self.path = self.bfs_path((px, py), (gx, gy))
            self.build_path_surface()

        # 若走到第一個 tile，移除節點
        if self.path:
            gx, gy = self.path[0]
            delta = 2
            if abs(self.game_manager.player.position.x - gx * GameSettings.TILE_SIZE) <= delta and \
                abs(self.game_manager.player.position.y - gy * GameSettings.TILE_SIZE) <= delta:
                self.path.pop(0)
                self.build_path_surface()

        # 若路徑走完，停止導覽
        if not self.path:
            self.current_goal = None
            self.path_surface = None

    # ---------------- PATH SURFACE ----------------

    def build_path_surface(self):
        if not self.path:
            self.path_surface = None
            return

        tmx = load_tmx(self.game_manager.current_map_key)
        pixel_w = tmx.width * GameSettings.TILE_SIZE
        pixel_h = tmx.height * GameSettings.TILE_SIZE

        surf = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        for x, y in self.path:
            surf.blit(self.path_img, (x * GameSettings.TILE_SIZE,
                                      y * GameSettings.TILE_SIZE))
        self.path_surface = surf

    # ---------------- AUTO MOVE SUPPORT ----------------

    def get_next_pixel_target(self):
        if not self.path:
            return None

        tx, ty = self.path[0]
        target_x = tx * GameSettings.TILE_SIZE
        target_y = ty * GameSettings.TILE_SIZE
        return target_x, target_y

    # ---------------- DRAW ----------------

    def draw(self, screen: pg.Surface):
       self.menu.draw(screen)
    def draw_path(self, screen: pg.Surface, camera):
        if self.path_surface:
            screen.blit(
                self.path_surface,
                camera.transform_position(Position(0, 0))
            )