import pygame as py
from settings import *


class TileCache:
    def __init__(self, width=32, height=None):
        self.width = width
        self.height = height or width
        self.cache = {}

    def __getitem__(self, filename):
        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table("tiles/" + filename, self.width, self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        image = py.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                tile_image = image.subsurface(rect)
                tile_image = py.transform.scale(tile_image, (self.width * SCALE_FACTOR, self.height * SCALE_FACTOR))
                line.append(tile_image)
        return tile_table


SELECTOR_CACHE = TileCache(TILESIZE, TILESIZE)
MAP_CACHE = TileCache(TILESIZE, TILESIZE)
SPRITE_CACHE = TileCache(TILESIZE * 2, TILESIZE * 2)
ENTITY_CACHE = TileCache(TILESIZE + 1, TILESIZE + 1)
