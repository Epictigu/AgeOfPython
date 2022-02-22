import configparser
import math

from sprite import *
from cache import *
from level import *


class Entity(Sprite):
    def __init__(self, level, pos=(0, 0), name=None):
        parser = configparser.ConfigParser()
        parser.read("entities/" + name + ".entity")

        self.texture_file = parser.get("entity", "texture")
        self.max_health = parser.get("entity", "health")
        self.health = self.max_health
        self.base_damage = parser.get("entity", "damage")
        self.speed = parser.get("entity", "speed")
        self.default_animation = parser.get("entity", "default_animation")
        self.level = level

        super(Entity, self).__init__((0, 0), ENTITY_CACHE[self.texture_file])
        self.pos = pos
        self.move_to_pos = pos

        self.key = {}
        for section in parser.sections():
            if not section == "entity":
                desc = dict(parser.items(section))
                self.key[section] = desc

        self.current_animation = self.key[self.default_animation]
        self.current_frame = int(self.current_animation['start'])
        self.walkwaittime = 0
        self.cell_previous = [[(-1, -1) for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]

        self.blocked_counter = 0
        self.last_requested_position = (-1, -1)

    def _get_pos(self):
        return (self.rect.midbottom[0] + 2 - self.rect[2] / 2) / TILESIZE_SCALED, (self.rect.midbottom[1] + 4 - self.rect[3]) / TILESIZE_SCALED

    def _set_pos(self, pos):
        self.rect.midbottom = pos[0] * TILESIZE_SCALED + self.rect[2] / 2 - 2, pos[1] * TILESIZE_SCALED + self.rect[3] - 4
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def get_actual_pos(self):
        return (self.rect.midbottom[0] + 2 + self.offset[0] - self.rect[2] / 2) / TILESIZE_SCALED, (self.rect.midbottom[1] + 4 + self.offset[1] - self.rect[3]) / TILESIZE_SCALED

    def update(self, *args):
        self.waittime += 1
        if self.waittime == 6:
            self.waittime = 0
            self.animation.__next__()
            self.walkwaittime += 1
            if self.walkwaittime == 2:
                self.walkwaittime = 0
                self.move_to_next_pos()

    def setRunningAnimation(self):
        actual_pos = self.get_actual_pos()
        move_pos = self.cell_previous[int(actual_pos[0])][int(actual_pos[1])]

        if move_pos == (-1, -1):
            self.current_animation = self.key[self.default_animation]
            return

        if move_pos[0] > self.get_actual_pos()[0]:
            self.current_animation = self.key['run_right']
        elif move_pos[0] < self.get_actual_pos()[0]:
            self.current_animation = self.key['run_left']
        elif move_pos[1] > self.get_actual_pos()[1]:
            self.current_animation = self.key['run_down']
        elif move_pos[1] < self.get_actual_pos()[1]:
            self.current_animation = self.key['run_up']

    def move_to_next_pos(self):
        actual_pos = self.get_actual_pos()
        if self.cell_previous[int(actual_pos[0])][int(actual_pos[1])] != (-1, -1):
            new_pos = self.cell_previous[int(actual_pos[0])][int(actual_pos[1])]
            if not self.level.is_blocking(new_pos[0], new_pos[1]):
                self.pos = (new_pos[0] - self.offset[0] / TILESIZE_SCALED, new_pos[1] - self.offset[1] / TILESIZE_SCALED)
                self.blocked_counter = 0
            else:
                self.blocked_counter += 1
                if self.blocked_counter >= 5:
                    self.calc_path(self.last_requested_position)

        self.setRunningAnimation()

    def stand_animation(self):
        while True:
            self.current_frame += 1
            if self.current_frame > int(self.current_animation['end']) or self.current_frame < int(self.current_animation['start']):
                self.current_frame = int(self.current_animation['start'])
            self.image = self.frames[self.current_frame][0]
            yield None
            yield None

    def go_to(self, pos):
        self.calc_path(pos)
        self.setRunningAnimation()

    def calc_path(self, pos):
        self.last_requested_position = pos

        open_fields = [pos]
        cell_count = [[-1 for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]
        cell_previous = [[(-1, -1) for i in range(GAME_SIZE)] for j in range(GAME_SIZE)]
        cell_count[pos[0]][pos[1]] = 0

        if self.level.is_blocking(pos[0], pos[1]):
            open_fields.clear()

        while open_fields:
            cur_pos = open_fields.pop(0)

            neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for neighbor in neighbors:
                n_pos = (cur_pos[0] + neighbor[0], cur_pos[1] + neighbor[1])
                if not self.level.is_valid_point(n_pos):
                    continue

                if self.level.is_blocking(n_pos[0], n_pos[1]) and n_pos != self.get_actual_pos():
                    continue

                dist = cell_count[cur_pos[0]][cur_pos[1]] + 1
                old_dist = cell_count[n_pos[0]][n_pos[1]]
                if old_dist > dist or old_dist == -1:
                    cell_count[n_pos[0]][n_pos[1]] = dist
                    cell_previous[n_pos[0]][n_pos[1]] = cur_pos

                    if n_pos == self.pos:
                        open_fields.clear()
                        break
                    open_fields.append(n_pos)
        self.cell_previous = cell_previous


