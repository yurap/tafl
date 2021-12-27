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

    @staticmethod
    def third_in_a_row(a: CoordT, b: CoordT) -> CoordT:
        x = b.x - a.x
        y = b.y - a.y
        return Coord(b.x + x, b.y + y)


@dataclass
class Board:
    board: List[List[Square]]

    def __getitem__(self, coord: Coord) -> Square:
        return self.board[coord.x][coord.y]

    def __setitem__(self, coord: Coord, sq: Square) -> None:
        self.board[coord.x][coord.y] = sq

    @property
    def size(self):
        return len(self.board)

    def is_edge(self, coord: Coord):
        return coord.x == 0 or coord.y == 0 \
               or coord.x == self.size - 1 or coord.y == self.size - 1

    def is_valid(self, coord: Coord):
        return 0 <= coord.x < self.size and 0 <= coord.y < self.size

    def neighbors(self, coord: Coord) -> List[Coord]:
        raw = [
            Coord(coord.x + 1, coord.y),
            Coord(coord.x - 1, coord.y),
            Coord(coord.x, coord.y + 1),
            Coord(coord.x, coord.y - 1),
        ]
        return [c for c in raw if self.is_valid(c)]


@dataclass
class Move:
    src: Coord
    dst: Coord

    @staticmethod
    def from_str(move_str: str):
        return Move(Coord.from_str(move_str[0:2]), Coord.from_str(move_str[2:4]))

    def __str__(self):
        return str(self.src) + str(self.dst)


class GameStatus(Enum):
    IN_PROGRESS = 1
    ATTACKERS_WIN = 2
    DEFENDERS_WIN = 3


@dataclass
class Tablut:
    board: Board
    turn_attackers: bool
    history: List[Move] = field(default_factory=list)
    status: GameStatus = GameStatus.IN_PROGRESS

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

    def process_move(self, move: Move):
        self.board[move.dst], self.board[move.src] = self.board[move.src], self.board[move.dst]

    def fetch_captures(self, move: Move) -> List[Coord]:
        captures = []
        is_attacker = self.board[move.dst].is_attacker
        for c in self.board.neighbors(move.dst):
            if self.board[c] == Square.EMPTY or self.board[c].is_attacker == is_attacker:
                continue
            third = Coord.third_in_a_row(move.dst, c)
            if not self.board.is_valid(third):
                captures.append(c)
            elif self.board[third] != Square.EMPTY and self.board[third].is_attacker == is_attacker:
                captures.append(c)
        return captures

    def evaluate_endgame_conditions(self, move: Move, captures: List[Coord]):
        for coord in captures:
            if self.board[coord] == Square.DEFENDER_KING:
                self.status = GameStatus.ATTACKERS_WIN
            self.board[coord] = Square.EMPTY

        if self.board[move.dst] == Square.DEFENDER_KING:
            if self.board.is_edge(move.dst):
                self.status = GameStatus.DEFENDERS_WIN

    def process_captures(self, captures: List[Coord]):
        for coord in captures:
            self.board[coord] = Square.EMPTY

    def move(self, move_str: str) -> None:
        if self.status != GameStatus.IN_PROGRESS:
            raise IllegalMoveException("Game is over")

        if len(move_str) != 4:
            raise IllegalMoveException("Move must consist of 4 characters")

        move = Move.from_str(move_str)
        self.check_move_is_valid(move)
        self.process_move(move)
        self.turn_attackers = not self.turn_attackers
        self.history.append(move)

        captures = self.fetch_captures(move)
        self.evaluate_endgame_conditions(move, captures)
        if self.status == GameStatus.IN_PROGRESS:
            self.process_captures(captures)


class IllegalMoveException(Exception):
    pass


class IllegalSquareException(Exception):
    pass
