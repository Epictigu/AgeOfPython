import pygame as py
import pygame.locals
from settings import *
from cache import *
from level import *
from sprite import *


if __name__ == '__main__':
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    level = Level()
    level.load_file('level.map')

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
        overlay.rect = image.get_rect().move(x * TILESIZE_SCALED, y * TILESIZE_SCALED - TILESIZE_SCALED)
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

                    xpos = int(mouse_pos[0] / TILESIZE_SCALED)
                    ypos = int(mouse_pos[1] / TILESIZE_SCALED)
                    if xpos >= level.width:
                        xpos = level.width - 1
                    if ypos >= level.height:
                        ypos = level.height - 1
                    s.pos = (xpos, ypos)
