from enum import Enum

card_id_to_sticker = {
     1 : 'CAADAgADEwAD0hEqHBhyCsDhJKzAFgQ', # Взрывной котенок
     2 : 'CAADAgADFAAD0hEqHHVu8rC1xA0dFgQ', # Взрывной котенок
     3 : 'CAADAgADFQAD0hEqHIOKjnIZGELPFgQ', # Взрывной котенок
     4 : 'CAADAgADFgAD0hEqHGPrtvJXG97TFgQ', # Взрывной котенок
     5 : 'CAADAgADFwAD0hEqHLgXw1McRjxDFgQ', # Обезвредь
     6 : 'CAADAgADGAAD0hEqHDFFTFGZ2iHOFgQ', # Обезвредь
     7 : 'CAADAgADGQAD0hEqHPJza51KG4_hFgQ', # Обезвредь
     8 : 'CAADAgADGgAD0hEqHNAtadM_gcccFgQ', # Обезвредь
     9 : 'CAADAgADGwAD0hEqHBxsB1C5FURbFgQ', # Обезвредь
    10 : 'CAADAgADHAAD0hEqHPq_ft6WfUC9FgQ', # Обезвредь
    11 : 'CAADAgADHQAD0hEqHPxVaGVnpV6DFgQ', # Взгляд в Будущее
    12 : 'CAADAgADHgAD0hEqHH4ikKiGILBJFgQ', # Взгляд в Будущее
    13 : 'CAADAgADHwAD0hEqHExRrLgrnVijFgQ', # Взгляд в Будущее
    14 : 'CAADAgADIAAD0hEqHCr9dL-UDbNZFgQ', # Взгляд в Будущее
    15 : 'CAADAgADIQAD0hEqHJGfDKx9hvKjFgQ', # Взгляд в Будущее
    16 : 'CAADAgADIgAD0hEqHKUwEDRANNiyFgQ', # Неа!
    17 : 'CAADAgADIwAD0hEqHB9kxVmK4BroFgQ', # Неа!
    18 : 'CAADAgADJAAD0hEqHGpULZpI5LsJFgQ', # Неа!
    19 : 'CAADAgADJQAD0hEqHEQfkbcdJC93FgQ', # Неа!
    20 : 'CAADAgADJgAD0hEqHM-5bIhMQwv2FgQ', # Неа!
    21 : 'CAADAgADJwAD0hEqHEF21s7KtFqiFgQ', # Перемешать
    22 : 'CAADAgADKAAD0hEqHMhFXv9T1i3GFgQ', # Перемешать
    23 : 'CAADAgADKQAD0hEqHLU2yjPtRSrOFgQ', # Перемешать
    24 : 'CAADAgADKgAD0hEqHM2kyxbR7upNFgQ', # Перемешать
    25 : 'CAADAgADKwAD0hEqHPUbwV3nCcK9FgQ', # Сбежать
    26 : 'CAADAgADLAAD0hEqHFPhrema0PGDFgQ', # Сбежать
    27 : 'CAADAgADLQAD0hEqHDK67syjIm_CFgQ', # Сбежать
    28 : 'CAADAgADLgAD0hEqHIJBAdxCzH_fFgQ', # Сбежать
    29 : 'CAADAgADLwAD0hEqHK4jtZcmsF7jFgQ', # Одолжение
    30 : 'CAADAgADMAAD0hEqHFxKVGeFL3_TFgQ', # Одолжение
    31 : 'CAADAgADMQAD0hEqHEcCvi9siaVFFgQ', # Одолжение
    32 : 'CAADAgADMgAD0hEqHPLp9evnxGklFgQ', # Одолжение
    33 : 'CAADAgADMwAD0hEqHDtRoa8kAr5BFgQ', # Атака
    34 : 'CAADAgADNAAD0hEqHCOuRsspSY1dFgQ', # Атака
    35 : 'CAADAgADNQAD0hEqHKJi0LdcXcf_FgQ', # Атака
    36 : 'CAADAgADNgAD0hEqHDT1nDrPErGIFgQ', # Атака
    37 : 'CAADAgADNwAD0hEqHE6oPhZUdodLFgQ', # "Кот радугапожиратель"
    38 : 'CAADAgADNwAD0hEqHE6oPhZUdodLFgQ', # "Кот радугапожиратель"
    39 : 'CAADAgADNwAD0hEqHE6oPhZUdodLFgQ', # "Кот радугапожиратель"
    40 : 'CAADAgADNwAD0hEqHE6oPhZUdodLFgQ', # "Кот радугапожиратель"
    41 : 'CAADAgADOAAD0hEqHHlloAnKVv2YFgQ', # "Волосатый кот-картошка"
    42 : 'CAADAgADOAAD0hEqHHlloAnKVv2YFgQ', # "Волосатый кот-картошка"
    43 : 'CAADAgADOAAD0hEqHHlloAnKVv2YFgQ', # "Волосатый кот-картошка"
    44 : 'CAADAgADOAAD0hEqHHlloAnKVv2YFgQ', # "Волосатый кот-картошка"
    45 : 'CAADAgADOQAD0hEqHLK7pONrjTBFFgQ', # "Такокот"
    46 : 'CAADAgADOQAD0hEqHLK7pONrjTBFFgQ', # "Такокот"
    47 : 'CAADAgADOQAD0hEqHLK7pONrjTBFFgQ', # "Такокот"
    48 : 'CAADAgADOQAD0hEqHLK7pONrjTBFFgQ', # "Такокот"
    49 : 'CAADAgADOgAD0hEqHDBzxd19XpDIFgQ', # "Арбузный кот"
    50 : 'CAADAgADOgAD0hEqHDBzxd19XpDIFgQ', # "Арбузный кот"
    51 : 'CAADAgADOgAD0hEqHDBzxd19XpDIFgQ', # "Арбузный кот"
    52 : 'CAADAgADOgAD0hEqHDBzxd19XpDIFgQ', # "Арбузный кот"
    53 : 'CAADAgADOwAD0hEqHOlDiahM3TlBFgQ', # "Бородакот"
    54 : 'CAADAgADOwAD0hEqHOlDiahM3TlBFgQ', # "Бородакот"
    55 : 'CAADAgADOwAD0hEqHOlDiahM3TlBFgQ', # "Бородакот"
    56 : 'CAADAgADOwAD0hEqHOlDiahM3TlBFgQ'  # "Бородакот"
}

