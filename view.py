import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
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
ARCHIVE, START_OVER, MANAGEMENT, EDIT, CREATE = 'ARCHIVE', 'START_OVER', 'MANAGEMENT', 'EDIT', 'CREATE'
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
            InlineKeyboardButton("Редактирование событий", callback_data=str(MANAGEMENT))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("Танцы спасут этот мир\U0001F483\nЯ бот и покажу тебе, что происходит в мире танцев\U0001F525",
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
            InlineKeyboardButton("Редактирование событий", callback_data=str(MANAGEMENT))
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


def show_management(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Создать событие", callback_data=str(CREATE))
        ],
        [
            InlineKeyboardButton("Редактировать событие", callback_data=str(EDIT))
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Управление событиями", reply_markup=reply_markup
    )
    return FIRST


def go_back(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(MANAGEMENT))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Управление событиями", reply_markup=reply_markup
    )
    return FIRST
#
#
# def gender(update: Update, context: CallbackContext) -> int:
#     """Stores the selected gender and asks for a photo."""
#     user = update.message.from_user
#     logger.info("Gender of %s: %s", user.first_name, update.message.text)
#     update.message.reply_text(
#         'I see! Please send me a photo of yourself, '
#         'so I know what you look like, or send /skip if you don\'t want to.',
#         reply_markup=ReplyKeyboardRemove(),
#     )
#
#     return PHOTO
#
#
# def photo(update: Update, context: CallbackContext) -> int:
#     """Stores the photo and asks for a location."""
#     user = update.message.from_user
#     photo_file = update.message.photo[-1].get_file()
#     photo_file.download('user_photo.jpg')
#     logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
#     update.message.reply_text(
#         'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
#     )
#
#     return LOCATION
#
#
# def skip_photo(update: Update, context: CallbackContext) -> int:
#     """Skips the photo and asks for a location."""
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     update.message.reply_text(
#         'I bet you look great! Now, send me your location please, or send /skip.'
#     )
#
#     return LOCATION
#
#
# def cancel(update: Update, context: CallbackContext) -> int:
#     """Cancels and ends the conversation."""
#     user = update.message.from_user
#     logger.info("User %s canceled the conversation.", user.first_name)
#     update.message.reply_text(
#         'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
#     )
#
#     return ConversationHandler.END