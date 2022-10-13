from pathlib import Path
import logging
import const as con
from models import MonthEventsData
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove,
    Message, Bot
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from config import BOT_TOKEN
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import datetime, date, timedelta

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
    _text = generate_text_event(event_name='FESTIVALITO LA VIDA, MÚSICA Y TANGO 2022', event_city='Челябинск',
                                event_country='Россия',
                                event_desc='Душевное вятское гостеприимство, высокий уровень организации мероприятий, атмосфера уюта, '
                                           'праздника, дружбы,любви и радости, комфорт для каждого участника - всё это ждет вас на любом нашем танго-мероприятии.'
                                           'Шикарный зал 700 кв. метров в самом центре города, шикарный пол, звук и свет,'
                                           ' любимые маэстрос, оркестры и танго-диджеи и многое другое мы готовим для участников осеннего фестиваля.'
                                           'В программе: ПЯТЬ милонг, ТРИ оркестра.'
                                           'Показательные выступления Себастьяна Арсе и Марии Мариновой.'
                                           'Показательные выступления Михаила Надточего и Эльвиры Ламбо.',
                                event_date_end='2022-10-30', event_date_start='2022-10-28')
    context.user_data['FAKE_TEXT'] = _text
    return con.TOP_LEVEL


def start_over(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = set_keyboard(context, con.START)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if context.user_data['FAKE_TEXT']:
        query.delete_message()
        query.message.reply_text(
            text="\U000026F3 Что делаем дальше?",
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text="\U000026F3 Что делаем дальше?",
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
    keyboard = set_keyboard(context, con.CREATE_EVENT)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.message.caption:
        query.message.delete()
        query.message.reply_text(
            text=con.TEXT_REQUEST[con.CREATE_EVENT],
            reply_markup=reply_markup
        )
    else:
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
    _validation_passed, _validation_comment = validate_user_data(category, text)
    if _validation_passed:
        user_data[category] = text

        logger.info('category - %s', category)
        logger.info('set property - %s', text)
        # bot = Bot(BOT_TOKEN)
        # bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

        del user_data['property_to_edit']
        keyboard = set_keyboard(context, con.CREATE_EVENT)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text=con.TEXT_REQUEST[con.CREATE_EVENT],
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text=_validation_comment,
            reply_markup=reply_markup
        )
        return con.CREATE_PROPERTY
    return con.CREATE_EVENT


def get_date_to_edit(update: Update, context: CallbackContext) -> int:
    text = update.callback_query.data
    context.user_data['property_to_edit'] = text
    logger.info("property_to_edit - %s", text)

    query = update.callback_query
    query.answer()
    calendar, step = DetailedTelegramCalendar(calendar_id=1, additional_buttons=[
        {"text": "\U00002B05 Назад", 'callback_data': con.GO_BACK}]).build()
    query.edit_message_text(
        text=con.TEXT_REQUEST[text],
        reply_markup=calendar
    )
    return con.CREATE_DATE


def cal(update: Update, context: CallbackContext):
    _datetype = {con.EDIT_DATE_START: 'Дата начала ', con.EDIT_DATE_END: 'Дата окончания '}
    query = update.callback_query
    logger.info('def cal - %s', update.callback_query.data)
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
        user_data[category + '_dt'] = result
        _validation_passed, _validation_comment = validate_user_data(category + '_dt', checked_date=result)
        if _validation_passed:
            _validation_passed, _validation_comment = validate_user_data(
                category + '_dt',
                checked_date=user_data[con.EDIT_DATE_START + '_dt'],
                checked_sec_date=user_data[con.EDIT_DATE_END + '_dt']
            )
        if _validation_passed:
            user_data[category] = _datetype[category] + str(result)

            logger.info('category - %s', category)
            logger.info('set date - %s', result)

            del user_data['property_to_edit']
            keyboard = set_keyboard(context, con.CREATE_EVENT)
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text=con.TEXT_REQUEST[con.CREATE_EVENT],
                reply_markup=reply_markup
            )
        else:
            user_data[category + '_dt'] = None
            keyboard = [
                [InlineKeyboardButton("\U00002B05 Назад", callback_data=category)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text=_validation_comment,
                reply_markup=reply_markup
            )
            return con.CREATE_DATE
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
    photo_file = update.message.photo[-1]
    logger.info('set_photo____photo_file - %s', photo_file)
    logger.info('set_photo____photo_file.file_id - %s', photo_file.file_id)
    user_data[category] = photo_file.file_id

    logger.info('category - %s', category)

    del user_data['property_to_edit']
    keyboard = set_keyboard(context, con.CREATE_EVENT)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        con.TEXT_REQUEST[con.CREATE_EVENT],
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def set_doc(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    category = user_data['property_to_edit']
    doc_file = update.message.document
    logger.info('set_doc____doc_file - %s', doc_file)
    photo_file = doc_file.get_file()
    photo_file.download(custom_path='./banners/' + photo_file.file_unique_id)

    _validation_passed, _validation_comment = validate_user_data(category, userdata=photo_file.file_size)
    _validation_mime_passed, _validation_mime_comment = validate_user_data(category, mimetype=doc_file.mime_type)
    if _validation_passed and _validation_mime_passed:
        user_data[category] = Path.cwd() / 'banners' / photo_file.file_unique_id
        del user_data['property_to_edit']
        keyboard = set_keyboard(context, con.CREATE_EVENT)
        reply_markup = InlineKeyboardMarkup(keyboard)
        _msg = update.message.reply_photo(
            photo=open(user_data[category], 'rb'),
            # reply_markup=reply_markup
        )
        user_data[category] = _msg.photo[-1]
        update.message.reply_text(
            con.TEXT_REQUEST[con.CREATE_EVENT],
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            text=(_validation_comment if _validation_comment else _validation_mime_comment),
            reply_markup=reply_markup
        )
        return con.CREATE_PHOTO
    return con.CREATE_EVENT


def show_edit_preview(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    query = update.callback_query
    query.answer()
    _validation_passed, _validation_comment = validate_user_data(con.PUBLISH_EVENT, userdata=context)
    if _validation_passed:
        keyboard = [
            [InlineKeyboardButton("Опубликовать", callback_data=con.PUBLISH_EVENT)],
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    _text = generate_text_event(user_data[con.EDIT_NAME], user_data[con.EDIT_CITY], user_data[con.EDIT_COUNTRY],
                                user_data[con.EDIT_DATE_START], user_data[con.EDIT_DATE_END], user_data[con.EDIT_DESC])
    if context.user_data[con.EDIT_PHOTO]:
        logger.info('show_edit_preview - %s', context.user_data[con.EDIT_PHOTO])
        query.message.delete()
        query.message.reply_photo(
            photo=context.user_data[con.EDIT_PHOTO],
            caption=_text,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=_text,
            reply_markup=reply_markup
        )
    return con.CREATE_EVENT


def publish_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = [
        [InlineKeyboardButton("Ок", callback_data=con.START_OVER)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.delete()
    query.message.reply_text(
        text="\U0001F4F0 Событие опубликовано!",
        reply_markup=reply_markup
    )
    return con.CREATE_EVENT


def show_event_calendar(update: Update, context: CallbackContext) -> int:
    # month_events_data_0 = MonthEventsData('month_events_data_0')
    # month_events_data_1 = MonthEventsData('month_events_data_1')
    # month_events_data_2 = MonthEventsData('month_events_data_2')
    # month_events_data_3 = MonthEventsData('month_events_data_3')
    # month_events_data_4 = MonthEventsData('month_events_data_4')
    #
    # month_events_data_0.random()
    # month_events_data_1.random()
    # month_events_data_2.random()
    # month_events_data_3.random()
    # month_events_data_4.random()
    #
    # context.user_data['month_events_data_0'] = month_events_data_0
    # context.user_data['month_events_data_1'] = month_events_data_1
    # context.user_data['month_events_data_2'] = month_events_data_2
    # context.user_data['month_events_data_3'] = month_events_data_3
    # context.user_data['month_events_data_4'] = month_events_data_4
    query = update.callback_query
    query.answer()
    _text = context.user_data['FAKE_TEXT']
    logger.info('show_event_calendar - %s', _text)
    if _text:
        query.delete_message()
        keyboard = set_keyboard(context, con.CALENDAR)
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_photo(
            photo='AgACAgIAAxkBAAIC8mNEWei1pJxkp_kZXTGbHNV6tF1ZAALfwzEbsOsgSjmF2xeA2UOiAQADAgADbQADKgQ',
            caption=_text,
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [InlineKeyboardButton("Ок", callback_data=con.GO_BACK)],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.edit_text(
            text="Нет активных событий",
            reply_markup=reply_markup
        )
    return con.CALENDAR


def delete_event_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.delete_message()
    keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=con.DELETE_EVENT_OK)],
        [InlineKeyboardButton("Назад", callback_data=con.CALENDAR)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(
        text="Вы уверены, что хотите удалить событие?",
        reply_markup=reply_markup
    )
    return con.CALENDAR


def delete_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['FAKE_TEXT'] = ''
    keyboard = [
        [InlineKeyboardButton("Ок", callback_data=con.GO_BACK)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(
        text="Событие удалено!",
        reply_markup=reply_markup
    )
    return con.CALENDAR


def set_default_userdata(context: CallbackContext):
    context.user_data[con.EDIT_NAME] = "Название события"
    context.user_data[con.EDIT_CITY] = "Город"
    context.user_data[con.EDIT_COUNTRY] = "Страна"
    context.user_data[con.EDIT_DESC] = ""
    context.user_data[con.EDIT_DATE_START] = "Дата начала"
    context.user_data[con.EDIT_DATE_END] = "Дата окончания"
    context.user_data[con.EDIT_DATE_START + '_dt'] = None
    context.user_data[con.EDIT_DATE_END + '_dt'] = None
    context.user_data[con.EDIT_PHOTO] = ""


def set_keyboard(context: CallbackContext, stage: str):
    user_data = context.user_data
    keyboard = None
    if stage == con.START:
        keyboard = [
            [InlineKeyboardButton("\U0001F4C6   Календарь событий", callback_data=con.CALENDAR)],
            [InlineKeyboardButton("\U0001FAA9   Создать событие", callback_data=con.MANAGEMENT)],
            [InlineKeyboardButton("\U0001F5C4   Посмотреть архив", callback_data=con.ARCHIVE)],
        ]
    if stage == con.CREATE_EVENT:
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
    if stage == con.CALENDAR:
        keyboard = [
            [InlineKeyboardButton("\U0001F5D1 Удалить событие", callback_data=con.DELETE_EVENT)],
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
            # [InlineKeyboardButton(str(context.user_data['month_events_data_0'].month) + ' ' + str(context.user_data['month_events_data_0'].year), callback_data=context.user_data['month_events_data_0'].callback)],
            # [InlineKeyboardButton(str(context.user_data['month_events_data_1'].month) + ' ' + str(context.user_data['month_events_data_1'].year), callback_data=context.user_data['month_events_data_1'].callback)],
            # [InlineKeyboardButton(str(context.user_data['month_events_data_2'].month) + ' ' + str(context.user_data['month_events_data_2'].year), callback_data=context.user_data['month_events_data_2'].callback)],
            # [InlineKeyboardButton(str(context.user_data['month_events_data_3'].month) + ' ' + str(context.user_data['month_events_data_3'].year), callback_data=context.user_data['month_events_data_3'].callback)],
            # [InlineKeyboardButton(str(context.user_data['month_events_data_4'].month) + ' ' + str(context.user_data['month_events_data_4'].year), callback_data=context.user_data['month_events_data_4'].callback)],
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


def validate_user_data(category: str, userdata=None, mimetype=None, checked_date=None, checked_sec_date=None):
    validation_passed, validation_comment = True, None
    if category == con.EDIT_NAME or category == con.EDIT_COUNTRY or category == con.EDIT_CITY:
        _name_len = 50
        validation_passed = len(userdata) < _name_len
        if not validation_passed:
            validation_comment = '\U0001F6AB Название не должно быть длиннее ' + str(_name_len) + ' символов'
            return validation_passed, validation_comment
    if category == con.EDIT_DESC:
        _name_len = 1000
        validation_passed = len(userdata) < _name_len
        if not validation_passed:
            validation_comment = '\U0001F6AB Описание не должно быть длиннее ' + str(_name_len) + ' символов'
            return validation_passed, validation_comment
    if category == con.EDIT_PHOTO:
        if userdata:
            _name_len = 10485760
            validation_passed = userdata < _name_len
            if not validation_passed:
                validation_comment = '\U0001F6AB Картинка не должна весить более 10 Мб'
                return validation_passed, validation_comment
        if mimetype:
            validation_passed = mimetype == 'image/gif' or mimetype == 'image/jpeg' or mimetype == 'image/png'
            if not validation_passed:
                validation_comment = '\U0001F6AB Некорректный формат файла'
                return validation_passed, validation_comment
    if category == con.EDIT_DATE_START + '_dt' and checked_date is not None or \
            category == con.EDIT_DATE_END + '_dt' and checked_date is not None:
        validation_passed = checked_date >= date.today()
        if not validation_passed:
            validation_comment = '\U0001F6AB Дата события не должна быть в прошлом времени'
            return validation_passed, validation_comment
    if (category == con.EDIT_DATE_START + '_dt' or category == con.EDIT_DATE_END + '_dt')\
            and checked_date is not None and checked_sec_date is not None:
        _delta: timedelta = (checked_sec_date - checked_date)
        validation_passed = _delta.total_seconds() > 0
        if not validation_passed:
            validation_comment = '\U0001F6AB Дата окончания события не должна быть раньше начала события'
            return validation_passed, validation_comment
    if category == con.PUBLISH_EVENT:
        validation_passed = userdata.user_data[con.EDIT_NAME] != "Название события" \
                            and userdata.user_data[con.EDIT_CITY] != "Город" \
                            and userdata.user_data[con.EDIT_COUNTRY] != "Страна" \
                            and userdata.user_data[con.EDIT_DESC] != "" \
                            and userdata.user_data[con.EDIT_DATE_START + '_dt'] is not None \
                            and userdata.user_data[con.EDIT_DATE_END + '_dt'] is not None
        if not validation_passed:
            validation_comment = '\U0001F6AB Не заполнены все поля события'
            return validation_passed, validation_comment
    return validation_passed, validation_comment


def check_symbol(checked: bool):
    if checked:
        return "\U00002705"
    else:
        return "\U00002611"
        # return "\U0000274C" - red cross
