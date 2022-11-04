import datetime
import re
import textwrap

from sqlalchemy import and_
from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

import const as con
from core.view import send_text_and_keyboard, generate_text_event, set_default_userdata, \
    update_date_id_dict, user_access, check_symbol
from events.view import creating_event
from main_models import Session, Event, Party, User


def show_event_calendar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    user_data[con.DATE_COUNTER] = update_date_id_dict()
    browse_event_calendar(update, context)
    return con.CALENDAR


def browse_event_calendar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    keyboard_list = []
    keyboard_nav = update_page_of_month_new(update, context)
    page_slice = slice(user_data[con.START_PAGE], user_data[con.END_PAGE])
    date_list = list(user_data[con.DATE_COUNTER].keys())
    for event_num in date_list[page_slice]:
        keyboard_list.append(
            [InlineKeyboardButton('%s %s г. (%s)' %
                                  (con.RU_MONTH_CAPITALIZED.get(event_num.month),
                                   str(event_num.year),
                                   user_data[con.DATE_COUNTER].get(event_num)[0]),
                                  callback_data=con.SELECT_ALM + '_' + str(event_num.year * 100 + event_num.month))]
        )
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard_list + keyboard_nav,
        message_text="Выберите дату начала события"
    )
    return con.CALENDAR


def show_events_of_month(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    user_data[con.CURRENT_EVENT_ID] = None
    keyboard_list = []
    event_date_int = int(re.search(pattern='\d{6}', string=query.data).group())
    y_from_data, m_from_data = event_date_int // 100, event_date_int - (event_date_int // 100) * 100
    id_list = user_data[con.DATE_COUNTER].get(datetime.date(y_from_data, m_from_data, 1))[1]

    session = Session()
    events_of_month = session.query(Event).filter(Event.id.in_(id_list)).order_by(Event.event_date_start)
    session.commit()

    for event in events_of_month:
        _date_str_for_button = ''
        if event.event_date_start.month != event.event_date_end.month:
            _date_str_for_button = '{:02d}'.format(event.event_date_start.day) + '.' + '{:02d}'.format(
                event.event_date_start.month) \
                                   + '-' + '{:02d}'.format(event.event_date_end.day) + '.' + '{:02d}'.format(
                event.event_date_end.month)
        else:
            _date_str_for_button = '{:02d}'.format(event.event_date_start.day) + '-' + '{:02d}'.format(
                event.event_date_end.day)
        keyboard_list.append(
            [InlineKeyboardButton(
                _date_str_for_button + ', ' + event.event_name + ' \U0001F4CD' + event.event_city + ', ' + event.event_country,
                width=40,
                callback_data=con.SELECT_EVENT + '_' + str(event.id))]
        )
    keyboard_nav = [
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK + '_' + str(event_date_int))],
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

    search = re.search(pattern=con.SELECT_EVENT + '_\d+', string=query.data).group()
    user_data[con.CURRENT_EVENT_ID] = int(re.search(pattern='\d+', string=search).group())
    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    check_in_event(update, context)
    status = update_checkbox_party(update, context)
    keyboard = [
        [InlineKeyboardButton(check_symbol(status == con.DEF_GO) + " Точно пойду", callback_data=con.SELECT_EVENT + '_' + str(event_id_int) + con.CHECK_IN + '_' + str(con.DEF_GO))],
        [InlineKeyboardButton(check_symbol(status == con.PROB_GO) + " Возможно пойду", callback_data=con.SELECT_EVENT + '_' + str(event_id_int) + con.CHECK_IN + '_' + str(con.PROB_GO))],
        [InlineKeyboardButton("Не пойду", callback_data=con.SELECT_EVENT + '_' + str(event_id_int) + con.CHECK_IN + '_' + str(con.DONT_GO))],
    ]
    if user_access(context) <= con.ADMIN_AL:
        keyboard.append([InlineKeyboardButton("\U0000270D Редактировать событие",
                                              callback_data=con.MANAGEMENT + '_' + str(event_id_int))])
        keyboard.append([InlineKeyboardButton("\U0001F5D1 Удалить событие",
                                              callback_data=con.DELETE_EVENT + '_' + str(event_id_int))])
    keyboard.append([InlineKeyboardButton("\U00002B05 К событиям месяца", callback_data=con.SELECT_ALM + '_' + str(
        event_data.event_date_start.year * 100 + event_data.event_date_start.month))])
    keyboard.append([InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)])
    if event_data:
        query.message.delete()
        _text = generate_text_event(
            event_data.event_name,
            event_data.event_city,
            event_data.event_country,
            'Дата начала ' + str(event_data.event_date_start.day) + ' ' + con.RU_MONTH.get(
                event_data.event_date_start.month) + ' ' + str(event_data.event_date_start.year) + ' г.',
            'Дата окончания ' + str(event_data.event_date_end.day) + ' ' + con.RU_MONTH.get(
                event_data.event_date_end.month) + ' ' + str(event_data.event_date_end.year) + ' г.',
            event_data.event_desc
        )
        # if event_data.event_photo:
        #     query.message.delete()
        send_text_and_keyboard(
            update=query.message.reply_photo if event_data.event_photo != '' else query.message.reply_text,
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
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.CALENDAR)]]
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


