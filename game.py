from dataclasses import dataclass, field
from typing import TypeVar, List
from enum import Enum


class Square(Enum):
    EMPTY = 1
    ATTACKER_PAWN = 2
    DEFENDER_PAWN = 3
    DEFENDER_KING = 4

    @property
    def is_attacker(self) -> bool:
        return self == Square.ATTACKER_PAWN


CoordT = TypeVar('CoordT', bound='Coord')


@dataclass
class Coord:
    x: int
    y: int

    def __str__(self):
        return chr(ord('a') + self.x) + chr(ord('1') + self.y)

    @staticmethod
    def from_str(coord_str: str) -> CoordT:
        x, y = coord_str
        if 'a' <= x <= 'i' and '1' <= y <= '9':
            return Coord(ord(x) - ord('a'), ord(y) - ord('1'))
        raise IllegalSquareException(f"square {coord_str} is incorrect")

    @staticmethod
    def squares_between(a: CoordT, b: CoordT):
        """generate all squares between given two fields, non-inclusive"""
        cmp = (lambda c: c.y) if a.x == b.x else (lambda c: c.x)
        a, b = min(a, b, key=cmp), max(a, b, key=cmp)
        coord = Coord(a.x, a.y)
        while coord != b:
            if a.x == b.x:
                coord.y += 1
            else:
                coord.x += 1
            if coord != b:
                yield coord


@dataclass
class Board:
    board: List[List[Square]]

    def __getitem__(self, coord: Coord) -> Square:
        return self.board[coord.x][coord.y]

    def __setitem__(self, coord: Coord, sq: Square) -> None:
        self.board[coord.x][coord.y] = sq


@dataclass
class Move:
    src: Coord
    dst: Coord

    @staticmethod
    def from_str(move_str: str):
        return Move(Coord.from_str(move_str[0:2]), Coord.from_str(move_str[2:4]))

    def __str__(self):
        return str(self.src) + str(self.dst)


@dataclass
class Game:
    board: Board
    turn_attackers: bool
    history: List[Move] = field(default_factory=list)

    def check_move_is_valid(self, move: Move) -> None:
        if self.board[move.src] == Square.EMPTY:
            raise IllegalMoveException(f"{move}: cannot move from empty square")
        if self.board[move.dst] != Square.EMPTY:
            raise IllegalMoveException(f"{move}: cannot move to occupied square")
        if move.src.x != move.dst.x and move.src.y != move.dst.y:
            raise IllegalMoveException(f"{move}: can move only vertically and horizontally")
        for coord in Coord.squares_between(move.src, move.dst):
            if self.board[coord] != Square.EMPTY:
                raise IllegalMoveException(f"{move}: cannot jump over {coord}")
        if self.turn_attackers and not self.board[move.src].is_attacker:
            raise IllegalMoveException(f"{move}: it is attacker's turn")
        if not self.turn_attackers and self.board[move.src].is_attacker:
            raise IllegalMoveException(f"{move}: it is defender's turn")

    def move(self, move_str: str) -> None:
        move = Move.from_str(move_str)
        self.check_move_is_valid(move)
        self.board[move.dst], self.board[move.src] = self.board[move.src], self.board[move.dst]
        # todo: check captures
        # todo: check endgame condition
        self.turn_attackers = not self.turn_attackers
        self.history.append(move)


class IllegalMoveException(Exception):
    pass


class IllegalSquareException(Exception):
    pass
