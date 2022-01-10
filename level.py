import configparser
import random
import pygame as py
from settings import *
from cache import *


class Level(object):
    def __init__(self, filename="level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read("levels/" + filename)
        self.tileset = parser.get("level", "tileset")
        # self.map = parser.get("level", "map").split("\n")

        random.seed()

        for y in range(GAME_SIZE):
            line = ''
            for x in range(GAME_SIZE):
                if (x > 0 and line[x - 1] == 'g') or (y > 0 and self.map[y - 1][x] == 'g') or ((x > 0 and y > 0) and self.map[y - 1][x - 1] == 'g'):
                    line = line + '.'
                    continue

                if x < GAME_SIZE - 2 and y > 0:
                    if self.map[y - 1][x + 1] == 'g':
                        line = line + '.'
                        continue

                if random.randint(1, 20) == 1:
                    line = line + 't'
                    continue
                if random.randint(1, 500) == 1:
                    if x < GAME_SIZE - 1 and y < GAME_SIZE - 1:
                        line = line + 'g'
                        continue
                line = line + '.'
            self.map.append(line)

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

    def render(self):
        wall = self.is_wall
        tiles = MAP_CACHE[self.tileset]
        image = py.Surface((self.width * TILESIZE_SCALED, self.height * TILESIZE_SCALED))
        overlays = {}
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                try:
                    tile = self.key[c]['tile'].split(',')
                    tile = int(tile[0]), int(tile[1])
                except (ValueError, KeyError):
                    # Default to ground tile
                    tile = 0, 0
                tile_image = tiles[tile[0]][tile[1]]
                image.blit(tile_image,
                           (map_x * TILESIZE_SCALED, map_y * TILESIZE_SCALED))
                if map_y > 0:
                    if self.is_tree(map_x, map_y):
                        overlays[(map_x, map_y)] = tiles[0][3]

        minimap = py.transform.scale(image.copy(), (MINIMAP_SIZE, MINIMAP_SIZE))

        return image, overlays, minimap


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
