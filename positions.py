from collections import defaultdict
from functools import cached_property
from typing import List, Dict, Tuple

from base import BoardPositions, Player, HorsePosition, Move, Color


class PositionLogic:
    """Расчёты по позиции на доске"""

    # Определение возможных ходов конём
    KNIGHT_STEPS = ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1))

    def __init__(self, position: BoardPositions, players: Dict[Color, Player]):
        self.position = position
        self.players = players

    @cached_property
    def player_positions_map(self) -> Dict[Color, List[HorsePosition]]:
        """Текущие позиции игроков"""
        positions = defaultdict(list)
        for line_index, line in enumerate(self.position):
            for column_index, column_color in enumerate(line):
                if column_color != '*':
                    positions[column_color].append(HorsePosition((line_index, column_index)))
        return positions

    @cached_property
    def legal_moves_map(self) -> Dict[Color, Tuple[Move]]:
        """Возможные ходы игроков"""
        moves = defaultdict(tuple)
        for color in self.player_positions_map.keys():
            player = self.players[color]
            moves[color] = tuple(self._get_legal_moves(player))
        return moves

    def get_player_positions(self, player: Player) -> List[HorsePosition]:
        """Получить все позиции пешек игрока"""
        return self.player_positions_map[player.color.value]

    def get_danger_positions(self, player: Player) -> List[HorsePosition]:
        """Получить все позиции пешек игрока, которые под угрозой сруба"""
        # todo САМАЯ долгая операция
        # return [move.pos_from for move in self.get_legal_moves(player) if move.is_damage_to_opponent]

        danger_positions = []
        for move in self.get_legal_moves(player):
            if self.position[move.pos_to[0]][move.pos_to[1]] == player.opponent_color.value:
                # Проверка, находится ли новая позиция в пределах доски и занята ЧУЖОЙ фигурой
                danger_positions.append(move.pos_from)
        return danger_positions

    def get_legal_moves(self, player: Player) -> Tuple[Move]:
        return self.legal_moves_map[player.color.value]

    def _get_legal_moves(self, player: Player) -> List[Move]:
        """Получить список возможных ходов"""
        knight_moves = []
        current_positions = self.get_player_positions(player)
        for position in current_positions:
            for (i, j) in self.KNIGHT_STEPS:
                try:
                    x, y = position[0] + i, position[1] + j

                    # Если на новой позиции не стоит пешка оппонента - то проверяем можно ли ходить назад
                    if self.position[x][y] != player.opponent_color.value:
                        # Нельзя ходить назад
                        current_line = position[0]
                        if player.finish_line == 7 and x < current_line:
                            continue
                        if player.finish_line == 0 and x > current_line:
                            continue

                    # Проверка, находится ли новая позиция в пределах доски и не занята ли она своей фигурой
                    if 0 <= x < 8 and 0 <= y < 8 and self.position[x][y] != player.color.value:
                        knight_moves.append(
                            Move(
                                player=player,
                                pos_from=position,
                                pos_to=HorsePosition((x, y)),
                                # is_damage_to_opponent=self.position[x][y] == player.opponent_color.value
                            )
                        )
                except IndexError:
                    pass

        return knight_moves
