import configparser
import math

from sprite import *
from cache import *


class Entity(Sprite):
    def __init__(self, pos=(0, 0), name=None):
        parser = configparser.ConfigParser()
        parser.read("entities/" + name + ".entity")

        self.texture_file = parser.get("entity", "texture")
        self.max_health = parser.get("entity", "health")
        self.health = self.max_health
        self.base_damage = parser.get("entity", "damage")
        self.speed = parser.get("entity", "speed")
        self.default_animation = parser.get("entity", "default_animation")

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
                if self.get_actual_pos() != self.move_to_pos:
                    self.move_to_next_pos()

    def setRunningAnimation(self):
        distance_x = self.move_to_pos[0] - self.get_actual_pos()[0]
        distance_y = self.move_to_pos[1] - self.get_actual_pos()[1]
        if distance_x != 0 or distance_y != 0:
            if abs(distance_x) > abs(distance_y):
                if distance_x > 0:
                    self.current_animation = self.key['run_right']
                else:
                    self.current_animation = self.key['run_left']
            else:
                if distance_y > 0:
                    self.current_animation = self.key['run_down']
                else:
                    self.current_animation = self.key['run_up']
        else:
            self.current_animation = self.key[self.default_animation]

    def move_to_next_pos(self):
        distance_x = self.move_to_pos[0] - self.get_actual_pos()[0]
        distance_y = self.move_to_pos[1] - self.get_actual_pos()[1]
        if abs(distance_x) > abs(distance_y):
            if distance_x > 0:
                self.pos = (self.pos[0] + 1, self.pos[1])
            else:
                self.pos = (self.pos[0] - 1, self.pos[1])
        elif abs(distance_x) < abs(distance_y):
            if distance_y > 0:
                self.pos = (self.pos[0], self.pos[1] + 1)
            else:
                self.pos = (self.pos[0], self.pos[1] - 1)
        else:
            move_x = 0
            move_y = 0
            if distance_x > 0:
                move_x = 1
            elif distance_x < 0:
                move_x = -1

            if distance_y > 0:
                move_y = 1
            elif distance_y < 0:
                move_y = -1

            self.pos = (self.pos[0] + move_x, self.pos[1] + move_y)
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
        self.move_to_pos = pos
        self.setRunningAnimation()
