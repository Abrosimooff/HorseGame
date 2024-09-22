from typing import List, Optional

import pygame as pg

from base import HorsePosition, BoardPositions, Color
from process import GameProcess
from base import UserStepFinishedEvent, ClickEvent


def get_rect(x, y):
    """Фигура клетки"""
    return x * TILE + 1, y * TILE + 1, TILE - 2, TILE - 2


def get_figure(x, y):
    """Фигура шашки"""
    return x * TILE + 20, y * TILE + 20, 60, 60


def get_legal_point(x, y):
    """Фигура разрешенной точки"""
    return x * TILE + 40, y * TILE + 40, 20, 20


def get_click_mouse_pos(sc) -> Optional[ClickEvent]:
    """подсветить клетку и вернуть клик"""
    x, y = pg.mouse.get_pos()
    grid_x, grid_y = x // TILE, y // TILE
    BLUE = (10, 135, 206, 235)
    # pg.Rect(get_rect(grid_x, grid_y))
    pg.draw.rect(sc, BLUE, get_figure(grid_x, grid_y), 5, border_radius=100)
    # sc.set_alpha(80)
    click = pg.mouse.get_pressed()
    return ClickEvent(line=grid_y, column=grid_x) if click[0] else False


def draw_current_position(sc, grid_y, grid_x):
    BLUE = (10, 135, 206, 235)
    pg.draw.rect(sc, BLUE, get_figure(grid_x, grid_y), 5, border_radius=100)


def draw_legal_moves(sc, positions: List[HorsePosition]):
    BLUE = (10, 135, 206, 235)
    for p in positions:
        pg.draw.rect(sc, BLUE, get_legal_point(p[1], p[0]), 10, border_radius=100)


def draw_board(sc, position: BoardPositions):
    # fill screen
    sc.fill(pg.Color('white'))

    # рисуем поле
    for line_index, line in enumerate(position):
        for column_index, column in enumerate(line):
            # if column == '*':
            pg.draw.rect(sc, pg.Color('DarkKhaki'), get_rect(column_index, line_index))
            if column == Color.WHITE.value:
                pg.draw.rect(sc, pg.Color('white'), get_figure(column_index, line_index), border_radius=100)
            if column == Color.BLACK.value:
                pg.draw.rect(sc, pg.Color('DarkSlateGray'), get_figure(column_index, line_index), border_radius=100)


TILE = 100


def run():
    pg.init()

    cols, rows = 8, 8

    sc = pg.display.set_mode([cols * TILE, rows * TILE])
    clock = pg.time.Clock()

    game = GameProcess()
    game.make_players(player_is_white=True)

    while True:

        draw_board(sc, game.board.position)
        if game._position_from:
            draw_current_position(sc, *game._position_from)
        if game.user_legal_moves:
            draw_legal_moves(sc, game.user_legal_moves)

        clicked_event = get_click_mouse_pos(sc)

        # Обработка события клик
        if clicked_event:
            click_result = game.click_to_tile(HorsePosition((clicked_event.line, clicked_event.column)))
            if click_result:

                # Событие - ход игрока закончен
                if isinstance(click_result, UserStepFinishedEvent):
                    print('Ход совершен')
                    draw_board(sc, game.board.position)
                    # clock.tick(3)

                    game.step_computer()
                    print('Ход компьютером совершен')
                    draw_board(sc, game.board.position)
                    # clock.tick(0)

        if game.is_game_over:
            pg.font.init()
            player_win = game.who_wins(game.board)
            my_font = pg.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render(f'Игра окончена. Победили {player_win.verbose_color}', False, (0, 0, 0))
            sc.blit(text_surface, (100, 100))

        # # pygame necessary lines
        [exit() for event in pg.event.get() if event.type == pg.QUIT]
        pg.display.flip()
        clock.tick(0)


if __name__ == '__main__':
    run()
