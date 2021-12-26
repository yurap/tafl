from game import Game, Board, Square, GameStatus
from typing import List
import random
import string


class TaflGameCreator:
    square_types = {
        ' ': Square.EMPTY,
        'x': Square.ATTACKER_PAWN,
        'o': Square.DEFENDER_PAWN,
        'O': Square.DEFENDER_KING,
    }

    @staticmethod
    def create(pos: List[str], turn_back: bool) -> Game:
        b = []
        for horizontal in pos:
            b.append([TaflGameCreator.square(c) for c in horizontal])
        return Game(Board(b), turn_back)

    @staticmethod
    def create_basic() -> Game:
        return TaflGameCreator.create([
            '   xxx   ',
            '    x    ',
            '    o    ',
            'x   o   x',
            'xxooOooxx',
            'x   o   x',
            '    o    ',
            '    x    ',
            '   xxx   ',
        ], True)

    @staticmethod
    def square(c: str) -> Square:
        return TaflGameCreator.square_types[c]


class TaflGamePrinter:
    square_names = {
        Square.EMPTY: ' ',
        Square.ATTACKER_PAWN: 'x',
        Square.DEFENDER_PAWN: 'o',
        Square.DEFENDER_KING: 'O',
    }

    status_names = {
        GameStatus.IN_PROGRESS: 'in progress',
        GameStatus.ATTACKERS_WIN: 'attackers win',
        GameStatus.DEFENDERS_WIN: 'defenders win',
    }

    @staticmethod
    def str(g: Game) -> str:
        s = '    1 2 3 4 5 6 7 8 9\n'
        s += '  ' + '=' * 21 + '\n'
        h = 'a'
        for v in g.board.board:
            s += h + ' | '
            for sq in v:
                s += TaflGamePrinter.square_alias(sq) + ' '
            s += '| ' + h + '\n'
            h = chr(ord(h) + 1)
        s += '  ' + '=' * 21 + '\n'
        s += '    1 2 3 4 5 6 7 8 9\n'
        turn = 'attackers (x)' if g.turn_attackers else 'defenders (o)'
        if g.status != GameStatus.IN_PROGRESS:
            turn = TaflGamePrinter.status_names[g.status]
        last_move = str(g.history[-1]) if len(g.history) else 'none'
        s += f'turn: {turn}\nlast move: {last_move}'

        return s

    @staticmethod
    def square_alias(sq: Square):
        return TaflGamePrinter.square_names[sq]


def get_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))
