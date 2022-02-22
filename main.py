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

        if mouse_pos[1] > py.display.Info().current_h - MINIMAP_SIZE or mouse_pos[1] <= 32:
            s.pos = (-1, -1)
        else:
            xpos_offset = level.camera.x_offset % TILESIZE_SCALED
            ypos_offset = level.camera.y_offset % TILESIZE_SCALED

            xpos = int((mouse_pos[0] + xpos_offset) / TILESIZE_SCALED) - xpos_offset / TILESIZE_SCALED
            ypos = int((mouse_pos[1] - 32 + ypos_offset) / TILESIZE_SCALED) - ypos_offset / TILESIZE_SCALED
            if xpos >= level.width:
                xpos = level.width - 1
            if ypos >= level.height:
                ypos = level.height - 1
            s.pos = (xpos, ypos)


def move_map(x_pos, y_pos):
    level.camera.move((int(x_pos / MINIMAP_SIZE * level.width * TILESIZE_SCALED), int(y_pos / MINIMAP_SIZE * level.height * TILESIZE_SCALED)))
    move_sprites(level.sprites)
    move_sprites(level.entities)
    move_sprites(level.buildings)


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


def get_pos(x, y):
    pos_x = level.camera.x_offset + x
    pos_y = level.camera.y_offset + y

    return int(pos_x / TILESIZE_SCALED), int(pos_y / TILESIZE_SCALED)


if __name__ == '__main__':
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    main_surface = py.Surface((screen.get_width(), screen.get_height() - MINIMAP_SIZE - 32))

    py.init()
    font = pygame.font.Font('freesansbold.ttf', 80)
    img = font.render("Karte wird generiert ...", True, (255, 255, 255))

    text_rect = img.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))

    screen.blit(img, text_rect)
    pygame.display.flip()

    level = Level('level.map')

    selector = pygame.sprite.RenderUpdates()
    selector.add(Sprite((0, 0), SELECTOR_CACHE["TileSelector.png"]))

    clock = pygame.time.Clock()
    background, overlay, minimap = level.pre_render()

    pressed_keys = []
    mouse_edge = []
    game_over = False
    minimap_pressed = False
    minimap_distance = py.display.Info().current_h - MINIMAP_SIZE

    background_image = py.Surface((screen.get_width() - MINIMAP_SIZE, MINIMAP_SIZE))
    background_tile_image = level.tiles[level.background_tile[0]][level.background_tile[1]]
    x = 0
    while x < screen.get_width() - MINIMAP_SIZE:
        y = 0
        while y < MINIMAP_SIZE:
            background_image.blit(background_tile_image, (x, y))
            y += TILESIZE_SCALED
        x += TILESIZE_SCALED

    header_image = py.Surface((screen.get_width(), TILESIZE_SCALED))
    x = 0
    while x < screen.get_width():
        header_image.blit(background_tile_image, (x, 0))
        x += TILESIZE_SCALED

    selection_start = (-1, -1)
    selection_end = (-1, -1)

    while not game_over:
        main_surface.blit(background, (level.camera.x_offset * -1, level.camera.y_offset * -1))
        main_surface.blit(overlay, (level.camera.x_offset * -1, level.camera.y_offset * -1))

        level.update()

        level.sprites.draw(main_surface)
        level.buildings.draw(main_surface)
        level.entities.draw(main_surface)
        selector.draw(main_surface)

        screen.blit(minimap, (0, minimap_distance))

        minimap_x = (py.display.Info().current_w / background.get_width() * level.camera.x_offset) / py.display.Info().current_w * MINIMAP_SIZE
        minimap_y = ((py.display.Info().current_h - MINIMAP_SIZE) / background.get_height() * level.camera.y_offset) / (py.display.Info().current_h - MINIMAP_SIZE) * MINIMAP_SIZE
        minimap_width = (py.display.Info().current_w / background.get_width() * (level.camera.x_offset + py.display.Info().current_w) / py.display.Info().current_w * MINIMAP_SIZE - minimap_x)
        minimap_height = ((py.display.Info().current_h - MINIMAP_SIZE) / background.get_height() * (level.camera.y_offset + py.display.Info().current_h - MINIMAP_SIZE) / (py.display.Info().current_h - MINIMAP_SIZE) * MINIMAP_SIZE - minimap_y)

        py.draw.rect(screen, py.Color(255, 255, 255), (minimap_x, minimap_y + minimap_distance, minimap_width, minimap_height), 1)

        screen.blit(main_surface, (0, 32))

        if selection_start != (-1, -1):
            width = selection_end[0] - selection_start[0]
            height = selection_end[1] - selection_start[1]
            x = selection_start[0] - level.camera.x_offset
            y = selection_start[1] - level.camera.y_offset
            if width < 0:
                x = x + width
            if height < 0:
                y = y + height
            py.draw.rect(screen, py.Color(255, 255, 255), (x, y, abs(width), abs(height)), 1)

        screen.blit(background_image, (MINIMAP_SIZE, screen.get_height() - MINIMAP_SIZE))
        screen.blit(header_image, (0, 0))

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
            move_sprites(level.sprites)
            move_sprites(level.entities)
            move_sprites(level.buildings)

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
                    y_pos = event.pos[1] - (py.display.Info().current_h - MINIMAP_SIZE) + 32
                    move_map(x_pos, y_pos)
                else:
                    check_for_edge()
                    if selection_start != (-1, -1):
                        selection_end = (event.pos[0] + level.camera.x_offset, event.pos[1] + level.camera.y_offset)
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                if event.pos[1] >= py.display.Info().current_h - MINIMAP_SIZE and event.pos[0] <= MINIMAP_SIZE:
                    x_pos = event.pos[0]
                    y_pos = event.pos[1] - (py.display.Info().current_h - MINIMAP_SIZE) + 32
                    move_map(x_pos, y_pos)
                    minimap_pressed = True
                elif event.pos[1] <= 32:
                    print("TODO: Menü")
                else:
                    if event.button == 3:
                        for entity in level.selected_entities:
                            e_pos = get_pos(event.pos[0], event.pos[1] - 32)
                            entity.go_to((e_pos[0], e_pos[1]))
                    elif event.button == 1:
                        e_pos = get_pos(event.pos[0], event.pos[1] - 32)
                        selection_start = (event.pos[0] + level.camera.x_offset, event.pos[1] + level.camera.y_offset)
                        selection_end = selection_start
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                if minimap_pressed:
                    minimap_pressed = False
                elif selection_start != (-1, -1):
                    level.select_entities(get_pos(selection_start[0] - level.camera.x_offset, selection_start[1] - level.camera.y_offset - 32), get_pos(selection_end[0] - level.camera.x_offset, selection_end[1] - level.camera.y_offset - 32))
                    selection_start = (-1, -1)


