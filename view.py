import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)
Y2021, Y2022, Y2023, Y2024 = range(2021, 2025)
ARCHIVE, START_OVER = 'ARCHIVE', 'START_OVER'
JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC = range(1, 13)
FLAG_RU, FLAG_TR, FLAG_HR = "\U0001F1F7\U0001F1FA", "\U0001F1F9\U0001F1F7", "\U0001F1ED\U0001F1F7"


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть календарь событий", callback_data=str(ONE))
        ],
        [
            InlineKeyboardButton("Управление событиями", callback_data=str(TWO))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Танцы спасут этот мир :) Я бот и покажу тебе, что происходит в мире танцев",
                              reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть календарь событий", callback_data=str(ONE))
        ],
        [
            InlineKeyboardButton("Управление событиями", callback_data=str(TWO))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    query.edit_message_text(text="Что делаем дальше?", reply_markup=reply_markup)
    return FIRST


def show_calendar(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("2022 год (6)", callback_data=str(Y2022))
        ],
        # [
        #     InlineKeyboardButton("2023 год (0)", callback_data=str(Y2023))
        # ],
        [
            InlineKeyboardButton("Архив", callback_data=ARCHIVE)
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выбери период:", reply_markup=reply_markup
    )
    return FIRST


def show_month_list(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Октябрь (3)", callback_data=str(OCT))
        ],
        # [
        #     InlineKeyboardButton("Ноябрь (1)", callback_data=str(NOV))
        # ],
        [
            InlineKeyboardButton("Декабрь (3)", callback_data=str(DEC))
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(ONE))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выбери месяц:", reply_markup=reply_markup
    )
    return FIRST


def show_month_oct(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(Y2022))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="События в этом месяце:\n\n"
             "1. " + FLAG_RU + "Открытый Кубок Черноземья (Воронеж) 3-4 октября\n\n"
             "2. " + FLAG_HR + "ROVINJ SUMMER SENSUAL DAYS (Ровинь) 03-11 октября\n\n"
             "3. " + FLAG_RU + "Volga Open Cup 2022 (Пенза) 09-11 октября", reply_markup=reply_markup
    )
    return FIRST


def show_month_dec(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(Y2022))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="События в этом месяце:\n\n"
             "1. " + FLAG_TR + "FETHIYE DANCE CAMP (Фетхие) 3-11 декабря\n\n"
             "2. " + FLAG_RU + "Открытый Южный Кубок 2022 (Анапа) 03-11 декабря\n\n"
             "3. " + FLAG_RU + "RUSSIAN BACHATA FESTIVAL (Санкт-Петербург) 09-11 декабря", reply_markup=reply_markup
    )
    return FIRST


def show_archive(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("2021 год (0)", callback_data=str(Y2021))
        ],
        # [
        #     InlineKeyboardButton("2023 год (0)", callback_data=str(Y2023))
        # ],
        # [
        #     InlineKeyboardButton("Архив", callback_data=ARCHIVE)
        # ],
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Выбери период:", reply_markup=reply_markup
    )
    return FIRST

# def two(update: Update, context: CallbackContext) -> int:
#     """Show new choice of buttons"""
#     query = update.callback_query
#     query.answer()
#     keyboard = [
#         [
#             InlineKeyboardButton("1", callback_data=str(ONE)),
#             InlineKeyboardButton("3", callback_data=str(THREE)),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.edit_message_text(
#         text="Second CallbackQueryHandler, Choose a route", reply_markup=reply_markup
#     )
#     return FIRST
#
#
# def three(update: Update, context: CallbackContext) -> int:
#     """Show new choice of buttons"""
#     query = update.callback_query
#     query.answer()
#     keyboard = [
#         [
#             InlineKeyboardButton("Yes, let's do it again!", callback_data=str(ONE)),
#             InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(TWO)),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.edit_message_text(
#         text="Third CallbackQueryHandler. Do want to start over?", reply_markup=reply_markup
#     )
#     # Transfer to conversation state `SECOND`
#     return SECOND
#
#
# def four(update: Update, context: CallbackContext) -> int:
#     """Show new choice of buttons"""
#     query = update.callback_query
#     query.answer()
#     keyboard = [
#         [
#             InlineKeyboardButton("2", callback_data=str(TWO)),
#             InlineKeyboardButton("3", callback_data=str(THREE)),
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.edit_message_text(
#         text="Fourth CallbackQueryHandler, Choose a route", reply_markup=reply_markup
#     )
#     return FIRST