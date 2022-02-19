import pygame as py
from settings import *


class Sprite(py.sprite.Sprite):
    def __init__(self, pos=(0, 0), frames=None, framepos=(0, 0)):
        super(Sprite, self).__init__()
        self.frames = frames
        self.animation = self.stand_animation()
        if frames is not None:
            if type(frames) == py.Surface:
                self.image = frames
            else:
                self.image = frames[framepos[0]][framepos[1]]
        self.rect = self.image.get_rect()
        self.offset = (0, 0)
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
        if self.waittime == 6:
            self.waittime = 0
            self.animation.__next__()

    def _get_pos(self):
        return (self.rect.midbottom[0] - self.rect[2] / 2) / TILESIZE_SCALED, (self.rect.midbottom[1] - self.rect[3]) / TILESIZE_SCALED

    def _set_pos(self, pos):
        self.rect.midbottom = pos[0] * TILESIZE_SCALED + self.rect[2] / 2, pos[1] * TILESIZE_SCALED + self.rect[3]
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, offset):
        self.pos = (self.pos[0] - (offset[0] - self.offset[0]) / TILESIZE_SCALED, self.pos[1] - (offset[1] - self.offset[1]) / TILESIZE_SCALED)
        self.offset = offset
