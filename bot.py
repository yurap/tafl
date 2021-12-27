from helpers import TablutGameCreator, TablutGamePrinter
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secrets import TOKEN
from server import Server
from message import Message, MessageManager
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
games = Server()
updater = Updater(TOKEN, use_context=True)
messenger = MessageManager(updater)


def command_new(update, _):
    global games, messenger
    msg = Message.from_update(update)
    g = games.new(msg.chat, msg.name)
    if g is None:
        messenger.notify_waiting_for_opp(msg.chat)
    else:
        opp = g.opponent(msg.chat)
        messenger.notify_game_start(msg.chat, g)
        messenger.notify_game_start(opp.chat, g)


def command_abort(update, _):
    # fixme: implement
    update.message.reply_text('Oops, not implemented!')


def command_start(update, _):
    msg = Message.from_update(update)
    logger.info(f'New user: {msg.name}!')
    update.message.reply_text(
        f"Hi {msg.name},\n\nWould you like to play a game of tablut?\n\n"
        f"Use /new to create a new game, you will be paired with another user\n\n"
        f"Use /help to find out how to play\n\n"
        f"Good luck and have fun!"
    )


def command_help(update, _):
    update.message.reply_text(
        f'Tablut is an ancient game of viking chess.\n\n'
        f'It is played on a 9x9 board with two teams: attackers (x) and defenders (o).\n\n'
        f'Attackers try to surround the king of defenders (O), and '
        f'the king tries to escape to any edge of the board.\n\n'
        f'All pieces move only vertically or horizontally and cannot jump over each other.\n\n'
        f"A piece is captured if it is surrounded from two opposite sides via opponent's move.\n\n"
        f"When it's your turn -- type the coordinates of src and dst squares to make a move, e.g. d1d2\n\n"
        f"Use /new to start a new game"
    )


def process(update, _):
    global games, messenger
    msg = Message.from_update(update)
    g = games.game(msg.chat)
    if g is None:
        update.message.reply_text(f"Oops, there's no game! To create one use /new and wait to be paired")
    else:
        g.move(msg.chat, msg.text)
        opp = g.opponent(msg.chat)
        messenger.notify_move_made(msg.chat, g)
        messenger.notify_move_made(opp.chat, g)


def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text('Oops, something went wrong :(')


if __name__ == '__main__':
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", command_start))
    dp.add_handler(CommandHandler("help", command_help))
    dp.add_handler(CommandHandler("new", command_new))
    dp.add_handler(CommandHandler("abort", command_abort))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
