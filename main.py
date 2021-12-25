from helpers import TaflGameCreator, TaflGamePrinter
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secrets import TOKEN
from dataclasses import dataclass
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
games = {}


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


def command_new(update, _):
    global games
    msg = Message.from_update(update)
    g = games[msg.chat] = TaflGameCreator.create_basic()
    update.message.reply_text("New game created!")
    update.message.reply_text('```' + TaflGamePrinter.str(g) + '```', parse_mode='MarkdownV2')


def command_start(update, _):
    msg = Message.from_update(update)
    logger.info(f'New user: {msg.name}!')
    update.message.reply_text(f"Hi {msg.name}! Let's play a game of tablut? Type /new to create a new game")


def command_help(update, _):
    update.message.reply_text('Help!')


def process(update, _):
    global games
    msg = Message.from_update(update)
    g = games[msg.chat]
    if g is None:
        update.message.reply_text('There is no game, type /new to create one')
        return

    try:
        g.move(msg.text)
        update.message.reply_text('```' + TaflGamePrinter.str(g) + '```', parse_mode='MarkdownV2')
    except Exception as e:
        update.message.reply_text(str(e))


def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", command_start))
    dp.add_handler(CommandHandler("help", command_help))
    dp.add_handler(CommandHandler("new", command_new))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
