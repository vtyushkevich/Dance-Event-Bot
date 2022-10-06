import logging
import const as con
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


def start(update: Update, context: CallbackContext) -> int:
    """Send a message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = [
        [InlineKeyboardButton("Посмотреть календарь событий", callback_data=con.START)],
        [InlineKeyboardButton("Создать событие", callback_data=con.MANAGEMENT)],
        [InlineKeyboardButton("Посмотреть архив", callback_data=con.ARCHIVE)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="\U0001F483 Я бот для отслеживания танцевальных событий и покажу тебе, что происходит в мире танцев "
             "\U0001F525",
        reply_markup=reply_markup
    )
    set_default_userdata(context)
    return con.TOP_LEVEL


def start_over(update: Update, context: CallbackContext) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Посмотреть календарь событий", callback_data=con.START)],
        [InlineKeyboardButton("Создать событие", callback_data=con.MANAGEMENT)],
        [InlineKeyboardButton("Посмотреть архив", callback_data=con.ARCHIVE)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Что делаем дальше?", reply_markup=reply_markup)
    set_default_userdata(context)
    return con.TOP_LEVEL


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'До встречи!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def creating_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = set_keyboard(context)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(
        text="Заполните данные о событии",
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def get_property_to_edit(update: Update, context: CallbackContext) -> int:
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Отправьте информацию сообщением", reply_markup=reply_markup
    )
    return con.CREATE_PROPERTY


def set_property_value(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data['property_to_edit']
    user_data[category] = text

    logger.info('category - %s', category)
    logger.info('set property - %s', text)
    # bot = Bot(BOT_TOKEN)
    # bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

    del user_data['property_to_edit']
    keyboard = set_keyboard(context)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=user_data[con.EDIT_NAME] + "\n" + user_data[con.EDIT_CITY] + "\n" + user_data[con.EDIT_COUNTRY] +
        "\n" + user_data[con.EDIT_DESC] + "\n" + str(user_data[con.EDIT_DATE_START]) +
        "\n" + str(user_data[con.EDIT_DATE_END]) + " ",
        reply_markup=reply_markup)
    return con.CREATE_EVENT


def get_date_to_edit(update: Update, context: CallbackContext) -> int:
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    calendar, step = DetailedTelegramCalendar(calendar_id=1).build()
    query.edit_message_text(
        text="Выберите дату", reply_markup=calendar
    )
    return con.CREATE_DATE


def cal(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    result, key, step = DetailedTelegramCalendar().process(query.data)
    if not result and key:
        query.edit_message_text(
            text=f"Select {LSTEP[step]}",
            reply_markup=key
        )
        return con.CREATE_DATE
    elif result:
        user_data = context.user_data
        category = user_data['property_to_edit']
        user_data[category] = str(result)

        logger.info('category - %s', category)
        logger.info('set date - %s', result)

        del user_data['property_to_edit']
        keyboard = set_keyboard(context)
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=user_data[con.EDIT_NAME] + "\n" + user_data[con.EDIT_CITY] + "\n" + user_data[con.EDIT_COUNTRY] +
            "\n" + user_data[con.EDIT_DESC] + "\n" + str(user_data[con.EDIT_DATE_START]) +
            "\n" + str(user_data[con.EDIT_DATE_END]) + " ",
            reply_markup=reply_markup
        )
        return con.CREATE_EVENT


def get_photo_to_edit(update: Update, context: CallbackContext) -> int:
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Загрузите фото", reply_markup=reply_markup
    )

    return con.CREATE_PHOTO


def set_photo(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    category = user_data['property_to_edit']
    photo_file = update.message.photo[1]
    logger.info('category - %s', photo_file)
    photo_file_1 = update.message.photo[1].get_file()
    logger.info('category - %s', photo_file_1)
    photo_file_1.download()
    # photo_file.download('event_photo.jpg')
    user_data[category] = photo_file

    logger.info('category - %s', category)

    del user_data['property_to_edit']
    keyboard = set_keyboard(context)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Предварительный просмотр" + "\n" + user_data[con.EDIT_NAME] + "\n" + user_data[con.EDIT_CITY] +
                              "\n" + user_data[con.EDIT_COUNTRY] + "\n" + user_data[con.EDIT_DESC] +
                              "\n" + str(user_data[con.EDIT_DATE_START]) + "\n" + str(user_data[con.EDIT_DATE_END]),
                              reply_markup=reply_markup
                              )

    # update.message.reply_photo( photo=photo_file, caption="Предварительный просмотр" + "\n" + user_data[EDIT_NAME]
    # + "\n" + user_data[EDIT_CITY] + "\n" + user_data[EDIT_COUNTRY] + "\n" + user_data[EDIT_DESC] + "\n" + str(
    # user_data[EDIT_DATE_START]) + "\n" + str(user_data[EDIT_DATE_END]), reply_markup=reply_markup )
    return con.CREATE_EVENT


def show_edit_preview(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Опубликовать", callback_data=con.PUBLISH_EVENT)],
        [InlineKeyboardButton("Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if context.user_data['EDIT_PHOTO']:
        query.message.reply_photo(
            photo=context.user_data['EDIT_PHOTO'],
            caption=user_data[con.EDIT_NAME] + "\n" + user_data[con.EDIT_CITY] + "\n" + user_data[con.EDIT_COUNTRY] +
            "\n" + user_data[con.EDIT_DESC] + "\n" + str(user_data[con.EDIT_DATE_START]) + "\n" + str(user_data[con.EDIT_DATE_END]),
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=user_data[con.EDIT_NAME] + "\n" + user_data[con.EDIT_CITY] + "\n" + user_data[con.EDIT_COUNTRY] +
            "\n" + user_data[con.EDIT_DESC] + "\n" + str(user_data[con.EDIT_DATE_START]) +
            "\n" + str(user_data[con.EDIT_DATE_END]) + " ",
            reply_markup=reply_markup
        )
    return con.CREATE_EVENT


def publish_event(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Ок", callback_data=con.START_OVER)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Событие опубликовано!",
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def set_default_userdata(context: CallbackContext):
    context.user_data[con.EDIT_NAME] = "Название события"
    context.user_data[con.EDIT_CITY] = ""
    context.user_data[con.EDIT_COUNTRY] = ""
    context.user_data[con.EDIT_DESC] = ""
    context.user_data[con.EDIT_DATE_START] = ""
    context.user_data[con.EDIT_DATE_END] = ""
    context.user_data[con.EDIT_PHOTO] = ""


def set_keyboard(context: CallbackContext):
    user_data = context.user_data
    keyboard = [
        [InlineKeyboardButton("Название события: " + user_data[con.EDIT_NAME], callback_data=con.EDIT_NAME)],
        [InlineKeyboardButton("Страна" + user_data[con.EDIT_COUNTRY], callback_data=con.EDIT_COUNTRY)],
        [InlineKeyboardButton("Город " + user_data[con.EDIT_CITY], callback_data=con.EDIT_CITY)],
        [InlineKeyboardButton("Дата начала " + str(user_data[con.EDIT_DATE_START]), callback_data=con.EDIT_DATE_START)],
        [InlineKeyboardButton("Дата окончания" + str(user_data[con.EDIT_DATE_END]), callback_data=con.EDIT_DATE_END)],
        [InlineKeyboardButton("Описание", callback_data=con.EDIT_DESC)],
        [InlineKeyboardButton("Картинка", callback_data=con.EDIT_PHOTO)],
        [InlineKeyboardButton("Предварительный просмотр", callback_data=con.EDIT_PREVIEW)],
        [InlineKeyboardButton("Назад", callback_data=con.START_OVER)],
    ]
    return keyboard


def check_symbol(checked: bool):
    if checked:
        return "\U00002705"
    else:
        return "\U0000274C"
