from dataclasses import dataclass


@dataclass
class Message:
    name: str
    chat: str
    text: str

    @staticmethod
    def from_update(update):
        return Message(
            update['message']['chat']['first_name'],
            update['message']['chat']['id'],
            update['message']['text']
        )


class MessageManager:
    def __init__(self, updater):
        self.updater = updater

    def send(self, chat, message, use_markdown=True):
        if use_markdown:
            self.updater.bot.send_message(chat, message, parse_mode='MarkdownV2')
        else:
            self.updater.bot.send_message(chat, message)

    def notify_board(self, chat, game):
        self.send(chat, f'```{game.board}```')

    def notify_turn(self, chat, game):
        if game.active:
            my_turn = game.check_my_turn(chat)
            turn_str = 'your' if my_turn else 'their'
            self.send(chat, f'It is {turn_str} turn')
        elif game.check_i_won(chat):
            self.send(chat, f'WINNER WINNER CHICKEN DINNER!')
            self.send(chat, f'Congrats! Use /new to play another one')
        else:
            opp = game.opponent(chat)
            self.send(chat, f'Oh no, {opp.name} wins, better luck next time!')
            self.send(chat, f'Use /new to play another one')

    def notify_game_start(self, chat, game):
        opp_name = game.opponent(chat).name
        self.send(chat, f"Game created! You play against {opp_name} as {game.side(chat)}", use_markdown=False)
        self.notify_board(chat, game)
        self.notify_turn(chat, game)

    def notify_move_made(self, chat, game):
        if game.check_my_turn(chat):
            self.send(chat, f"Opponent made a move!")
        self.notify_board(chat, game)
        self.notify_turn(chat, game)

    def notify_waiting_for_opp(self, chat):
        self.send(chat, "Waiting for an opponent, use /abort to bail out", use_markdown=False)