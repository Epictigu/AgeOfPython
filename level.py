import configparser
import random
import pygame as py
import pygame.sprite

from entity import *
from sprite import *
from settings import *
from cache import *
from building import *
from player import *


class Level(object):
    def __init__(self, filename="level.map"):
        """Funktion um ein Level zu initialiaiseren"""
        self.map = [['.' for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read("levels/" + filename)
        self.tileset = parser.get("level", "tileset")

        self.background_tile = parser.get("level", "background_tile").split(',')
        self.background_tile = (int(self.background_tile[0]), int(self.background_tile[1]))

        self.player = Player()
        self.ai = Player()

        self.width = GAME_SIZE
        self.height = GAME_SIZE

        random.seed()

        self.entities = py.sprite.RenderUpdates()
        self.selected_entities = []
        self.buildings = py.sprite.RenderUpdates()
        self.sprites = pygame.sprite.RenderUpdates()

        self.generate()

        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                self.key[section] = desc
        self.items = {}
        for y, line in enumerate(self.map):
            for x, c in enumerate(line):
                if 'sprite' in self.key[c]:
                    self.items[(x, y)] = self.key[c]
        self.camera = Camera(self)

        for pos, tile in self.items.items():
            sprite = Sprite(pos, SPRITE_CACHE[tile["sprite"]])
            self.sprites.add(sprite)

        self.image = py.Surface((self.width * TILESIZE_SCALED, self.height * TILESIZE_SCALED))
        self.overlay_image = py.Surface((self.width * TILESIZE_SCALED, self.height * TILESIZE_SCALED), pygame.SRCALPHA)
        self.minimap = py.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        self.tiles = []
        self.cut_trees = {}

    def select_entity(self, pos):
        """Funktion zum Auswählen einer einzelnen Entität"""
        self.selected_entities.clear()
        for e in self.entities.sprites():
            if e.owner != self.player:
                continue
            if e.get_actual_pos() == pos:
                self.selected_entities.append(e)

    def select_entities(self, pos1, pos2):
        """Funktion zum Auswählen mehrerer Entitäten"""
        lower_x = pos1[0]
        higher_x = pos2[0]
        if lower_x > higher_x:
            lower_x = pos2[0]
            higher_x = pos1[0]
        lower_y = pos1[1]
        higher_y = pos2[1]
        if lower_y > higher_y:
            lower_y = pos2[1]
            higher_y = pos1[1]

        self.selected_entities.clear()
        for e in self.entities.sprites():
            if e.owner != self.player:
                continue
            e_pos = e.get_actual_pos()
            if lower_x <= e_pos[0] <= higher_x:
                if lower_y <= e_pos[1] <= higher_y:
                    self.selected_entities.append(e)

    def generate(self):
        """Funktion zum Generieren eines Levels"""
        available_pos = []
        for y in range(GAME_SIZE):
            for x in range(GAME_SIZE):
                available_pos.append((y, x))

        for y in range(GAME_SIZE):
            for x in range(GAME_SIZE):
                if y < 4 or y >= GAME_SIZE - 4 or x < 4 or x >= GAME_SIZE - 4 or x * y < 80 or (GAME_SIZE - x) * (GAME_SIZE - y) < 80 or (GAME_SIZE - x) * y < 80 or x * (GAME_SIZE - y) < 80:
                    self.map[y][x] = 't'
                    if (y, x) in available_pos:
                        available_pos.remove((y, x))

        gold_row = [14, int(GAME_SIZE / 2), GAME_SIZE - 15]
        gold_column = [8, int(GAME_SIZE / 2), GAME_SIZE - 9]

        for x in gold_row:
            for y in gold_column:
                self.map[y][x] = 'g'
                for offset_x in range(-10, 12):
                    for offset_y in range(-10, 12):
                        if (x + offset_x, y + offset_y) in available_pos:
                            available_pos.remove((x + offset_x, y + offset_y))

        self.buildings.add(Building(self, self.player, (14, 13), "town_hall"))
        self.buildings.add(Building(self, self.ai, (GAME_SIZE - 15, GAME_SIZE - 14), "town_hall"))

        self.entities.add(Entity(self, self.player, (13, 12), "worker"))
        self.entities.add(Entity(self, self.player, (14, 12), "worker"))
        self.entities.add(Entity(self, self.player, (15, 12), "worker"))
        self.entities.add(Entity(self, self.player, (16, 12), "worker"))

        self.entities.add(Entity(self, self.ai, (GAME_SIZE - 16, GAME_SIZE - 12), "worker"))
        self.entities.add(Entity(self, self.ai, (GAME_SIZE - 15, GAME_SIZE - 12), "worker"))
        self.entities.add(Entity(self, self.ai, (GAME_SIZE - 14, GAME_SIZE - 12), "worker"))
        self.entities.add(Entity(self, self.ai, (GAME_SIZE - 13, GAME_SIZE - 12), "worker"))

        while len(available_pos):
            center_pos = available_pos[random.randint(0, len(available_pos) - 1)]
            center_range = 0
            continue_expanding = True
            while center_range < 10 and (center_range < 5 or random.randint(0, 1) == 0) and continue_expanding:
                new_range = center_range + 1
                for y in range(new_range * -1, new_range + 1):
                    for x in range(new_range * -1, new_range + 1):
                        if (center_pos[0] + y, center_pos[1] + x) not in available_pos:
                            continue_expanding = False
                            break
                    if not continue_expanding:
                        break
                if continue_expanding:
                    center_range = new_range
            if center_range < 3:
                available_pos.remove(center_pos)
                continue
            for y in range(center_range * -1, center_range + 1):
                for x in range(center_range * -1, center_range + 1):
                    available_pos.remove((center_pos[0] + y, center_pos[1] + x))

            width = int(center_range / 2 + random.uniform(0, center_range / 2))
            height = int(center_range / 2 + random.uniform(0, center_range / 2))

            for y in range(height * -1, height + 1):
                for x in range(width * -1, width + 1):
                    if abs(x) == width and abs(y) == height:
                        continue
                    self.map[center_pos[1] + y][center_pos[0] + x] = 't'

        for x in range(GAME_SIZE):
            for y in range(GAME_SIZE):
                if not self.is_blocking(y, x):
                    if self.map[y][x] == 'g' or self.map[y - 1][x - 1] == 'g' or self.map[y - 1][x] == 'g' or self.map[y][x - 1] == 'g':
                        continue
                    if random.randint(0, 20) == 0:
                        self.map[y][x] = 't'

    def update(self):
        """Updatet die Animationen der einzelnen Sprites"""
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

        return self.get_bool(int(x), int(y), 'tree')

    def is_blocking(self, x, y):
        """Ist diese Position blockiert?"""

        if not 0 <= x < self.width or not 0 <= y < self.height:
            return True
        if self.get_bool(x, y, 'block'):
            return True
        for e in self.entities.sprites():
            if e.get_actual_pos()[0] == x and e.get_actual_pos()[1] == y:
                return True
        for s in self.sprites.sprites():
            if s.get_actual_pos()[0] <= x <= s.get_actual_pos()[0] + 1 and s.get_actual_pos()[1] <= y <= s.get_actual_pos()[1] + 1:
                return True
        for b in self.buildings.sprites():
            if b.get_actual_pos()[0] <= x <= b.get_actual_pos()[0] + b.width - 1 and b.get_actual_pos()[1] <= y <= b.get_actual_pos()[1] + b.height - 1:
                return True

        return False

    def pre_render(self):
        """Rendert die Map vor"""
        self.tiles = MAP_CACHE[self.tileset]

        overlays_dict = {}
        for map_y, line in enumerate(self.map):
            for map_x, c in enumerate(line):
                try:
                    tile = self.key[c]['tile'].split(',')
                    tile = int(tile[0]), int(tile[1])
                except (ValueError, KeyError):
                    tile = 0, 0
                tile_image = self.tiles[tile[0]][tile[1]]
                self.image.blit(tile_image,
                           (map_x * TILESIZE_SCALED, map_y * TILESIZE_SCALED))
                if map_y > 0:
                    if 'overlay' in self.key[c]:
                        overlay = self.key[c]['overlay'].split(',')
                        overlays_dict[(map_x, map_y)] = self.tiles[int(overlay[0])][int(overlay[1])]

        for(x, y), overlay_image in overlays_dict.items():
            self.overlay_image.blit(overlay_image, (x * TILESIZE_SCALED, (y - 1) * TILESIZE_SCALED))

        self.minimap = py.transform.scale(self.image.copy(), (MINIMAP_SIZE, MINIMAP_SIZE))

        return self.image, self.overlay_image, self.minimap

    def cut_tree(self, pos):
        """Funktion zur Baum Fällen Interaktion"""
        if self.is_tree(pos[0], pos[1]) and pos not in self.cut_trees:
            self.change_tile(pos, 'd')
            self.cut_trees[pos] = 100
        elif self.is_tree(pos[0], pos[1]):
            tree_count = self.cut_trees[pos]
            tree_count = tree_count - 1
            if tree_count < 1:
                self.change_tile(pos, '.')
            else:
                self.cut_trees[pos] = 100

    def is_occupied(self, pos):
        """Ist ein Feld besetzt?"""
        for e in self.entities:
            if e.get_actual_pos() == pos:
                return True
        return False

    def change_tile(self, pos, tile_key):
        """Ändere das Aussehen an einer bestimmten Position um"""
        old_key = self.map[int(pos[1])][int(pos[0])]

        tile = self.key[tile_key]['tile'].split(', ')
        tile = int(tile[0]), int(tile[1])

        tile_image = self.tiles[tile[0]][tile[1]]
        self.image.blit(tile_image, (pos[0] * TILESIZE_SCALED, pos[1] * TILESIZE_SCALED))

        if 'overlay' in self.key[old_key]:
            py.draw.rect(self.overlay_image, (0, 0, 0, 0), py.Rect(pos[0] * TILESIZE_SCALED, (pos[1] - 1) * TILESIZE_SCALED, TILESIZE_SCALED, TILESIZE_SCALED))
        self.map[int(pos[1])][int(pos[0])] = tile_key

        if 'overlay' in self.key[tile_key]:
            overlay = self.key[tile_key]['overlay'].split(',')
            overlay_image = self.tiles[int(overlay[0])][int(overlay[1])]
            self.overlay_image.blit(overlay_image, (pos[0] * TILESIZE_SCALED, (pos[1] - 1) * TILESIZE_SCALED))

    def is_valid_point(self, pos):
        """Ist der Punkt innerhalb des Spielfeldles?"""
        if 0 <= pos[0] < GAME_SIZE and 0 <= pos[1] < GAME_SIZE:
            return True
        return False


class Camera:
    def __init__(self, level):
        """Initialisierung einer Kamera"""
        self.width = py.display.Info().current_w
        self.height = py.display.Info().current_h - MINIMAP_SIZE - 32

        self.x_offset = 0
        self.y_offset = 0

        self.level = level

    def moveRight(self):
        """Bewege Kamera nach Rechts"""
        self.x_offset = self.x_offset + 30
        if self.x_offset + self.width > self.level.width * TILESIZE_SCALED:
            self.x_offset = self.level.width * TILESIZE_SCALED - self.width

    def moveLeft(self):
        """Bewege Kamera nach Links"""
        self.x_offset = self.x_offset - 30
        if self.x_offset < 0:
            self.x_offset = 0

    def moveDown(self):
        """Bewege Kamera nach Unten"""
        self.y_offset = self.y_offset + 30
        if self.y_offset + self.height > self.level.height * TILESIZE_SCALED:
            self.y_offset = self.level.height * TILESIZE_SCALED - self.height

    def moveUp(self):
        """Bewege Kamera nach Oben"""
        self.y_offset = self.y_offset - 30
        if self.y_offset < 0:
            self.y_offset = 0

    def move(self, middle):
        """Bewege Kamera an eine bestimmte Stelle, mithilfe Mittelpunkt"""
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
