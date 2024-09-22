from dataclasses import dataclass
from enum import Enum
from typing import NewType, List, Tuple, Optional

BoardPositions = NewType('BoardPositions', List[List[str]])
"""Описание всех позиций на поле """

HorsePosition = NewType('HorsePosition', Tuple[int, int])
"""Позиция пешки на поле"""

__all__ = (
    'BoardPositions',
    'HorsePosition',
    'Player',
    'Color',
    'Move',
    'EvaluateCtx',

    'ClickEvent',
    'PositionFromSavedEvent',
    'UserStepFinishedEvent',
)


class Color(Enum):
    WHITE = 'W'
    BLACK = 'B'


@dataclass
class Player:
    color: Color
    """Цвет игрока"""
    home_line: int
    """Домашняя линия"""
    is_computer: bool
    """Компьютер?"""

    @property
    def finish_line(self):
        return 7 if self.home_line == 0 else 0

    @property
    def opponent_color(self):
        return Color.WHITE if self.color == Color.BLACK else Color.BLACK

    @property
    def verbose_color(self):
        return 'белые' if self.color == Color.WHITE else 'чёрные'


@dataclass
class EvaluateCtx:
    next_step_player: Player
    other_player: Player


@dataclass
class Move:
    """Ход на доске"""
    player: Player
    pos_from: HorsePosition
    pos_to: HorsePosition
    is_damage_to_opponent: Optional[bool] = None
    """Этот ход срубит соперника"""


@dataclass
class ClickEvent:
    """Событие клик по ячейке поля"""
    line: int
    column: int


@dataclass
class PositionFromSavedEvent:
    """Событие - игрок выбрал какой пешкой ходит"""


@dataclass
class UserStepFinishedEvent:
    """Событие - игрок походил"""