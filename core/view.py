from datetime import datetime, date

from sqlalchemy import and_
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import const as con
from main_models import Session, Event


def set_default_userdata(context: CallbackContext, event_data=None):
    if event_data is None:
        context.user_data[con.EDIT_NAME] = ""
        context.user_data[con.EDIT_CITY] = ""
        context.user_data[con.EDIT_COUNTRY] = ""
        context.user_data[con.EDIT_DESC] = ""
        context.user_data[con.EDIT_DATE_START] = "Дата начала"
        context.user_data[con.EDIT_DATE_END] = "Дата окончания"
        context.user_data[con.EDIT_DATE_START + '_dt'] = None
        context.user_data[con.EDIT_DATE_END + '_dt'] = None
        context.user_data[con.EDIT_PHOTO] = ""
        context.user_data[con.PROPERTY_TO_EDIT] = None
        context.user_data[con.CALLBACK_QUERY] = None
        # context.user_data['page_event_pointer'] = [0, con.NUM_EVENTS_ON_PAGE]
        context.user_data[con.CURRENT_EVENT_ID] = None
        context.user_data[con.START_PAGE] = 0
        context.user_data[con.END_PAGE] = con.NUM_EVENTS_ON_PAGE
    else:
        context.user_data[con.EDIT_NAME] = event_data.event_name
        context.user_data[con.EDIT_CITY] = event_data.event_city
        context.user_data[con.EDIT_COUNTRY] = event_data.event_country
        context.user_data[con.EDIT_DESC] = event_data.event_desc
        context.user_data[con.EDIT_DATE_START] = "Дата начала " + str(event_data.event_date_start.day) + ' ' + con.RU_MONTH.get(
                event_data.event_date_start.month) + ' ' + str(event_data.event_date_start.year) + ' г.'
        context.user_data[con.EDIT_DATE_END] = "Дата окончания " + str(event_data.event_date_end.day) + ' ' + con.RU_MONTH.get(
                event_data.event_date_end.month) + ' ' + str(event_data.event_date_end.year) + ' г.'
        context.user_data[con.EDIT_DATE_START + '_dt'] = date(event_data.event_date_start.year, event_data.event_date_start.month, event_data.event_date_start.day)
        context.user_data[con.EDIT_DATE_END + '_dt'] = date(event_data.event_date_end.year, event_data.event_date_end.month, event_data.event_date_end.day)
        context.user_data[con.EDIT_PHOTO] = event_data.event_photo


def set_keyboard(context: CallbackContext, stage: str):
    user_data = context.user_data
    keyboard = None
    if stage == con.START:
        keyboard = [
            [InlineKeyboardButton("\U0001F4C6   Календарь событий", callback_data=con.CALENDAR)],
            [InlineKeyboardButton("\U0001FAA9   Создать событие", callback_data=con.MANAGEMENT)],
            # [InlineKeyboardButton("Посмотреть архив", callback_data=con.ARCHIVE)],
            # [InlineKeyboardButton("Пересоздать базу данных", callback_data=con.DELETE_EVENT)],
        ]
    if stage == con.CREATE_EVENT:
        keyboard = [
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_NAME] != "") +
                                  "   " + ("Название события" if user_data[con.EDIT_NAME] == "" else user_data[con.EDIT_NAME]), callback_data=con.EDIT_NAME)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_COUNTRY] != "") +
                                  "   " + ("Страна" if user_data[con.EDIT_COUNTRY] == "" else user_data[con.EDIT_COUNTRY]), callback_data=con.EDIT_COUNTRY)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_CITY] != "") +
                                  "   " + ("Город" if user_data[con.EDIT_CITY] == "" else user_data[con.EDIT_CITY]), callback_data=con.EDIT_CITY)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_START] != "Дата начала") +
                                  "   " + str(user_data[con.EDIT_DATE_START]), callback_data=con.EDIT_DATE_START)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_END] != "Дата окончания") +
                                  "   " + str(user_data[con.EDIT_DATE_END]), callback_data=con.EDIT_DATE_END)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DESC] != "") +
                                  "   Описание", callback_data=con.EDIT_DESC)],
            [InlineKeyboardButton(check_symbol(user_data[con.EDIT_PHOTO] != "") +
                                  "   Картинка", callback_data=con.EDIT_PHOTO)],
            [InlineKeyboardButton("\U0001F57A Предварительный просмотр", callback_data=con.EDIT_PREVIEW)],
            [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.START_OVER if user_data[con.CURRENT_EVENT_ID] is None else con.SELECT_EVENT + '_' + str(user_data[con.CURRENT_EVENT_ID]))],
        ]
    if stage == con.SELECT_ALM:
        button_list = []
        if user_data['page_event_pointer'][0] - con.NUM_EVENTS_ON_PAGE >= 0:
            button_list = [InlineKeyboardButton("\U000023EA Назад", callback_data=con.BACK_LIST)]
        if user_data['page_event_pointer'][0] + con.NUM_EVENTS_ON_PAGE < len(user_data[con.DATE_COUNTER]):
            button_list = button_list + [InlineKeyboardButton("\U000023E9 Вперед", callback_data=con.FORWARD_LIST)]
        keyboard = [
            button_list,
            [InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)]
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


def update_date_id_dict() -> dict:
    session = Session()
    future_events = session.query(Event).filter(and_(Event.event_date_start >= datetime.today(), Event.deleted == False)).order_by(
        Event.event_date_start)
    session.commit()
    date_floor_list = []
    id_event_dict = {}
    for event in future_events:
        ev = event.event_date_start.replace(day=1)
        date_floor_list.append(ev)
        id_event_dict.setdefault(ev, [0, []])
        num_id_list = id_event_dict[ev]
        num_id_list[0] = num_id_list[0] + 1
        id_list = num_id_list[1]
        id_list.append(event.id)
        id_event_dict[ev] = num_id_list
    return id_event_dict