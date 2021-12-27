"""
Use this to play tablut against yourself in console
"""
from helpers import TablutGameCreator, TablutGamePrinter
from cmd import Cmd
import os


def clear_console():
    return os.system('cls' if os.name in ('nt', 'dos') else 'clear')


class GameShell(Cmd):
    prompt = 'move: '
    game = None

    def __init__(self):
        super().__init__()
        self.do_new(None)

    def do_new(self, _):
        clear_console()
        self.game = TablutGameCreator.create_basic()
        print(TablutGamePrinter.str(self.game))

    def default(self, move):
        clear_console()
        try:
            self.game.move(move)
        except Exception as e:
            print('Oops: ' + str(e))
        print(TablutGamePrinter.str(self.game))

    @staticmethod
    def do_exit(_):
        return True


if __name__ == '__main__':
    clear_console()
    GameShell().cmdloop()
