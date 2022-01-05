import pygame
import pygame.locals
import configparser


class Level(object):
    def load_file(self, filename="level.map"):
        self.map = []
        self.key = {}
        parser = configparser.ConfigParser()
        parser.read(filename)
        self.tileset = parser.get("level", "tileset")
        self.map = parser.get("level", "map").split("\n")
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
        image = pygame.Surface((self.width * MAP_TILE_WIDTH * 4, self.height * MAP_TILE_HEIGHT * 4))
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
                           (map_x * MAP_TILE_WIDTH * 4, map_y * MAP_TILE_HEIGHT * 4))
                if map_y > 0:
                    if self.is_tree(map_x, map_y):
                        overlays[(map_x, map_y)] = tiles[0][3]
                        #image.blit(tiles[0][3], (map_x * MAP_TILE_WIDTH * 4, (map_y - 1) * MAP_TILE_HEIGHT * 4))
        return image, overlays


class Sprite(pygame.sprite.Sprite):
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
        return (self.rect.midbottom[0] - self.rect[2] / 2) / MAP_TILE_WIDTH * 4, (self.rect.midbottom[1] - self.rect[3]) / MAP_TILE_HEIGHT * 4

    def _set_pos(self, pos):
        self.rect.midbottom = pos[0] * MAP_TILE_WIDTH * 4 + self.rect[2] / 2, pos[1] * MAP_TILE_HEIGHT * 4 + self.rect[3]
        self.depth = self.rect.midbottom[1]

    pos = property(_get_pos, _set_pos)

    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
        self.depth = self.rect.midbottom[1]


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
            tile_table = self._load_tile_table(filename, self.width, self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                tile_image = image.subsurface(rect)
                tile_image = pygame.transform.scale(tile_image, (self.width * 4, self.height * 4))
                line.append(tile_image)
        return tile_table


if __name__ == '__main__':
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    MAP_TILE_WIDTH = 8
    MAP_TILE_HEIGHT = 8
    SELECTOR_CACHE = TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)
    MAP_CACHE = TileCache(MAP_TILE_WIDTH, MAP_TILE_HEIGHT)

    level = Level()
    level.load_file('level.map')

    SPRITE_CACHE = TileCache(MAP_TILE_WIDTH * 2, MAP_TILE_HEIGHT * 2)
    sprites = pygame.sprite.RenderUpdates()
    for pos, tile in level.items.items():
        sprite = Sprite(pos, SPRITE_CACHE[tile["sprite"]])
        sprites.add(sprite)

    selector = pygame.sprite.RenderUpdates()
    selector.add(Sprite((0, 0), SELECTOR_CACHE["TileSelector.png"]))

    clock = pygame.time.Clock()

    background, overlay_dict = level.render()
    overlays = pygame.sprite.RenderUpdates()
    for(x, y), image in overlay_dict.items():
        overlay = pygame.sprite.Sprite(overlays)
        overlay.image = image
        overlay.rect = image.get_rect().move(x * MAP_TILE_WIDTH * 4, y * MAP_TILE_HEIGHT * 4 - MAP_TILE_HEIGHT * 4)
    screen.blit(background, (0, 0))

    overlays.draw(screen)
    pygame.display.flip()

    game_over = False
    while not game_over:
        sprites.clear(screen, background)
        selector.clear(screen, background)

        sprites.update()
        dirty = sprites.draw(screen)
        overlays.draw(screen)

        dirty_selector = selector.draw(screen)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                game_over = True
            elif event.type == pygame.locals.KEYDOWN:
                pressed_key = event.key
            elif event.type == pygame.locals.MOUSEMOTION:
                for s in selector.sprites():
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0] < background.get_rect()[2] and mouse_pos[1] < background.get_rect()[3]:
                        s.pos = (int(mouse_pos[0] / (MAP_TILE_WIDTH * 4)), int(mouse_pos[1] / (MAP_TILE_HEIGHT * 4)))
