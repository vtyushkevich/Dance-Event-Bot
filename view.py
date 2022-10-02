import logging
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    Message, Bot
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from config import BOT_TOKEN
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
TOP_LEVEL, CREATE_EVENT, CREATE_DATE = range(3)
# Callback data
ONE, TWO, THREE, FOUR = range(4)
Y2021, Y2022, Y2023, Y2024 = range(2021, 2025)
ARCHIVE, START_OVER, MANAGEMENT, EDIT, CREATE = 'ARCHIVE', 'START_OVER', 'MANAGEMENT', 'EDIT', 'CREATE'
JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC = range(1, 13)
FLAG_RU, FLAG_TR, FLAG_HR = "\U0001F1F7\U0001F1FA", "\U0001F1F9\U0001F1F7", "\U0001F1ED\U0001F1F7"
EDIT_NAME, EDIT_CITY, EDIT_DESC, EDIT_DATE_START = 'EDIT_NAME', 'EDIT_CITY', 'EDIT_DESC', 'EDIT_DATE_START'


def start(update: Update, context: CallbackContext) -> int:
    """Send message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [
            InlineKeyboardButton("Посмотреть календарь событий", callback_data=str(ONE))
        ],
        [
            InlineKeyboardButton("Создать событие", callback_data=str(MANAGEMENT))
        ],
        [
            InlineKeyboardButton("Посмотреть архив", callback_data=str(ARCHIVE))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    update.message.reply_text("\U0001F483Я бот для отслеживания танцевальных событий и покажу тебе, что происходит в мире танцев\U0001F525",
                              reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return TOP_LEVEL


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
            InlineKeyboardButton("Создать событие", callback_data=str(MANAGEMENT))
        ],
        [
            InlineKeyboardButton("Посмотреть архив", callback_data=str(ARCHIVE))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    query.edit_message_text(text="Что делаем дальше?", reply_markup=reply_markup)
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


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
    return TOP_LEVEL


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'До встречи!', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def creating_event(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Название события", callback_data=EDIT_NAME)
        ],
        [
            InlineKeyboardButton("Страна", callback_data=str(Y2023))
        ],
        [
            InlineKeyboardButton("Город", callback_data=EDIT_CITY)
        ],
        [
            InlineKeyboardButton("Дата начала", callback_data=EDIT_DATE_START)
        ],
        [
            InlineKeyboardButton("Дата окончания", callback_data=str(START_OVER))
        ],
        [
            InlineKeyboardButton("Описание", callback_data=EDIT_DESC)
        ],
        [
            InlineKeyboardButton("Картинка", callback_data=str(START_OVER))
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Заполните данные о событии", reply_markup=reply_markup
    )
    context.user_data['EDIT_NAME'] = ""
    context.user_data['EDIT_CITY'] = ""
    context.user_data['EDIT_DESC'] = ""
    context.user_data['EDIT_DATE_START'] = ""

    return CREATE_EVENT


def get_property_to_edit(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Отправьте информацию сообщением", reply_markup=reply_markup
    )
    return CREATE_EVENT


def set_property_value(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    user_data = context.user_data
    text = update.message.text
    category = user_data['property_to_edit']
    user_data[category] = text

    logger.info('category - %s', category)
    logger.info('set property - %s', text)
    # logger.info('id_msg = %s', update.message.message_id)
    # logger.info('id_chat = %s', update.message.chat_id)
    # bot = Bot(BOT_TOKEN)
    # bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    del user_data['property_to_edit']
    keyboard = [
        [
            InlineKeyboardButton("Название события: " + user_data[EDIT_NAME], callback_data=EDIT_NAME)
        ],
        [
            InlineKeyboardButton("Страна", callback_data=str(Y2023))
        ],
        [
            InlineKeyboardButton("Город " + user_data[EDIT_CITY], callback_data=EDIT_CITY)
        ],
        [
            InlineKeyboardButton("Дата начала " + str(user_data[EDIT_DATE_START]), callback_data=EDIT_DATE_START)
        ],
        [
            InlineKeyboardButton("Дата окончания", callback_data=str(START_OVER))
        ],
        [
            InlineKeyboardButton("Описание", callback_data=EDIT_DESC)
        ],
        [
            InlineKeyboardButton("Картинка", callback_data=str(START_OVER))
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(START_OVER))
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(user_data[EDIT_NAME] + "\n" + user_data[EDIT_CITY] + "\n" + user_data[EDIT_DESC] + "\n" + str(user_data[EDIT_DATE_START]),
                              reply_markup=reply_markup)
    return CREATE_EVENT


def get_date_to_edit(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    # keyboard = [
    #     [
    #         InlineKeyboardButton("Назад", callback_data=str(START_OVER))
    #     ],
    # ]
    # reply_markup = InlineKeyboardMarkup(keyboard)
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    query.edit_message_text(
        text="Выберите дату", reply_markup=calendar
    )
    return CREATE_DATE


def cal(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        query.edit_message_text(
            text=f"Select {LSTEP[step]}",
            reply_markup=key
        )
        return CREATE_DATE
    elif result:
        user_data = context.user_data
        category = user_data['property_to_edit']
        user_data[category] = str(result)

        logger.info('category - %s', category)
        logger.info('set date - %s', result)

        del user_data['property_to_edit']
        keyboard = [
            [
                InlineKeyboardButton("Название события: " + user_data[EDIT_NAME], callback_data=EDIT_NAME)
            ],
            [
                InlineKeyboardButton("Страна", callback_data=str(Y2023))
            ],
            [
                InlineKeyboardButton("Город " + user_data[EDIT_CITY], callback_data=EDIT_CITY)
            ],
            [
                InlineKeyboardButton("Дата начала " + str(user_data[EDIT_DATE_START]), callback_data=EDIT_DATE_START)
            ],
            [
                InlineKeyboardButton("Дата окончания", callback_data=str(START_OVER))
            ],
            [
                InlineKeyboardButton("Описание", callback_data=EDIT_DESC)
            ],
            [
                InlineKeyboardButton("Картинка", callback_data=str(START_OVER))
            ],
            [
                InlineKeyboardButton("Назад", callback_data=str(START_OVER))
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            user_data[EDIT_NAME] + "\n" + user_data[EDIT_CITY] + "\n" + user_data[EDIT_DESC] + "\n" + str(user_data[EDIT_DATE_START]),
            reply_markup=reply_markup
        )
        return CREATE_EVENT