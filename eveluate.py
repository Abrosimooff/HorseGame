
from base import Player, EvaluateCtx
from positions import PositionLogic


class IEvaluateIndex:
    """Показатель/Критерий"""

    def __init__(self, logic: PositionLogic):
        self.logic = logic

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        raise NotImplementedError


# todo близость к пустым финишным клеткам

class DangerPositionsEvaluateIndex(IEvaluateIndex):
    """Оценка позиций под угрозой сруба"""

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        dangers = self.logic.get_danger_positions(player)
        score = len(dangers) * 100

        # todo продумать большой вес, чтобы обязательно рубить (доработка get_danger_positions)

        # Если следующий ход компьютера - то чем больше очков, тем лучше! Под угрозу ставим соперника
        if ctx.next_step_player.is_computer:
            return score
        else:  # Если следующий ход пользователя - то чем меньше очков, тем лучше! Под угрозой мы
            return - score


class TotalCountEvaluateIndex(IEvaluateIndex):
    """ Оценка количества коней (0 - 100)  """
    max = 8

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        return len(self.logic.get_player_positions(player)) / 8 * 100.0


class HomeTotalCountEvaluateIndex(IEvaluateIndex):
    """Оценка количества коней на домашнем месте (0 - 100)"""
    max = 8

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        positions = self.logic.get_player_positions(player)
        # колонки, которые закрывают домашние позиции
        home_columns = [column_index for line_index, column_index in positions if line_index == player.home_line]

        # две крайние позиции весят меньше, т.к их прикрывают соседи (предположение)
        score_column_map = {0: 10, 1: 10, 2: 15, 3: 15, 4: 15, 5: 15, 6: 10, 7: 10}
        return sum([score_column_map.get(column_index) for column_index in home_columns])


class FinishTotalCountEvaluateIndex(IEvaluateIndex):
    """Оценка близости коней к финишному месту"""
    SCORE_LINE_MAP = {0: 1000, 1: 900, 2: 700, 3: 500, 4: 200, 5: 100, 6: 0, 7: 0}

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        computer_scores = self.calc_player(player)
        other_scores = self.calc_player(ctx.other_player)
        return computer_scores - other_scores

    def calc_player(self, player: Player):
        # Ищем линии, которые занимают наши пешки. Чем ближе к финишу - тем лучше.
        positions = self.logic.get_player_positions(player)
        lines = [line_index for line_index, column_index in positions]
        scores = 0
        for line in lines:
            diff = abs(player.finish_line - line)
            scores += self.SCORE_LINE_MAP.get(diff, 0)
        return scores


# class OtherPlayerAhtungEvaluateIndex(IEvaluateIndex):
#     """Юзер бликок к победе!!! Ахтунг"""
#
#     def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
#         other_player_positions = self.logic.get_player_positions(ctx.other_player)
#         finished = [pos for pos in other_player_positions if pos[0] == ctx.other_player.finish_line]
#         # Если сейчас противник выиграет
#         if finished:
#             return - 1000
#
#         other_player_legal_moves = self.logic.get_legal_moves(ctx.other_player)
#         finished = [move for move in other_player_legal_moves if move.pos_from[0] == ctx.other_player.finish_line]
#         # Если следующим ходом противник выиграет
#         if finished:
#             return - 1000
#         return 0


class IEvaluateStrategy:

    def __init__(self, logic: PositionLogic):
        self.logic = logic

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        ...


class EvaluateStrategy(IEvaluateStrategy):

    def calc_for(self, player: Player, ctx: EvaluateCtx) -> float:
        """
        Рассчитываемые критерии:
        1. Близость к противоположной стороне (желательно к пустым позициям)
        2. Отсутствие угрозы
        3. Возможность срубить
        4. Количество защитников на исходном месте
        5. Общее количество коней

        :param player:
        :return:
        """
        scores = sum([
            TotalCountEvaluateIndex(self.logic).calc_for(player, ctx),
            HomeTotalCountEvaluateIndex(self.logic).calc_for(player, ctx),
            DangerPositionsEvaluateIndex(self.logic).calc_for(player, ctx),
            FinishTotalCountEvaluateIndex(self.logic).calc_for(player, ctx),
            # OtherPlayerAhtungEvaluateIndex(self.logic).calc_for(player, ctx),
        ])
        return scores
