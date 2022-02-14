import configparser
import random
import pygame as py
import pygame.sprite

from entity import *
from settings import *
from cache import *


class Level(object):
    def __init__(self, filename="level.map"):
        self.map = [['.' for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read("levels/" + filename)
        self.tileset = parser.get("level", "tileset")

        random.seed()

        for y in range(GAME_SIZE):
            line = ''
            for x in range(GAME_SIZE):
                if (x > 0 and self.map[x - 1] == 'g') or (y > 0 and self.map[y - 1][x] == 'g') or ((x > 0 and y > 0) and self.map[y - 1][x - 1] == 'g'):
                    self.map[y][x] = '.'
                    continue

                if x < GAME_SIZE - 2 and y > 0:
                    if self.map[y - 1][x + 1] == 'g':
                        self.map[y][x] = '.'
                        continue

                if random.randint(1, 20) == 1:
                    self.map[y][x] = 't'
                    continue
                if random.randint(1, 500) == 1:
                    if x < GAME_SIZE - 1 and y < GAME_SIZE - 1:
                        self.map[y][x] = 'g'
                        continue
                self.map[y][x] = '.'

        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.width = len(self.map[0])
        self.height = len(self.map)
        self.items = {}
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if 'sprite' in self.key[c]:
                    self.items[(x, y)] = self.key[c]
        self.camera = Camera(self)

        self.overlays = pygame.sprite.RenderUpdates()

        self.entities = py.sprite.RenderUpdates()
        self.entities.add(Entity((1, 1), "worker"))

        self.sprites = pygame.sprite.RenderUpdates()
        for pos, tile in self.items.items():
            sprite = Sprite(pos, SPRITE_CACHE[tile["sprite"]])
            self.sprites.add(sprite)

        self.overlays_map = {}
        self.image = py.Surface((self.width * TILESIZE_SCALED, self.height * TILESIZE_SCALED))
        self.minimap = py.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        self.tiles = []

    def update(self):
        self.sprites.update()
        self.entities.update()

    def get_tile(self, x, y):
        """Gibt zurück, was an einer bestimmten Position ist."""

        try:
            char = self.map[y][x]
        except IndexError:
            return {}
        try:
            return self.key[char]
        except KeyError:
            return {}

    def get_bool(self, x, y, name):
        """Gibt zurück ob der spezifizierte Flag für die Position gesetzt ist."""

        value = self.get_tile(x, y).get(name)
        return value in (True, 1, 'true', 'yes', 'True', 'Yes', '1', 'on', 'On')

    def is_wall(self, x, y):
        """Ist an dieser Position eine Wand?"""

        return self.get_bool(x, y, 'wall')

    def is_tree(self, x, y):
        """Ist an dieser Position ein Baum?"""

        return self.get_bool(x, y, 'tree')

    def is_blocking(self, x, y):
        """Ist diese Position blockiert?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        return self.get_bool(x, y, 'block')

    def pre_render(self):
        self.tiles = MAP_CACHE[self.tileset]

        overlays_dict = {}
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                try:
                    tile = self.key[c]['tile'].split(',')
                    tile = int(tile[0]), int(tile[1])
                except (ValueError, KeyError):
                    # Default to ground tile
                    tile = 0, 0
                tile_image = self.tiles[tile[0]][tile[1]]
                self.image.blit(tile_image,
                           (map_x * TILESIZE_SCALED, map_y * TILESIZE_SCALED))
                if map_y > 0:
                    if 'overlay' in self.key[c]:
                        overlay = self.key[c]['overlay'].split(',')
                        overlays_dict[(map_x, map_y)] = self.tiles[int(overlay[0])][int(overlay[1])]

        self.overlays = pygame.sprite.RenderUpdates()
        for(x, y), overlay_image in overlays_dict.items():
            overlay = Sprite((x, y), overlay_image)
            overlay.rect = overlay_image.get_rect().move(x * TILESIZE_SCALED, y * TILESIZE_SCALED - TILESIZE_SCALED)
            self.overlays.add(overlay)
            self.overlays_map[(x, y)] = overlay

        self.minimap = py.transform.scale(self.image.copy(), (MINIMAP_SIZE, MINIMAP_SIZE))

        return self.image, self.minimap

    def change_tile(self, pos, tile_key):
        tile = self.key[tile_key]['tile'].split(', ')
        tile = int(tile[0]), int(tile[1])

        tile_image = self.tiles[tile[0]][tile[1]]
        self.image.blit(tile_image, (pos[0] * TILESIZE_SCALED, pos[1] * TILESIZE_SCALED))

        if pos in self.overlays_map:
            self.overlays.remove(self.overlays_map[pos])
        self.map[pos[0]][pos[1]] = tile_key

        if 'overlay' in self.key[tile_key]:
            overlay = self.key[tile_key]['overlay'].split(',')
            overlay_image = self.tiles[int(overlay[0])][int(overlay[1])]
            overlay = Sprite(pos, overlay_image)
            overlay.rect = overlay_image.get_rect().move(pos[0] * TILESIZE_SCALED, pos[1] * TILESIZE_SCALED - TILESIZE_SCALED)
            self.overlays.add(overlay)


class Camera:
    def __init__(self, level):
        self.width = py.display.Info().current_w
        self.height = py.display.Info().current_h

        self.x_offset = 0
        self.y_offset = 0

        self.level = level

    def moveRight(self):
        self.x_offset = self.x_offset + 30
        if self.x_offset + self.width > self.level.width * TILESIZE_SCALED:
            self.x_offset = self.level.width * TILESIZE_SCALED - self.width

    def moveLeft(self):
        self.x_offset = self.x_offset - 30
        if self.x_offset < 0:
            self.x_offset = 0

    def moveDown(self):
        self.y_offset = self.y_offset + 30
        if self.y_offset + self.height > self.level.height * TILESIZE_SCALED:
            self.y_offset = self.level.height * TILESIZE_SCALED - self.height

    def moveUp(self):
        self.y_offset = self.y_offset - 30
        if self.y_offset < 0:
            self.y_offset = 0

    def move(self, middle):
        if middle[0] > self.level.width * TILESIZE_SCALED - self.width / 2:
            middle = (self.level.width * TILESIZE_SCALED - self.width / 2, middle[1])
        if middle[1] > self.level.height * TILESIZE_SCALED - self.height / 2:
            middle = (middle[0], self.level.height * TILESIZE_SCALED - self.height / 2)
        if middle[0] < 0 + self.width / 2:
            middle = (self.width / 2, middle[1])
        if middle[1] < 0 + self.height / 2:
            middle = (middle[0], self.height / 2)

        self.x_offset = middle[0] - self.width / 2
        self.y_offset = middle[1] - self.height / 2
