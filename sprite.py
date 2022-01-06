import pygame as py
from settings import *


class Sprite(py.sprite.Sprite):
    def __init__(self, pos=(0, 0), frames=None):
        super(Sprite, self).__init__()
        self.frames = frames
        self.animation = self.stand_animation()
        self.image = frames[0][0]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.waittime = 0

    def stand_animation(self):
        while True:
            for frame in self.frames:
                self.image = frame[0]
                yield None
                yield None

    def update(self, *args):
        self.waittime += 1
        if self.waittime == 3:
            self.waittime = 0
            self.animation.__next__()

    def _get_pos(self):
        return (self.rect.midbottom[0] - self.rect[2] / 2) / TILESIZE_SCALED, (self.rect.midbottom[1] - self.rect[3]) / TILESIZE_SCALED

    def _set_pos(self, pos):
        self.rect.midbottom = pos[0] * TILESIZE_SCALED + self.rect[2] / 2, pos[1] * TILESIZE_SCALED + self.rect[3]
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]