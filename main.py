from bot_processor import BotProcessor
import telebot
import time
from string_generators import *

from commands import Commands

bot = telebot.TeleBot('TOKEN')
bot.threaded = False
bot_processor = BotProcessor(bot)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "---")

@bot.message_handler(commands=['create'])
def create_game(message):
    bot_processor.process_command(Commands.CREATE, message)

@bot.message_handler(commands=['join'])
def join_game(message):
    bot_processor.process_command(Commands.JOIN, message)

@bot.message_handler(commands=['leave'])
def leave_game(message):
    bot_processor.process_command(Commands.LEAVE, message)

@bot.message_handler(commands=['leave_all'])
def leave_all_games(message):
    bot_processor.process_command(Commands.LEAVE_ALL, message)

@bot.message_handler(commands=['play'])
def play_game(message):
    bot_processor.process_command(Commands.PLAY, message)

@bot.message_handler(commands=['close'])
def close_game(message):
    bot_processor.process_command(Commands.CLOSE, message)

@bot.message_handler(commands=['take_card'])
def close_game(message):
    bot_processor.process_command(Commands.TAKE_CARD, message)

@bot.message_handler(commands=['set'])
def close_game(message):
    bot_processor.process_command(Commands.PLACE_CARD, message)

@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def inline_chosen(chosen_inline_result):
    bot_processor.process_inline_chosen(chosen_inline_result)

    bot.edit_message_text

@bot.inline_handler(lambda query: len(query.query) == 0)
def query_text(inline_query):
    bot_processor.process_inline_request(inline_query)

@bot.inline_handler(lambda query: len(query.query) != 0)
def query_text(inline_query):
    bot.answer_inline_query(inline_query.id, [], cache_time=500)

@bot.callback_query_handler(func=lambda call: True)
def process_callback_query(call):
    bot_processor.process_callback_query(call)

@bot.message_handler(commands=['rules'])
def message_instruction(message):
    rules = open('rules.pdf', 'rb')
    bot.send_document(message.chat.id, rules, caption='📘 Правила')

@bot.message_handler(commands=['special2'])
def message_instruction(message):
    bot_processor.process_command(Commands.SPECIAL2, message)

@bot.message_handler(commands=['special3'])
def message_instruction(message):
    bot_processor.process_command(Commands.SPECIAL3, message)

@bot.message_handler(commands=['special5'])
def message_instruction(message):
    bot_processor.process_command(Commands.SPECIAL5, message)

@bot.message_handler(commands=['undo'])
def message_instruction(message):
    bot_processor.process_command(Commands.UNDO, message)

@bot.message_handler(commands=['cards'])
def message_instruction(message):
    bot_processor.process_command(Commands.CARDS, message)

@bot.message_handler(commands=['menu'])
def message_instruction(message):
    bot_processor.process_command(Commands.MENU, message)

while True:
    bot.polling(none_stop=True)
    print("Bot stopped. Waiting 1 sec")
    time.sleep(1)