def check_in_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    event_id = user_data[con.CURRENT_EVENT_ID]
    user_id = user_data[con.LOGGED_USER_ID]
    search = re.search(pattern=con.CHECK_IN + '_\d+', string=query.data)
    if search:
        status_int = int(re.search(pattern='\d+', string=search.group()).group())
        session = Session()
        party_data = session.query(Party).filter(
            and_(Party.event_id == event_id, Event.deleted == False, Event.id == event_id, User.unique_id == user_id,
                 User.id == Party.user_id)).one_or_none()
        if party_data:
            party_data.status = status_int
        else:
            user = session.query(User).filter_by(unique_id=user_id).one_or_none()
            party = Party(
                event_id=event_id,
                user_id=user.id,
                status=status_int
            )
            session.add(party)
        session.commit()


def update_page_of_month_new(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_data = context.user_data
    start = user_data[con.START_PAGE]
    stop = user_data[con.END_PAGE]
    button_back, button_forward = [], []
    if query.data == con.FORWARD_LIST:
        start += con.NUM_EVENTS_ON_PAGE
        stop += con.NUM_EVENTS_ON_PAGE
    if query.data == con.BACK_LIST:
        start -= con.NUM_EVENTS_ON_PAGE
        stop -= con.NUM_EVENTS_ON_PAGE
    if query.data == con.CALENDAR:
        start = 0
        stop = con.NUM_EVENTS_ON_PAGE
    if re.match(pattern='^' + con.GO_BACK + '.*$', string=query.data) is not None:
        date_list = list(user_data[con.DATE_COUNTER].keys())
        event_date_int = int(re.search(pattern='\d{6}', string=query.data).group())
        y_from_data, m_from_data = event_date_int // 100, event_date_int - (event_date_int // 100) * 100
        start = (date_list.index(datetime.date(y_from_data, m_from_data, 1))) // con.NUM_EVENTS_ON_PAGE
        start = start * con.NUM_EVENTS_ON_PAGE
        stop = start + con.NUM_EVENTS_ON_PAGE
    if start + con.NUM_EVENTS_ON_PAGE < len(user_data[con.DATE_COUNTER]):
        button_forward = [InlineKeyboardButton("\U000023E9 Вперед", callback_data=con.FORWARD_LIST)]
    if start - con.NUM_EVENTS_ON_PAGE >= 0:
        button_back = [InlineKeyboardButton("\U000023EA Назад", callback_data=con.BACK_LIST)]
    user_data[con.START_PAGE] = start
    user_data[con.END_PAGE] = stop
    button_list = button_back + button_forward
    keyboard = [
        button_list,
        [InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)]
    ]
    return keyboard


def update_checkbox_party(update, context) -> int:
    query = update.callback_query
    user_data = context.user_data
    event_id = user_data[con.CURRENT_EVENT_ID]
    user_id = user_data[con.LOGGED_USER_ID]
    status = 0

    session = Session()
    party_data = session.query(Party).filter(
        and_(Party.event_id == event_id, Event.deleted == False, Event.id == event_id, User.unique_id == user_id,
             User.id == Party.user_id)).one_or_none()
    if party_data and party_data.status != 0:
        status = party_data.status
    return status
