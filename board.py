import copy
from typing import List, Optional, Dict
from eveluate import EvaluateStrategy
from base import Player, BoardPositions, HorsePosition, Move, Color, EvaluateCtx
from positions import PositionLogic


def switch_color(color: Color):
    """Переключить игрока"""
    return Color.BLACK if color == Color.WHITE else Color.WHITE


WHITE_TOP_POSITIONS = [
    ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
]

BLACK_TOP_POSITIONS = [
    ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['*', '*', '*', '*', '*', '*', '*', '*'],
    ['W', 'W', 'W', 'W', 'W', 'W', 'W', 'W'],
]

"""
Вот основные шаги для реализации алгоритма минимакс в Python:

1. Оценка позиции: Сначала необходимо разработать функцию для оценки текущей позиции на доске. 
Это может включать в себя подсчет количества шашек каждого цвета, а также оценку позиций шашек на доске, 
учитывая их влияние на возможные ходы и защиту. Например, шашки в центре доски могут быть оценены выше, 
чем шашки на краях.
2. Генерация возможных ходов: Для каждой позиции на доске, программа должна генерировать все возможные ходы, 
которые могут быть сделаны. Это включает в себя перемещение шашек вперед, 
а также возможные "съедания" шашек соперника.
3. Рекурсивный анализ: Для каждого возможного хода, программа должна рекурсивно анализировать, 
какие ходы может сделать соперник в ответ, и так далее, до определенной глубины поиска. 
Это позволяет программе "видеть" вперед и выбирать ходы, которые максимизируют ее шансы на победу.
4. Выбор хода: После анализа всех возможных ходов, программа выбирает ход, который, по ее мнению, 
приведет к наилучшему исходу.
"""


class Board:
    """Шахматная Доска"""
    evaluate_strategy_cls: EvaluateStrategy = EvaluateStrategy

    def __init__(self, position: Optional[BoardPositions], players: Dict[Color, Player]):
        self.position = position
        self.players = players
        self.logic = PositionLogic(position, players)

    def evaluate(self, player: Player, ctx: EvaluateCtx) -> float:
        """
        Ценность позиции игрока в этом положении на доске
        """
        return self.evaluate_strategy_cls(self.logic).calc_for(player, ctx)

    def make_move(self, move: Move) -> 'Board':
        """Сделать ход. Создаем новую доску, делаем на ней ход и возвращаем новую доску"""
        new_board = Board(copy.deepcopy(self.position), self.players)  # возможно нужна копия players
        new_board.position[move.pos_from[0]][move.pos_from[1]] = '*'
        new_board.position[move.pos_to[0]][move.pos_to[1]] = move.player.color.value
        return new_board


