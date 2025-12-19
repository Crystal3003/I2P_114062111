from src.core.managers import GameManager
from src.utils import load_tmx, GameSettings
import pygame as pg
import pytmx

class MiniMap:

    def __init__(self, size: int, game_manager: GameManager):
        self.game_manager = game_manager
        self.SIZE = size

        self.tmxdata = load_tmx(game_manager.current_map_key)
        self.MAP_W = self.tmxdata.width * self.tmxdata.tilewidth
        self.MAP_H = self.tmxdata.height * self.tmxdata.tileheight

        ratio_w = self.SIZE / self.MAP_W
        ratio_h = self.SIZE / self.MAP_H
        self.scale = min(ratio_w, ratio_h)


        self._surface = pg.Surface((self.MAP_W, self.MAP_H), pg.SRCALPHA)
        self._render_all_layers(self._surface)


        self.minimap = pg.transform.scale(
            self._surface,
            (int(self.MAP_W * self.scale), int(self.MAP_H * self.scale))
        )
        self.player = game_manager.player
    def _render_all_layers(self, target: pg.Surface):
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)

    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer):
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image:
                target.blit(image, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))
    def reload(self):
        self.tmxdata = load_tmx(self.game_manager.current_map_key)
        self.MAP_W = self.tmxdata.width * self.tmxdata.tilewidth
        self.MAP_H = self.tmxdata.height * self.tmxdata.tileheight

        ratio_w = self.SIZE / self.MAP_W
        ratio_h = self.SIZE / self.MAP_H
        self.scale = min(ratio_w, ratio_h)

        self._surface = pg.Surface((self.MAP_W, self.MAP_H), pg.SRCALPHA)
        self._render_all_layers(self._surface)


        self.minimap = pg.transform.scale(
            self._surface,
            (int(self.MAP_W * self.scale), int(self.MAP_H * self.scale))
        )
    def update(self, dt):
        pass
    def draw(self, screen: pg.Surface):
        map_x, map_y = 10, 10

        pg.draw.rect(
            screen,
            (0, 0, 0),
            (map_x - 5, map_y - 5, self.MAP_W * self.scale + 10, self.MAP_H * self.scale + 10)
        )
        pg.draw.rect(
            screen,
            (128, 128, 128),
            (map_x - 5, map_y - 5, self.MAP_W * self.scale + 10, self.MAP_H * self.scale + 10), 2
        )
        screen.blit(self.minimap, (map_x, map_y))

        px = map_x + 4 + (self.player.position.x * self.scale / 4)
        py = map_x + 4 + (self.player.position.y * self.scale / 4)
        vision_w = GameSettings.SCREEN_WIDTH * self.scale / 4
        vision_h = GameSettings.SCREEN_HEIGHT * self.scale / 4
        pg.draw.circle(screen, (255, 0, 0), (px, py), 3)
        pg.draw.rect(screen, (255, 255, 0), (px - vision_w / 2, py - vision_h / 2, vision_w, vision_h), 1)