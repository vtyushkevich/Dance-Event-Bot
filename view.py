import logging
import const as con
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove,
    # Message, Bot
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
# from config import BOT_TOKEN
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    """Send a message on `/start`."""
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    keyboard = set_keyboard(context, con.START)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text="\U0001F483 Я бот для отслеживания танцевальных событий и расскажу, что происходит в мире танцев "
             "\U0001F525",
        reply_markup=reply_markup
    )
    set_default_userdata(context)
    return con.TOP_LEVEL


def start_over(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = set_keyboard(context, con.START)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="Что делаем дальше?",
        reply_markup=reply_markup
    )
    set_default_userdata(context)
    return con.TOP_LEVEL


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'До встречи!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def creating_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = set_keyboard(context, con.CREATE)
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(
        text=con.TEXT_REQUEST[con.CREATE_EVENT],
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
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=con.TEXT_REQUEST[text],
        reply_markup=reply_markup
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
    keyboard = set_keyboard(context, con.CREATE)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        text=con.TEXT_REQUEST[con.CREATE_EVENT],
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def get_date_to_edit(update: Update, context: CallbackContext) -> int:
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    calendar, step = DetailedTelegramCalendar(calendar_id=1, additional_buttons=[
        {"text": "\U00002B05 Назад", 'callback_data': con.GO_BACK}]).build()
    # logger.info("type(calendar) - %s", type(calendar))
    query.edit_message_text(
        text=con.TEXT_REQUEST[text],
        reply_markup=calendar
    )
    return con.CREATE_DATE


def cal(update: Update, context: CallbackContext):
    _datetype = {con.EDIT_DATE_START: 'Дата начала ', con.EDIT_DATE_END: 'Дата окончания '}
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
        user_data[category] = _datetype[category] + str(result)

        logger.info('category - %s', category)
        logger.info('set date - %s', result)

        del user_data['property_to_edit']
        keyboard = set_keyboard(context, con.CREATE)
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=con.TEXT_REQUEST[con.CREATE_EVENT],
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
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=con.TEXT_REQUEST[text],
        reply_markup=reply_markup
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
    keyboard = set_keyboard(context, con.CREATE)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        con.TEXT_REQUEST[con.CREATE_EVENT],
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
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    _text = generate_text_event(user_data[con.EDIT_NAME], user_data[con.EDIT_CITY], user_data[con.EDIT_COUNTRY],
                                user_data[con.EDIT_DATE_START], user_data[con.EDIT_DATE_END], user_data[con.EDIT_DESC])
    if context.user_data['EDIT_PHOTO']:
        query.message.reply_photo(
            photo=context.user_data['EDIT_PHOTO'],
            caption=_text,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=_text,
            reply_markup=reply_markup
        )
    return con.CREATE_EVENT


def show_event_calendar():
    pass


def publish_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Ок", callback_data=con.START_OVER)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(
        text="Событие опубликовано!",
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def set_default_userdata(context: CallbackContext):
    context.user_data[con.EDIT_NAME] = "Название события"
    context.user_data[con.EDIT_CITY] = "Город"
    context.user_data[con.EDIT_COUNTRY] = "Страна"
    context.user_data[con.EDIT_DESC] = ""
    context.user_data[con.EDIT_DATE_START] = "Дата начала"
    context.user_data[con.EDIT_DATE_END] = "Дата окончания"
    context.user_data[con.EDIT_PHOTO] = ""


def set_keyboard(context: CallbackContext, stage: str):
    user_data = context.user_data
    keyboard = None
    if stage == con.START:
        keyboard = [
            [InlineKeyboardButton("\U0001F4C6   Календарь событий", callback_data=con.START)],
            [InlineKeyboardButton("\U0001FAA9   Создать событие", callback_data=con.MANAGEMENT)],
            [InlineKeyboardButton("\U0001F5C4   Посмотреть архив", callback_data=con.ARCHIVE)],
        ]
    if stage == con.CREATE:
        keyboard = [
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_NAME] != "Название события") +
                                  "   " + user_data[con.EDIT_NAME], callback_data=con.EDIT_NAME)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_COUNTRY] != "Страна") +
                                  "   " + user_data[con.EDIT_COUNTRY], callback_data=con.EDIT_COUNTRY)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_CITY] != "Город") +
                                  "   " + user_data[con.EDIT_CITY], callback_data=con.EDIT_CITY)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_START] != "Дата начала") +
                                  "   " + str(user_data[con.EDIT_DATE_START]), callback_data=con.EDIT_DATE_START)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_END] != "Дата окончания") +
                                  "   " + str(user_data[con.EDIT_DATE_END]), callback_data=con.EDIT_DATE_END)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DESC] != "") +
                                  "   Описание", callback_data=con.EDIT_DESC)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_PHOTO] != "") +
                                  "   Картинка", callback_data=con.EDIT_PHOTO)],
            [InlineKeyboardButton("\U0001F57A Предварительный просмотр", callback_data=con.EDIT_PREVIEW)],
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.START_OVER)],
        ]
    return keyboard


def generate_text_event(
        event_name: str,
        event_city: str,
        event_country: str,
        event_date_start: str,
        event_date_end: str,
        event_desc: str,
):
    _text = '\U0001F46B ' + event_name + '\n' * 2
    _text = _text + '\U0001F4CD ' + ('' if event_city == 'Город' else event_city + ', ')
    _text = _text + ('' if event_country == 'Страна' else event_country) + '\n' * 2
    _text = _text + '\U0001F680 ' + ("Дата начала не указана" if event_date_start == "Дата начала" else
                                     event_date_start) + '\n' * 2
    _text = _text + '\U0001F3C1 ' + ("Дата окончания не указана" if event_date_end == "Дата окончания" else
                                     event_date_end) + '\n' * 2

    _text = _text + ("" if event_desc == "" else
                     'О событии:\n' + event_desc)
    return _text


def check_symbol(checked: bool):
    if checked:
        return "\U00002705"
    else:
        return "\U00002611"
        # return "\U0000274C" - red cross
