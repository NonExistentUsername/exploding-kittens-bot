from os import makedirs
from notifications import Notifications
from chats_manager import ChatsManager
from notifications_processor import NotificationsProcessor
from games_manager import GamesManager
from commands import Commands
from messages import Messages
from string_generators import *
from telebot import types
from cards import *

class BotProcessor:
    ##########################################################

    @property
    def __chat_id(self):
        if self.__message != None:
            return self.__message.chat.id
        elif self.__call != None:
            return self.__call.message.chat.id
        return None

    @property
    def __u(self):
        if self.__message != None:
            return self.__message.from_user
        elif self.__call != None:
            return self.__call.from_user
        elif self.__inline_result != None:
            return self.__inline_result.from_user
        return None
        
    @property
    def __user_id(self):
        if self.__u != None:
            return self.__u.id
        return None

    ##########################################################

    def __create(self):
        self.__gms_controller.create_game(self.__message.chat.id)

    def __close(self):
        self.__gms_controller.close_game(self.__message.chat.id)

    def __join(self):
        self.__gms_controller.join_game(self.__chat_id, self.__user_id)

    def __leave(self):
        self.__gms_controller.leave_game(self.__chat_id, self.__user_id)

    def __leave_all(self):
        self.__gms_controller.leave_all_games(self.__message.from_user.id)

    def __play(self):
        self.__gms_controller.start_game(self.__message.chat.id)

    def __take_card(self):
        self.__gms_controller.take_card(self.__user_id)

    def __place_card(self):
        self.__gms_controller.place_card(self.__user_id, self.__message.text[4:])

    def __boom(self):
        self.__gms_controller.boom(self.__user_id)

    def __choose_player(self, data):
        __user_id = int(data.split()[1])
        self.__gms_controller.choose_player(self.__user_id, __user_id)
    
    def __choose_card(self, data):
        __card_type = int(data.split()[1])
        self.__gms_controller.choose_card(self.__user_id, __card_type)

    def __special2(self):
        self.__gms_controller.special2(self.__user_id)

    def __special3(self):
        self.__gms_controller.special3(self.__user_id)

    def __special5(self):
        self.__gms_controller.special5(self.__user_id)

    def __undo_special(self):
        self.__gms_controller.undo_special(self.__user_id)

    def __cards(self):
        self.__gms_controller.get_deck(self.__user_id)

    def __menu(self):
        if self.__message != None:
            if self.__message.chat.id in self.__menus:
                self.__bot.reply_to(self.__menus[self.__message.chat.id], Messages.MENU)
            else:
                self.__game_not_started()

    ##########################################################
        
    @staticmethod
    def __generate_players_count(count):
        return '🔷 Количество игроков: ' + str(count)
    
    @staticmethod
    def __generate_cards_count(count):
        return '🔷 Количество карт в колоде: ' + str(count)

    ##########################################################

    @staticmethod
    def __generate_jl_markup(empty):
        if empty:
            return None
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        __join = types.InlineKeyboardButton(text='Подключиться', callback_data='join')
        __leave = types.InlineKeyboardButton(text='Выйти', callback_data='leave')
        markup.add(__join, __leave)

        return markup

    @staticmethod
    def __generate_deck_button_markup(empty):
        if empty:
            return None
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        __deck = types.InlineKeyboardButton(text='Открыть колоду', switch_inline_query_current_chat='')
        markup.add(__deck)

        return markup

    @staticmethod
    def __generate_take_card_markup(empty):
        if empty:
            return None

        markup = types.InlineKeyboardMarkup(row_width=2)
        __take_card = types.InlineKeyboardButton(text='Взять карту', callback_data='take_card')
        __deck = types.InlineKeyboardButton(text='Открыть колоду', switch_inline_query_current_chat='')
        markup.add(__take_card, __deck)

        return markup

    @staticmethod
    def __generate_boom_markup():
        markup = types.InlineKeyboardMarkup(row_width=1)
        __take_card = types.InlineKeyboardButton(text='Взорваться!', callback_data='boom')
        markup.add(__take_card)

        return markup

    def __generate_user_choosing_markup(self, chat_id):
        __card_counts = self.__gms_controller.get_no_cards_in_decks(chat_id)
        markup = types.InlineKeyboardMarkup(row_width=1)
        __users = self.__gms_controller.get_users(chat_id)
        for i in range(len(__users)):
            user_id = __users[i]
            markup.add(types.InlineKeyboardButton(text=self.__user_id_to_user[user_id].first_name + ' (' + str(__card_counts[i]) + ')', callback_data='choose_player ' + str(user_id)))

        return markup

    @staticmethod
    def __generate_card_type_choosing_markup():
        markup = types.InlineKeyboardMarkup(row_width=2)

        __create_button = lambda __type: types.InlineKeyboardButton(text=convert_card_type_no_name(__type), callback_data='choose_card ' + str(__type))

        __type = 2
        while __type < 14:
            __a = __create_button(__type)
            __type += 1
            __b = __create_button(__type)
            __type += 1
            markup.add(__a, __b)
        # markup.add(types.InlineKeyboardButton(text='Обезвредь', callback_data='choose_card 2'), types.InlineKeyboardButton(text='Подсмуртри грядущее', callback_data='choose_card 3'))
        # markup.add(types.InlineKeyboardButton(text='Неть', callback_data='choose_card 4'), types.InlineKeyboardButton(text='Затасуй', callback_data='choose_card 5'))
        # markup.add(types.InlineKeyboardButton(text='Слиняй', callback_data='choose_card 6'), types.InlineKeyboardButton(text='Подлижись', callback_data='choose_card 7'))
        # markup.add(types.InlineKeyboardButton(text='Атака', callback_data='choose_card 8'), types.InlineKeyboardButton(text='Кот радугапожиратель', callback_data='choose_card 9'))
        # markup.add(types.InlineKeyboardButton(text='Волосатый кот-картошка', callback_data='choose_card 10'), types.InlineKeyboardButton(text='Такокот', callback_data='choose_card 11'))
        # markup.add(types.InlineKeyboardButton(text='Арбузный кот', callback_data='choose_card 12'), types.InlineKeyboardButton(text='Бородакот', callback_data='choose_card 13'))
        return markup

    ##########################################################

    def __generate_create_message(self, chat_id, default = False):
        if default:
            return Messages.GAME_CREATED
        else:
            return Messages.GAME_CREATED + '\n' + \
                BotProcessor.__generate_players_count(self.__gms_controller.get_users_count(chat_id))

    def __generate_users_list(self, chat_id):
        __str = ''
        __users = self.__gms_controller.get_users(chat_id)
        
        __index = 1
        for user_id in __users:
            __str += Messages.P_NEUTRAL + ' ' + str(__index) + '. ' + self.__user_id_to_user[user_id].first_name + '\n'
            __index += 1
        return __str

    def __generate_start_message(self, chat_id, default = False):
        if default:
            return Messages.GAME_STARTED
        else:
            return Messages.GAME_STARTED + '\n' + \
                BotProcessor.__generate_players_count(self.__gms_controller.get_users_count(chat_id)) + '\n' + \
                BotProcessor.__generate_cards_count(self.__gms_controller.get_deck_cards_count(chat_id)) + '\n\n' + \
                self.__generate_users_list(chat_id)

    def __generate_start_message_entities(self, chat_id, default = False):
        print('__generate_start_message_entities')
        if default:
            return []

        __result = []

        __prefix_len = len(Messages.GAME_STARTED + '\n' + \
                BotProcessor.__generate_players_count(self.__gms_controller.get_users_count(chat_id)) + '\n' + \
                BotProcessor.__generate_cards_count(self.__gms_controller.get_deck_cards_count(chat_id)) + '\n\n') + 2
        __users = self.__gms_controller.get_users(chat_id)

        __d_len = 0
        for user_id in __users:
            __d_len += len(Messages.P_NEUTRAL) + len(' 1. ') + 1
            __user = self.__user_id_to_user[user_id]
            __result.append(types.MessageEntity('text_mention', __prefix_len + __d_len, len(__user.first_name), user=__user.__dict__))
            __d_len += len(__user.first_name) + 1
        
        return __result

    ##########################################################

    def __create_message_updater(self, chat_id, message_id, default = False):
        try:
            self.__bot.edit_message_text(self.__generate_create_message(chat_id, default), chat_id, message_id, 
                reply_markup=BotProcessor.__generate_jl_markup(default))
        except Exception:
            pass

    def __start_message_updater(self, chat_id, message_id, default = False):
        try:
            print('__start_message_updater processed defalut = {0}'.format(default))

            self.__bot.edit_message_text(self.__generate_start_message(chat_id, default), chat_id, message_id,
                reply_markup=BotProcessor.__generate_take_card_markup(default),
                entities=self.__generate_start_message_entities(chat_id, default))

            print('__start_message updated')
        except Exception as e:
            print(e)

    ##########################################################

    def __game_created(self):
        message_id = self.__bot.send_message(self.__chat_id, self.__generate_create_message(self.__chat_id), 
            reply_markup=BotProcessor.__generate_jl_markup(False)
            ).message_id
        self.__messages.set(self.__chat_id, message_id, self.__create_message_updater)

    def __game_closed(self, **data):
        self.__messages.remove(self.__message.chat.id)
        if self.__message.chat.id in self.__menus:
            del self.__menus[self.__message.chat.id]
        for user_id in data['users']:
            del self.__user_id_to_user[user_id]
        
        self.__bot.reply_to(self.__message, Messages.GAME_CLOSED)

    def __game_started(self):
        self.__messages.remove(self.__chat_id)

        self.__menus[self.__message.chat.id] = self.__bot.send_message(self.__chat_id, self.__generate_start_message(self.__chat_id),
            reply_markup=BotProcessor.__generate_take_card_markup(False),
            entities=self.__generate_start_message_entities(self.__chat_id, False))

        print('__game_started sef.__messages.set proccessed')
        self.__messages.set(self.__chat_id, self.__menus[self.__message.chat.id].message_id, self.__start_message_updater)

    def __game_already_started(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.GAME_ALREADY_STARTED)

    def __game_already_created(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.GAME_ALREADY_CREATED)

    def __player_joined(self):
        self.__messages.update(self.__chat_id)

        self.__user_id_to_user[self.__u.id] = self.__u

        self.__bot.send_message(self.__chat_id, Messages.PLAYER_PREFIX + self.__u.first_name + Messages.PLAYER_JOINED_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __player_already_in_game(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.PLAYER_ALREADY_IN_GAME)

    def __player_in_another_game(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.PLAYER_IN_ANOTHER_GAME)

    def __game_not_created(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.GAME_NOT_CREATED)

    def __no_players_not_valid(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.NO_PLAYERS_NOT_VALID)

    def __player_not_in_game(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.PLAYER_NOT_IN_GAME)

    def __player_leaves(self, **data):
        self.__messages.update(data['chat_id'])

        del self.__user_id_to_user[self.__user_id]

        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__u.first_name + Messages.PLAYER_LEAVES_SUFFIX, 
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __card_taken(self):
        self.__messages.update(self.__chat_id)
        
        self.__bot.send_message(self.__chat_id, Messages.PLAYER_PREFIX + self.__u.first_name + Messages.PLAYER_TAKE_CARD_SUFFIX, 
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __another_player_turn(self, **data):
        if self.__message != None:
            self.__bot.send_message(self.__chat_id, Messages.ANOTHER_PLAYER_TURN + self.__user_id_to_user[data['user_id']].first_name, 
                entities=[types.MessageEntity('text_mention', len(Messages.ANOTHER_PLAYER_TURN), len(self.__user_id_to_user[data['user_id']].first_name), user= self.__user_id_to_user[data['user_id']].__dict__)])
        
    def __explosive_kitten(self, **data):
        self.__messages.update(self.__chat_id)

        self.__bot.send_sticker(self.__chat_id, card_id_to_sticker[data['card_id']], reply_markup=self.__generate_boom_markup())
        self.__bot.send_message(self.__chat_id, Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_TOOK_EXPLOSIVE_KITTEN_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __explosive_kitten_neutralized(self, **data):
        self.__messages.update(self.__chat_id)
        
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_NEUTRALIZED_EXPLISIVE_KITTEN_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])
        self.__bot.send_message(data['chat_id'], Messages.PLACE_CARD_TUTORIAL_MINI.format(self.__gms_controller.get_deck_cards_count(data['chat_id']) + 1))

    def __place_card_failed(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.PLACE_CARD_TUTORIAL.format(self.__gms_controller.get_deck_cards_count(self.__gms_controller.get_game_id(self.__user_id)) + 1))

    def __game_not_started(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.GAME_NOT_STARTED)

    def __card_placed(self, **data):
        self.__messages.update(self.__chat_id)

        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_PLACED_EXPLOSIVE_KITTEN_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __player_boom(self, **data):
        self.__messages.update(self.__chat_id)

        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_BOOM_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

        del self.__user_id_to_user[self.__user_id]

    def __player_shuffled_deck(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_SHUFFLED_DECK_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __player_ran_away(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[self.__user_id].first_name + Messages.PLAYER_RAN_AWAY_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__u.first_name), user=self.__u.__dict__)])

    def __next_player_turn(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.NEXT_PLAYER_TURN + self.__user_id_to_user[data['user_id']].first_name,
            # reply_markup=BotProcessor.__generate_deck_button_markup(False),
            entities=[types.MessageEntity('text_mention', len(Messages.NEXT_PLAYER_TURN)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_attacked(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_ATTACKED_SUFFIX.format(data['turns_count']),
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_see_the_future(self, **data):
        try:
            for card_id in data['cards']:
                self.__bot.send_sticker(data['user_id'], card_id_to_sticker[card_id])

            # self.__gms_controller.see_the_future_successful(data['user_id'])
            self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_SEEN_THE_FUTURE_SUFFIX,
                entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])
            self.__gms_controller.see_the_future_successful(data['user_id'])
        except Exception as e:
            # self.__gms_controller.undo(data['chat_id'])
            self.__bot.send_message(data['chat_id'], Messages.SEE_THE_FUTURE_FAILED)

    def __player_canceled_last_action(self, **data):
            self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_CANCELED_LAST_ACTION_SUFFIX,
                entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __favor_player_choosing(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.FAVOR_PLAYER_CHOOSING, reply_markup=self.__generate_user_choosing_markup(data['chat_id']))

    def __favor_card_choosing(self, **data):
            self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_MUST_CH0OSE_CARD_SUFFIX,
                entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __favor_player_choosed_with_empty_deck(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK)

    def __game_end(self, **data):
        self.__messages.remove(data['chat_id'])
        if data['chat_id'] in self.__menus:
            del self.__menus[data['chat_id']]

        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_WON_THE_GAME_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

        for user_id in data['users']:
            del self.__user_id_to_user[user_id]

    def __player_cant_use_this_combination(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.CANT_USE_THIS_COMBINATION)

    def __player_choosing_cards_for_comb(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_CHOOSING_CARDS_FOR_COMB_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __special2_done(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.SPECIAL2_DONE_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_has_no_card(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX_2 + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_HAS_NO_CARD_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX_2)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_choosed(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_CHOOSED + self.__user_id_to_user[data['user_id']].first_name,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_CHOOSED)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __card_type_choosing(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.CHOOSE_CARD_TYPE, reply_markup=BotProcessor.__generate_card_type_choosing_markup())

    def __special3_failed(self, **data):        
        self.__bot.send_message(data['chat_id'], Messages.SPECIAL3_FAILED_WITH_THIS_TYPE)

    def __special3_done(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.SPECIAL3_DONE_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __turn_canceled(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.TURN_CANCELED)

    def __discard_is_empty(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.DISCARD_IS_EMPTY)

    def __undo_special_successfull(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.CANCELED_SPECIAL_COMB_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __undo_special_failed(self):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.UNDO_SPECIAL_FAILED)

    def __card_type_choosed(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.CARD_TYPE_CHOOSED_SUFFIX + convert_card_type_no_name(data['card_type']),
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_taking_card_from_discard(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_TAKING_CARD_FROM_DISCARD_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __special5_waiting(self, **data):        
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_WAITING_TO_TAKE_CARD_FROM_DISCARD_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __player_took_card_from_discard(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.PLAYER_PREFIX + self.__user_id_to_user[data['user_id']].first_name + Messages.PLAYER_TOOK_CARD_FROM_DISCARD_SUFFIX,
            entities=[types.MessageEntity('text_mention', len(Messages.PLAYER_PREFIX)+1, len(self.__user_id_to_user[data['user_id']].first_name), user=self.__user_id_to_user[data['user_id']].__dict__)])

    def __print_deck_size(self, **data):
        if self.__message != None:
            self.__bot.reply_to(self.__message, Messages.DECK_SIZE + str(data['deck_size']))

    def __yourself_cannot_be_choosen(self, **data):
        self.__bot.send_message(data['chat_id'], Messages.YOURSELF_CAN_NOT_BE_CHOOSEN)

    ##########################################################

    def __init_notif_processor(self):
        self.__notif_processor.bind(Notifications.GAME_CREATED, self.__game_created)
        self.__notif_processor.bind(Notifications.GAME_CLOSED, self.__game_closed)
        self.__notif_processor.bind(Notifications.GAME_ALREADY_CREATED, self.__game_already_created)
        self.__notif_processor.bind(Notifications.GAME_NOT_CREATED, self.__game_not_created)
        self.__notif_processor.bind(Notifications.PLAYER_JOINED, self.__player_joined)
        self.__notif_processor.bind(Notifications.NO_PLAYERS_NOT_VALID, self.__no_players_not_valid)
        self.__notif_processor.bind(Notifications.PLAYER_ALREADY_IN_GAME, self.__player_already_in_game)
        self.__notif_processor.bind(Notifications.PLAYER_IN_ANOTHER_GAME, self.__player_in_another_game)
        self.__notif_processor.bind(Notifications.PLAYER_NOT_IN_GAME, self.__player_not_in_game)
        self.__notif_processor.bind(Notifications.PLAYER_LEAVES, self.__player_leaves)
        self.__notif_processor.bind(Notifications.GAME_STARTED, self.__game_started)
        self.__notif_processor.bind(Notifications.GAME_ALREADY_STARTED, self.__game_already_started)
        self.__notif_processor.bind(Notifications.CARD_TAKEN, self.__card_taken)
        self.__notif_processor.bind(Notifications.ANOTHER_PLAYER_TURN, self.__another_player_turn)
        self.__notif_processor.bind(Notifications.EXPLOSIVE_KITTEN, self.__explosive_kitten)
        self.__notif_processor.bind(Notifications.EXPLOSIVE_KITTEN_NEUTRALIZED, self.__explosive_kitten_neutralized)
        self.__notif_processor.bind(Notifications.PLACE_CARD_FAILED, self.__place_card_failed)
        self.__notif_processor.bind(Notifications.GAME_NOT_STARTED, self.__game_not_started)
        self.__notif_processor.bind(Notifications.EXPLOSIVE_KITTEN_PLACED, self.__card_placed)
        self.__notif_processor.bind(Notifications.PLAYER_BOOM, self.__player_boom)
        self.__notif_processor.bind(Notifications.PLAYER_SHUFFLED_DECK, self.__player_shuffled_deck)
        self.__notif_processor.bind(Notifications.PLAYER_RAN_AWAY, self.__player_ran_away)
        self.__notif_processor.bind(Notifications.NEXT_PLAYER_TURN, self.__next_player_turn)
        self.__notif_processor.bind(Notifications.PLAYER_ATTACKED, self.__player_attacked)
        self.__notif_processor.bind(Notifications.SEE_THE_FUTURE, self.__player_see_the_future)
        self.__notif_processor.bind(Notifications.PLAYER_CANCELED_LAST_ACTION, self.__player_canceled_last_action)
        self.__notif_processor.bind(Notifications.FAVOR_PLAYER_CHOOSING, self.__favor_player_choosing)
        self.__notif_processor.bind(Notifications.FAVOR_CARD_CHOOSING, self.__favor_card_choosing)
        self.__notif_processor.bind(Notifications.FAVOR_PLAYER_CHOOSED_WITH_EMPTY_DECK, self.__favor_player_choosed_with_empty_deck)
        self.__notif_processor.bind(Notifications.GAME_END, self.__game_end)
        self.__notif_processor.bind(Notifications.PLAYER_CANT_USE_THIS_COMBINATION, self.__player_cant_use_this_combination)
        self.__notif_processor.bind(Notifications.PLAYER_CHOOSING_CARDS_FOR_COMB, self.__player_choosing_cards_for_comb)
        self.__notif_processor.bind(Notifications.SPECIAL2_DONE, self.__special2_done)
        self.__notif_processor.bind(Notifications.PLAYER_HAS_NO_CARD, self.__player_has_no_card)
        self.__notif_processor.bind(Notifications.PLAYER_CHOOSED, self.__player_choosed)
        self.__notif_processor.bind(Notifications.CARD_TYPE_CHOOSING, self.__card_type_choosing)
        self.__notif_processor.bind(Notifications.SPECIAL3_FAILED_WITH_THIS_TYPE, self.__special3_failed)
        self.__notif_processor.bind(Notifications.SPECIAL3_DONE, self.__special3_done)
        self.__notif_processor.bind(Notifications.TURN_CANCELED, self.__turn_canceled)
        self.__notif_processor.bind(Notifications.DISCARD_IS_EMPTY, self.__discard_is_empty)
        self.__notif_processor.bind(Notifications.UNDO_SPECIAL_SUCCESSFULL, self.__undo_special_successfull)
        self.__notif_processor.bind(Notifications.UNDO_SPECIAL_FAILED, self.__undo_special_failed)
        self.__notif_processor.bind(Notifications.CARD_TYPE_CHOOSED, self.__card_type_choosed)
        self.__notif_processor.bind(Notifications.PLAYER_TAKING_CARD_FROM_DISCARD, self.__player_taking_card_from_discard)
        self.__notif_processor.bind(Notifications.SPECIAL5_WAINTING, self.__special5_waiting)
        self.__notif_processor.bind(Notifications.PLAYER_TOOK_CARD_FROM_DISCARD, self.__player_took_card_from_discard)
        self.__notif_processor.bind(Notifications.PRINT_DECK_SIZE, self.__print_deck_size)
        self.__notif_processor.bind(Notifications.YOURSELF_CAN_NOT_BE_CHOOSEN, self.__yourself_cannot_be_choosen)
        # self.__notif_processor.bind()

    def __init_command_reactions(self):
        self.__command_reactions[Commands.CREATE] = self.__create
        self.__command_reactions[Commands.JOIN] = self.__join
        self.__command_reactions[Commands.LEAVE] = self.__leave
        self.__command_reactions[Commands.CLOSE] = self.__close
        self.__command_reactions[Commands.LEAVE_ALL] = self.__leave_all
        self.__command_reactions[Commands.PLAY] = self.__play
        self.__command_reactions[Commands.TAKE_CARD] = self.__take_card
        self.__command_reactions[Commands.PLACE_CARD] = self.__place_card
        self.__command_reactions[Commands.SPECIAL2] = self.__special2
        self.__command_reactions[Commands.SPECIAL3] = self.__special3
        self.__command_reactions[Commands.SPECIAL5] = self.__special5
        self.__command_reactions[Commands.UNDO] = self.__undo_special
        self.__command_reactions[Commands.CARDS] = self.__cards
        self.__command_reactions[Commands.MENU] = self.__menu
        # self.__call_reactions['special2'] = lambda data: self.__special2()

    def __init_call_reactions(self):
        self.__call_reactions['join'] = lambda data: self.__join()
        self.__call_reactions['leave'] = lambda data: self.__leave()
        self.__call_reactions['take_card'] = lambda data: self.__take_card()
        self.__call_reactions['boom'] = lambda data: self.__boom()
        self.__call_reactions['choose_player'] = self.__choose_player
        self.__call_reactions['choose_card'] = self.__choose_card

    def __init__(self, bot):
        self.__bot = bot
        self.__user_id_to_user = {}

        self.__gms_controller = GamesManager()
        self.__messages = ChatsManager()
        # self.__messages_updaters
        
        self.__notif_processor = NotificationsProcessor(self.__gms_controller)
        self.__init_notif_processor()

        self.__command_reactions = {}
        self.__init_command_reactions()

        self.__call_reactions = {}
        self.__init_call_reactions()
        
        self.__message = None
        self.__call = None
        self.__inline_result = None

        self.__menus = {}

    ##########################################################

    def process_command(self, command, message):
        self.__message = message

        if command in self.__command_reactions:
            print('Command processed: ', command.name)
            self.__command_reactions[command]()
        else:
            print('Command skipped: ', command.name)
        
        self.__message = None

    def process_callback_query(self, call):
        self.__call = call

        __call_type = call.data.split()[0]

        if __call_type in self.__call_reactions:
            print('Call processed: ', __call_type)
            self.__call_reactions[__call_type](call.data)
        else:
            print('Call skipped: ', __call_type)
            print('call: ', call)
        
        self.__call = None

    def process_inline_chosen(self, chosen_result):
        if int(chosen_result.result_id) >= 0:
            self.__inline_result = chosen_result

            self.__gms_controller.card_choosen(self.__user_id, int(chosen_result.result_id))

            self.__inline_result = None
        else:
            print('inline chose_result skipped: ', chosen_result.result_id)

    def process_inline_request(self, inline_query):

        print("process_inline_request")
        try:
            print("try start")
            __answer = self.__gms_controller.create_inline_answer(inline_query.from_user.id)
            print("__answer = self.__gms_controller.create_inline_answer(inline_query.from_user.id) endd")
            
            if __answer == None:
                __result = [(
                    types.InlineQueryResultArticle(-1, Messages.FIRST_CREATE_GAME, 
                        types.InputTextMessageContent(Messages.CREATE_GAME_TUTORIAL)))
                    ]
                self.__bot.answer_inline_query(inline_query.id, __result, cache_time=0)
            else:
                __result = []

                # if __answer.turn != inline_query.from_user.id:
                #     for card_id in __answer.deck:
                #         __result.append(types.InlineQueryResultCachedSticker(-card_id, card_id_to_sticker[card_id], input_message_content=types.InputTextMessageContent(Messages.ANOTHER_PLAYER_TURN + self.__user_id_to_user[__answer.turn].first_name,  
                #             entities=[types.MessageEntity('text_mention', len(Messages.ANOTHER_PLAYER_TURN), len(self.__user_id_to_user[__answer.turn].first_name), user=self.__user_id_to_user[__answer.turn].__dict__)])))
                # else:
                print("deck is ", __answer.deck)
                for i in range(len(__answer.deck)):
                    card_id = __answer.deck[i]
                    if __answer.can_move[i]:
                        if __answer.hidden:
                            __result.append(types.InlineQueryResultCachedSticker(card_id, card_id_to_sticker[card_id], input_message_content=types.InputTextMessageContent(Messages.PLAYER_CHOSEN_CARD)))
                        else:
                            __result.append(types.InlineQueryResultCachedSticker(card_id, card_id_to_sticker[card_id]))
                    else:
                        if __answer.turn != inline_query.from_user.id:
                            __result.append(types.InlineQueryResultCachedSticker(-card_id, card_id_to_sticker[card_id], input_message_content=types.InputTextMessageContent(Messages.ANOTHER_PLAYER_TURN + self.__user_id_to_user[__answer.turn].first_name,  
                                entities=[types.MessageEntity('text_mention', len(Messages.ANOTHER_PLAYER_TURN), len(self.__user_id_to_user[__answer.turn].first_name), user=self.__user_id_to_user[__answer.turn].__dict__)])))
                        else:
                            __result.append(types.InlineQueryResultCachedSticker(-card_id, card_id_to_sticker[card_id], input_message_content=types.InputTextMessageContent(Messages.CANT_MOVE_THIS_CARD)))

                self.__bot.answer_inline_query(inline_query.id, __result, cache_time=0)
        except GamesManager.UserError:
            pass