# card_types = ['explosive kitten', # Взрывной котенок
#               'neutralize', # Обезвредь
#               'see the future',  # Взгляд в Будущее
#               'no', # Неа!
#               'shuffle', # Перемешать
#               'run away', # Сбежать
#               'favor', # Одолжение
#               'attack', # Атака
#               'special 1', # "Кот радугапожиратель"
#               'special 2', # "Волосатый кот-картошка"
#               'special 3', # "Такокот"
#               'special 4', # "Арбузный кот"
#               'special 5' # "Бородакот"
#               ]

class CardTypes(Enum):
    EXPLOSIVE_KITTEN = 1 # ✅
    NEUTRALIZE = 2 # ✅
    SEE_THE_FUTURE = 3 # 
    NO = 4 # ??? ✅ ??? <<<<<<<<<<<<<<<<<<<
    SHUFFLE = 5 # ✅
    RUN_AWAY = 6 # ✅
    FAVOR = 7 # ✅
    ATTACK = 8 # ✅
    SPECIAL_1 = 9 #
    SPECIAL_2 = 10 #    SPECIAL2 ✅
    SPECIAL_3 = 11 #    SPECIAL3 
    SPECIAL_4 = 12 #    SPECIAL5 
    SPECIAL_5 = 13 #

        # markup = types.InlineKeyboardMarkup(row_width=2)
        # markup.add(types.InlineKeyboardButton(text='Обезвредь', callback_data='choose_card 2'), types.InlineKeyboardButton(text='Подсмуртри грядущее', callback_data='choose_card 3'))
        # markup.add(types.InlineKeyboardButton(text='Неть', callback_data='choose_card 4'), types.InlineKeyboardButton(text='Затасуй', callback_data='choose_card 5'))
        # markup.add(types.InlineKeyboardButton(text='Слиняй', callback_data='choose_card 6'), types.InlineKeyboardButton(text='Подлижись', callback_data='choose_card 7'))
        # markup.add(types.InlineKeyboardButton(text='Атака', callback_data='choose_card 8'), types.InlineKeyboardButton(text='Кот радугапожиратель', callback_data='choose_card 9'))
        # markup.add(types.InlineKeyboardButton(text='Волосатый кот-картошка', callback_data='choose_card 10'), types.InlineKeyboardButton(text='Такокот', callback_data='choose_card 11'))
        # markup.add(types.InlineKeyboardButton(text='Арбузный кот', callback_data='choose_card 12'), types.InlineKeyboardButton(text='Бородакот', callback_data='choose_card 13'))
        # return markup

def convert_card_type_no_name(type):
    if type == 1:
        return 'Взрывной котенок'
    elif type == 2:
        return 'Обезвредь'
    elif type == 3:
        return 'Подсмуртри грядущее'
    elif type == 4:
        return 'Неть'
    elif type == 5:
        return 'Затасуй'
    elif type == 6:
        return 'Слиняй'
    elif type == 7:
        return 'Подлижись'
    elif type == 8:
        return 'Атака'
    elif type == 9:
        return 'Кот радугапожиратель'
    elif type == 10:
        return 'Волосатый кот-картошка'
    elif type == 11:
        return 'Такокот'
    elif type == 12:
        return 'Арбузный кот'
    elif type == 13:
        return 'Бородакот'
    return None

def convert_card_id_to_type(id):
    if id in [1, 2, 3, 4]:
        return CardTypes.EXPLOSIVE_KITTEN
    elif id in [5, 6, 7, 8, 9, 10]:
        return CardTypes.NEUTRALIZE
    elif id in [11, 12, 13, 14, 15]:
        return CardTypes.SEE_THE_FUTURE
    elif id in [16, 17, 18, 19, 20]:
        return CardTypes.NO
    elif id in [21, 22, 23, 24]:
        return CardTypes.SHUFFLE
    elif id in [25, 26, 27, 28]:
        return CardTypes.RUN_AWAY
    elif id in [29, 30, 31, 32]:
        return CardTypes.FAVOR
    elif id in [33, 34, 35, 36]:
        return CardTypes.ATTACK
    elif id in [37, 38, 39, 40]:
        return CardTypes.SPECIAL_1
    elif id in [41, 42, 43, 44]:
        return CardTypes.SPECIAL_2
    elif id in [45, 46, 47, 48]:
        return CardTypes.SPECIAL_3
    elif id in [49, 50, 51, 52]:
        return CardTypes.SPECIAL_4
    elif id in [53, 54, 55, 56]:
        return CardTypes.SPECIAL_5
