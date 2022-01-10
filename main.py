import math

import pygame as py
import pygame.locals
from settings import *
from cache import *
from level import *
from sprite import *
from entity import *


def redraw_selectors():
    for s in selector.sprites():
        mouse_pos = pygame.mouse.get_pos()

        if mouse_pos[0] < MINIMAP_SIZE and mouse_pos[1] > py.display.Info().current_h - MINIMAP_SIZE:
            s.pos = (-1, -1)
        else:
            xpos_offset = level.camera.x_offset % TILESIZE_SCALED
            ypos_offset = level.camera.y_offset % TILESIZE_SCALED

            xpos = int((mouse_pos[0] + xpos_offset) / TILESIZE_SCALED) - xpos_offset / TILESIZE_SCALED
            ypos = int((mouse_pos[1] + ypos_offset) / TILESIZE_SCALED) - ypos_offset / TILESIZE_SCALED
            if xpos >= level.width:
                xpos = level.width - 1
            if ypos >= level.height:
                ypos = level.height - 1
            s.pos = (xpos, ypos)


def move_map(x_pos, y_pos):
    level.camera.move((int(x_pos / MINIMAP_SIZE * level.width * TILESIZE_SCALED), int(y_pos / MINIMAP_SIZE * level.height * TILESIZE_SCALED)))
    move_sprites(sprites)
    move_sprites(overlays)


def check_for_edge():
    mouse_pos = pygame.mouse.get_pos()
    screen_width = py.display.Info().current_w
    screen_height = py.display.Info().current_h

    mouse_edge.clear()
    if mouse_pos[0] <= 10:
        mouse_edge.append(py.K_LEFT)
    elif mouse_pos[0] >= screen_width - 10:
        mouse_edge.append(py.K_RIGHT)

    if mouse_pos[1] <= 5:
        mouse_edge.append(py.K_UP)
    elif mouse_pos[1] >= screen_height - 10:
        mouse_edge.append(py.K_DOWN)


def move_sprites(sprite_group):
    for s in sprite_group:
        s.move((level.camera.x_offset, level.camera.y_offset))


if __name__ == '__main__':
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    level = Level('level.map')

    sprites = pygame.sprite.RenderUpdates()
    for pos, tile in level.items.items():
        sprite = Sprite(pos, SPRITE_CACHE[tile["sprite"]])
        sprites.add(sprite)

    selector = pygame.sprite.RenderUpdates()
    selector.add(Sprite((0, 0), SELECTOR_CACHE["TileSelector.png"]))

    clock = pygame.time.Clock()

    background, overlay_dict, minimap = level.render()
    overlays = pygame.sprite.RenderUpdates()
    for(x, y), image in overlay_dict.items():
        overlay = Sprite((x, y), image)
        overlay.rect = image.get_rect().move(x * TILESIZE_SCALED, y * TILESIZE_SCALED - TILESIZE_SCALED)
        overlays.add(overlay)

    minimap_distance = py.display.Info().current_h - MINIMAP_SIZE

    Entity((0, 0), None, "worker")

    pressed_keys = []
    mouse_edge = []
    game_over = False
    minimap_pressed = False

    while not game_over:
        screen.blit(background, (level.camera.x_offset * -1, level.camera.y_offset * -1))

        sprites.update()

        sprites.draw(screen)
        overlays.draw(screen)
        selector.draw(screen)

        screen.blit(minimap, (0, minimap_distance))

        minimap_x = (py.display.Info().current_w / background.get_width() * level.camera.x_offset) / py.display.Info().current_w * MINIMAP_SIZE
        minimap_y = (py.display.Info().current_h / background.get_height() * level.camera.y_offset) / py.display.Info().current_h * MINIMAP_SIZE
        minimap_width = (py.display.Info().current_w / background.get_width() * (level.camera.x_offset + py.display.Info().current_w) / py.display.Info().current_w * MINIMAP_SIZE - minimap_x)
        minimap_height = (py.display.Info().current_h / background.get_height() * (level.camera.y_offset + py.display.Info().current_h) / py.display.Info().current_h * MINIMAP_SIZE - minimap_y)

        py.draw.rect(screen, py.Color(255, 255, 255), (minimap_x, minimap_y + minimap_distance, minimap_width, minimap_height), 1)

        pygame.display.flip()
        clock.tick(60)

        if pressed_keys or mouse_edge:
            if py.K_UP in pressed_keys or py.K_UP in mouse_edge:
                level.camera.moveUp()
            if py.K_DOWN in pressed_keys or py.K_DOWN in mouse_edge:
                level.camera.moveDown()
            if py.K_LEFT in pressed_keys or py.K_LEFT in mouse_edge:
                level.camera.moveLeft()
            if py.K_RIGHT in pressed_keys or py.K_RIGHT in mouse_edge:
                level.camera.moveRight()
            redraw_selectors()
            move_sprites(sprites)
            move_sprites(overlays)

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                game_over = True
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == py.K_UP or event.key == py.K_DOWN or event.key == py.K_LEFT or event.key == py.K_RIGHT:
                    pressed_keys.append(event.key)
            elif event.type == pygame.locals.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)
            elif event.type == pygame.locals.MOUSEMOTION:
                redraw_selectors()
                if minimap_pressed:
                    x_pos = event.pos[0]
                    y_pos = event.pos[1] - (py.display.Info().current_h - MINIMAP_SIZE)
                    move_map(x_pos, y_pos)
                else:
                    check_for_edge()
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                if event.pos[1] >= py.display.Info().current_h - MINIMAP_SIZE and event.pos[0] <= MINIMAP_SIZE:
                    x_pos = event.pos[0]
                    y_pos = event.pos[1] - (py.display.Info().current_h - MINIMAP_SIZE)
                    move_map(x_pos, y_pos)
                    minimap_pressed = True
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                if minimap_pressed:
                    minimap_pressed = False


