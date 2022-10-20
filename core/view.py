from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import const as con


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
    context.user_data[con.PROPERTY_TO_EDIT] = None
    context.user_data[con.CALLBACK_QUERY] = None


def set_keyboard(context: CallbackContext, stage: str):
    user_data = context.user_data
    keyboard = None
    if stage == con.START:
        keyboard = [
            [InlineKeyboardButton("\U0001F4C6   Календарь событий", callback_data=con.CALENDAR)],
            [InlineKeyboardButton("\U0001FAA9   Создать событие", callback_data=con.MANAGEMENT)],
            [InlineKeyboardButton("Посмотреть архив", callback_data=con.ARCHIVE)],
            # [InlineKeyboardButton("Выбор даты в календаре №1", callback_data='select1')],
            [InlineKeyboardButton("Пересоздать базу данных", callback_data='select2')],
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


def send_text_and_keyboard(update, keyboard, message_text, photo=None):
    if message_text is None:
        update(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        if isinstance(keyboard, str):
            reply_markup = keyboard
        else:
            reply_markup = InlineKeyboardMarkup(keyboard)
        if photo is None:
            update(
                text=message_text,
                reply_markup=reply_markup
            )
        else:
            update(
                caption=message_text,
                reply_markup=reply_markup,
                photo=photo
            )


def generate_fake_event_date():
    pass