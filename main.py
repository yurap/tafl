from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class Square(Enum):
    EMPTY = 1
    BLACK_PAWN = 2
    WHITE_PAWN = 3
    WHITE_KING = 4


@dataclass
class Board:
    board: List[List[Square]]

    @staticmethod
    def coord(coord: str) -> Tuple[int, int]:
        x, y = coord
        if 'a' <= x <= 'i' and '1' <= y <= '9':
            return ord(x) - ord('a'), ord(y) - ord('1')
        raise IllegalSquareException(f"Oops, square {coord} is incorrect")

    def square(self, coord: str) -> Square:
        x, y = Board.coord(coord)
        return self.board[x][y]

    def update(self, coord: str, sq: Square):
        x, y = Board.coord(coord)
        self.board[x][y] = sq


@dataclass
class TaflGame:
    board: Board

    def __init__(self, board: Board):
        self.board = board

    def move(self, move: str) -> None:
        from_str, to_str = move[0:2], move[2:4]
        from_sq = self.board.square(from_str)
        to_sq = self.board.square(to_str)
        if from_sq == Square.EMPTY or to_sq != Square.EMPTY:
            raise IllegalMoveException
        self.board.update(to_str, from_sq)
        self.board.update(from_str, Square.EMPTY)


class TaflGameCreator:
    square_types = {
        ' ': Square.EMPTY,
        'b': Square.BLACK_PAWN,
        'w': Square.WHITE_PAWN,
        'K': Square.WHITE_KING,
    }

    @staticmethod
    def create(pos: List[str]) -> TaflGame:
        b = []
        for horizontal in pos:
            b.append([TaflGameCreator.square(c) for c in horizontal])
        return TaflGame(Board(b))

    @staticmethod
    def create_basic() -> TaflGame:
        return TaflGameCreator.create([
            '   bbb   ',
            '    b    ',
            '    w    ',
            'b   w   b',
            'bbwwKwwbb',
            'b   w   b',
            '    w    ',
            '    b    ',
            '   bbb   ',
        ])

    @staticmethod
    def square(c: str) -> Square:
        return TaflGameCreator.square_types[c]


class TaflGamePrinter:
    square_names = {
        Square.EMPTY: ' ',
        Square.BLACK_PAWN: 'b',
        Square.WHITE_PAWN: 'w',
        Square.WHITE_KING: 'K',
    }

    @staticmethod
    def str(g: TaflGame) -> str:
        s = '=' * 21 + '\n'
        for v in g.board.board:
            s += '| '
            for sq in v:
                s += TaflGamePrinter.square_alias(sq) + ' '
            s += '|\n'
        s += '=' * 21
        return s

    @staticmethod
    def square_alias(sq: Square):
        return TaflGamePrinter.square_names[sq]


class IllegalMoveException(Exception):
    pass


class IllegalSquareException(Exception):
    pass


if __name__ == '__main__':
    g = TaflGameCreator.create_basic()
    print(TaflGamePrinter.str(g))
    g.move('d1d2')
    print(TaflGamePrinter.str(g))
