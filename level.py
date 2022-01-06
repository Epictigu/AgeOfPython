import configparser
import random
import pygame as py
from settings import *
from cache import *

class Level(object):
    def load_file(self, filename="level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read("levels/" + filename)
        self.tileset = parser.get("level", "tileset")
        # self.map = parser.get("level", "map").split("\n")

        random.seed()

        for y in range(0, 100):
            line = ''
            for x in range(0, 100):
                if random.randint(1, 20) == 1:
                    line = line + 't'
                else:
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
        return image, overlays
