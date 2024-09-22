from typing import List, Optional
from base import Color, HorsePosition, EvaluateCtx, UserStepFinishedEvent, PositionFromSavedEvent
from board import Board, Move, Player, WHITE_TOP_POSITIONS, BLACK_TOP_POSITIONS
from utils import timeit


class GameProcess:
    PREDICT_LEVEL = 3
    board: Board
    _position_from: Optional[HorsePosition] = None
    user_legal_moves: Optional[List[HorsePosition]] = None

    def get_move_from_player(self, player: Player, legal_moves: List[Move]):
        """Получить ход от пользователя """
        def user_step():
            user_step = input("Вы играете белыми. Введите ваш ход через пробел\n")
            pos_from, pos_to = user_step.split(' ')
            return Move(
                player=player,
                pos_from=HorsePosition((int(pos_from[0]), int(pos_from[1]))),
                pos_to=HorsePosition((int(pos_to[0]), int(pos_to[1]))),
            )

        user_move = user_step()
        while user_move not in legal_moves:
            print('Ход невозможен')
            user_move = user_step()

        print('Ход принят')
        return user_move

    def click_to_tile(self, position: HorsePosition):
        """Ход игрока"""
        user_positions = self.board.logic.get_player_positions(self.other_player)
        if position in user_positions:
            self._position_from = position
            self.user_legal_moves = [move.pos_to for move in self.board.logic.get_legal_moves(self.other_player) if move.pos_from == position]

            print('POSITION FROM SAVED', position)
            return PositionFromSavedEvent()
        elif self._position_from is not None:
            current_move = Move(
                player=self.other_player,
                pos_from=self._position_from,
                pos_to=position
            )
            if current_move in self.board.logic.get_legal_moves(self.other_player):
                self.board = self.board.make_move(move=current_move)
                print('USER STEP FINISHED', current_move)
                self._position_from = None
                self.user_legal_moves = None
                return UserStepFinishedEvent()

    def step_computer(self):
        """Ход компьютера"""
        move = self.get_best_move(depth=self.PREDICT_LEVEL, player=self.computer_player, other_player=self.other_player)
        self.board = self.board.make_move(move)
        print('COMPUTER STEP FINISHED', move)

    def make_players(self, player_is_white: bool):
        if player_is_white:
            self.other_player = Player(color=Color.WHITE, home_line=7, is_computer=False)
            self.computer_player = Player(color=Color.BLACK, home_line=0, is_computer=True)
            self.players = {
                Color.WHITE.value: self.other_player,
                Color.BLACK.value: self.computer_player
            }
            self.board = Board(BLACK_TOP_POSITIONS, self.players)
        else:
            self.other_player = Player(color=Color.BLACK, home_line=7, is_computer=False)
            self.computer_player = Player(color=Color.WHITE, home_line=0, is_computer=True)
            self.players = {
                Color.WHITE.value: self.computer_player,
                Color.BLACK.value: self.other_player
            }
            self.board = Board(WHITE_TOP_POSITIONS, self.players)

    @property
    def is_game_over(self) -> bool:
        """Игра окончена ?"""
        return self.other_player.color.value in self.board.position[self.other_player.finish_line] or \
            self.computer_player.color.value in self.board.position[self.computer_player.finish_line]

    def who_wins(self, board: Board):
        """Кто выиграл? Чей конь перешёл на другую сторону первым?"""
        if self.other_player.color.value in board.position[self.other_player.finish_line]:
            return self.other_player

        if self.computer_player.color.value in board.position[self.computer_player.finish_line]:
            return self.computer_player

    @timeit
    def get_best_move(self, depth: int, player: Player, other_player: Player) -> Optional[Move]:
        """Получить лучший ход для игрока (по глубине)"""
        best_score = float('-inf')
        best_move = None
        for move in self.board.logic.get_legal_moves(player):
            # Вычисляем какой ход принесёт больше очков
            new_board = self.board.make_move(move)
            # score = self.minimax(new_board, depth - 1, player=player, other_player=other_player, calc_for_player=player)

            # на доске new_board учтен гипотетический ход компьютера - поэтому is_maximizing=False
            # ищем максимальное кол-во очков для компьютера на этом ходе
            score = self.minimax_new(new_board, depth - 1, is_maximizing=True)
            # print(score, move.pos_from, '=>', move.pos_to)  # todo выводить потенциальные очки для варианта хода
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    # @timeit
    def minimax_new(self, board: Board, depth: int, is_maximizing: bool) -> float:
        """Алгоритм минимакс - функция, которая рекурсивно анализирует все возможные ходы"""
        if depth == 0 or self.is_game_over:
            return board.evaluate(self.computer_player, EvaluateCtx(
                next_step_player=self.other_player if is_maximizing else self.computer_player,
                other_player=self.other_player
            ))  # всегда считаем значение положения для компьютера

        # меняем is_maximizing т.к следующий ход просчитываем для другого игрока
        is_maximizing = not is_maximizing

        if is_maximizing:
            # ищем максимум очков (для хода компьютера)
            max_eval = float('-inf')
            for move in board.logic.get_legal_moves(self.computer_player):
                new_board = board.make_move(move)
                value = self.minimax_new(new_board, depth=depth-1, is_maximizing=True)
                max_eval = max(max_eval, value)
            return max_eval
        else:
            # ищем минимум очков (для хода игрока)
            min_eval = float('inf')
            for move in board.logic.get_legal_moves(self.other_player):
                new_board = board.make_move(move)
                value = self.minimax_new(new_board, depth=depth-1, is_maximizing=False)
                min_eval = min(min_eval, value)
            return min_eval
