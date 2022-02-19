import configparser
import math

from sprite import *
from cache import *
from level import *


class Building(Sprite):
    def __init__(self, level, pos=(0, 0), name=None):
        parser = configparser.ConfigParser()
        parser.read("buildings/" + name + ".building")

        self.name = parser.get("building", "name")
        self.texture_file = parser.get("building", "texture")
        self.max_health = parser.get("building", "health")
        self.health = self.max_health
        self.level = level

        tile = parser.get("building", "tile").split(',')
        tile = int(tile[0]), int(tile[1])
        super(Building, self).__init__((0, 0), TileCache(TILESIZE * int(parser.get("building", "width")), TILESIZE * int(parser.get("building", "height")), (tile[0] * TILESIZE, tile[1] * TILESIZE))[self.texture_file])
        self.pos = pos
        self.move_to_pos = pos
