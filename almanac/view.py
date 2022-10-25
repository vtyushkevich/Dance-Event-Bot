import datetime
import re

from sqlalchemy import and_
from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

import const as con
from core.view import set_keyboard, send_text_and_keyboard, generate_text_event, set_default_userdata
from events.view import creating_event
from main_models import Base, Session, Event


def show_event_calendar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    session = Session()
    future_events = session.query(Event).filter(and_(Event.event_date_start >= datetime.date.today(), Event.deleted == False)).order_by(
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
    user_data['date_counter'] = id_event_dict
    browse_event_calendar(update, context)
    return con.CALENDAR


def browse_event_calendar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    keyboard_list = []
    date_list = list(user_data['date_counter'].keys())
    for event_num in date_list[user_data['page_event_pointer'][0]:user_data['page_event_pointer'][1]]:
        keyboard_list.append(
            [InlineKeyboardButton('%s %s г. (%s)' %
                                  (con.RU_MONTH_CAPITALIZED.get(event_num.month),
                                   str(event_num.year),
                                   user_data['date_counter'].get(event_num)[0]),
                                  callback_data=con.SELECT_ALM + '_' + str(event_num.year * 100 + event_num.month))]
        )
    keyboard_nav = set_keyboard(context, con.SELECT_ALM)
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard_list + keyboard_nav,
        message_text="Выберите дату начала события"
    )


def show_events_of_month(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    user_data[con.CURRENT_EVENT_ID] = None
    keyboard_list = []
    event_date_int = int(re.search(pattern='\d{6}', string=query.data).group())
    y_from_data, m_from_data = event_date_int // 100, event_date_int - (event_date_int // 100)*100
    id_list = user_data['date_counter'].get(datetime.date(y_from_data, m_from_data, 1))[1]

    session = Session()
    events_of_month = session.query(Event).filter(Event.id.in_(id_list)).order_by(Event.event_date_start)
    session.commit()

    for event in events_of_month:
        keyboard_list.append(
            [InlineKeyboardButton(
                str(event.event_date_start.day) + '-' + str(event.event_date_end.day) +
                ', ' + event.event_name + ' \U0001F4CD' + event.event_city + ', ' + event.event_country,
                callback_data=con.SELECT_EVENT + '_' + str(event.id))
            ]
        )
    keyboard_nav = [
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
        [InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)]
    ]
    if query.message.caption:
        query.delete_message()
        send_text_and_keyboard(
            update=query.message.reply_text,
            keyboard=keyboard_list + keyboard_nav,
            message_text=con.RU_MONTH_CAPITALIZED[m_from_data] + ' ' + str(y_from_data) + " г.\nВыберите событие"
        )
    else:
        send_text_and_keyboard(
            update=query.message.edit_text,
            keyboard=keyboard_list + keyboard_nav,
            message_text=con.RU_MONTH_CAPITALIZED[m_from_data] + ' ' + str(y_from_data) + " г.\nВыберите событие"
        )
    return con.CALENDAR


def show_selected_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    user_data[con.CURRENT_EVENT_ID] = int(re.search(pattern='\d+', string=query.data).group())
    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    keyboard = [
        [InlineKeyboardButton("\U0000270D Редактировать событие", callback_data=con.MANAGEMENT + '_' + str(event_id_int))],
        [InlineKeyboardButton("\U0001F5D1 Удалить событие", callback_data=con.DELETE_EVENT + '_' + str(event_id_int))],
        [InlineKeyboardButton("\U00002B05 К событиям месяца",
                              callback_data=con.SELECT_ALM + '_' + str(event_data.event_date_start.year * 100 + event_data.event_date_start.month))],
        [InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)],
    ]
    if event_data:
        _text = generate_text_event(
            event_data.event_name,
            event_data.event_city,
            event_data.event_country,
            'Дата начала ' + str(event_data.event_date_start.day) + ' ' + con.RU_MONTH.get(event_data.event_date_start.month) + ' ' + str(event_data.event_date_start.year) + ' г.',
            'Дата окончания ' + str(event_data.event_date_end.day) + ' ' + con.RU_MONTH.get(event_data.event_date_end.month) + ' ' + str(event_data.event_date_end.year) + ' г.',
            event_data.event_desc
        )
        if event_data.event_photo:
            query.message.delete()
        send_text_and_keyboard(
            update=query.message.reply_photo if event_data.event_photo != '' else query.edit_message_text,
            keyboard=keyboard,
            message_text=_text,
            photo=event_data.event_photo if event_data.event_photo != '' else None
        )
    return con.CALENDAR


def delete_event_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    query.delete_message()
    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=con.DELETE_CONFIRMED + '_' + str(event_id_int))],
        [InlineKeyboardButton("Назад", callback_data=con.SELECT_EVENT + '_' + str(event_id_int))],
    ]
    send_text_and_keyboard(
        update=query.message.reply_text,
        keyboard=keyboard,
        message_text=event_data.event_name + "\n" + "Вы уверены, что хотите удалить событие?",
    )
    return con.CALENDAR


def delete_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    if event_data:
        event_data.deleted = True
        session.commit()
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.GO_BACK)]]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text="Событие удалено!",
    )
    return con.CALENDAR


def edit_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    if event_data:
        set_default_userdata(context, event_data)
    creating_event(update, context)
    return con.CREATE_EVENT


def show_select_2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    Base.metadata.drop_all()
    Base.metadata.create_all()
    return con.TOP_LEVEL


def update_page_of_month(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    start = user_data['page_event_pointer'][0]
    stop = user_data['page_event_pointer'][1]
    if query.data == con.FORWARD_LIST:
        if start + con.NUM_EVENTS_ON_PAGE > len(user_data['date_counter']):
            user_data['page_event_pointer'][0] = start
            user_data['page_event_pointer'][1] = stop
        else:
            user_data['page_event_pointer'][0] = start + con.NUM_EVENTS_ON_PAGE
            user_data['page_event_pointer'][1] = stop + con.NUM_EVENTS_ON_PAGE
    else:
        if start - con.NUM_EVENTS_ON_PAGE < 0:
            user_data['page_event_pointer'][0] = start
            user_data['page_event_pointer'][1] = stop
        else:
            user_data['page_event_pointer'][0] = start - con.NUM_EVENTS_ON_PAGE
            user_data['page_event_pointer'][1] = stop - con.NUM_EVENTS_ON_PAGE
    browse_event_calendar(update, context)
    return con.CALENDAR