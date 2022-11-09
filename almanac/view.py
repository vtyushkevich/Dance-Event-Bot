import datetime
import re

from sqlalchemy import and_, or_
from sqlalchemy.orm import with_polymorphic
from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

import const as con
import emoji
from core.view import send_text_and_keyboard, generate_text_event, set_default_userdata, \
    update_date_id_dict, user_access, check_symbol, get_full_user_name, get_username_from_text
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
                f"{_date_str_for_button}, {event.event_name} {emoji.PIN}{event.event_city}, {event.event_country}",
                callback_data=f"{con.SELECT_EVENT}_{event.id}")]
        )
    keyboard_nav = [
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=f"{con.GO_BACK}_{event_date_int}")],
        [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)]
    ]
    update_func = query.message.edit_text
    if query.message.caption:
        query.delete_message()
        update_func = query.message.reply_text
    send_text_and_keyboard(
        update=update_func,
        keyboard=keyboard_list + keyboard_nav,
        message_text=f"{con.RU_MONTH_CAPITALIZED[m_from_data]} {y_from_data} г.\nВыберите событие"
    )
    session.close()
    return con.CALENDAR


def show_selected_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    from_find_cb = ''
    from_find_events = re.search(pattern=con.ADD_USER, string=query.data)
    if from_find_events:
        from_find_cb = f"_{con.ADD_USER}"
    search = re.search(pattern=f"{con.SELECT_EVENT}_\d+", string=query.data).group()
    user_data[con.CURRENT_EVENT_ID] = int(re.search(pattern="\d+", string=search).group())
    event_id_int = user_data[con.CURRENT_EVENT_ID]
    session = Session()
    event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
    session.commit()
    check_in_event(update, context)
    status = update_checkbox_party(context)
    status_numbers = update_numbers_who_goes(event_id=event_id_int)
    keyboard = [
        [InlineKeyboardButton(f"Кто пойдет ({status_numbers[0]})", callback_data=f"{con.WHO_GOES}_{con.DEF_GO}{from_find_cb}")],
        [InlineKeyboardButton(f"Кто возможно пойдет ({status_numbers[1]})", callback_data=f"{con.WHO_GOES}_{con.PROB_GO}{from_find_cb}")],
        [InlineKeyboardButton(f"{check_symbol(status == con.DEF_GO)} Точно пойду", callback_data=f"{con.SELECT_EVENT}_{event_id_int}{con.CHECK_IN}_{con.DEF_GO}{from_find_cb}")],
        [InlineKeyboardButton(f"{check_symbol(status == con.PROB_GO)} Возможно пойду", callback_data=f"{con.SELECT_EVENT}_{event_id_int}{con.CHECK_IN}_{con.PROB_GO}{from_find_cb}")],
        [InlineKeyboardButton(f"Не пойду", callback_data=f"{con.SELECT_EVENT}_{event_id_int}{con.CHECK_IN}_{con.DONT_GO}{from_find_cb}")],
    ]
    if user_access(context) <= con.ADMIN_AL and from_find_events is None:
        keyboard.append([InlineKeyboardButton(f"{emoji.EDIT_HAND} Редактировать событие", callback_data=f"{con.MANAGEMENT}_{event_id_int}")])
        keyboard.append([InlineKeyboardButton(f"{emoji.TRASH_BIN} Удалить событие", callback_data=f"{con.DELETE_EVENT}_{event_id_int}")])
    if from_find_events is None:
        keyboard.append([InlineKeyboardButton(f"{emoji.LEFT_ARROW} К событиям месяца", callback_data=f"{con.SELECT_ALM}_{event_data.event_date_start.year * 100 + event_data.event_date_start.month}")])
    else:
        keyboard.append([InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад к событиям пользователя", callback_data=context.user_data[con.CALLBACK_QUERY].data)])
    keyboard.append([InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)])
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
        [InlineKeyboardButton("Удалить", callback_data=f"{con.DELETE_CONFIRMED}_{event_id_int}")],
        [InlineKeyboardButton("Назад", callback_data=f"{con.SELECT_EVENT}_{event_id_int}")],
    ]
    send_text_and_keyboard(
        update=query.message.reply_text,
        keyboard=keyboard,
        message_text=f"{event_data.event_name}\nВы уверены, что хотите удалить событие?"
    )
    session.close()
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
    session.close()
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
    session.close()
    return con.CREATE_EVENT


def who_goes(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    event_id = user_data[con.CURRENT_EVENT_ID]
    who_goes_str = ''
    from_find_cb = ''
    from_find_events = re.search(pattern=con.ADD_USER, string=query.data)
    if from_find_events:
        from_find_cb = f"_{con.ADD_USER}"

    search = re.search(pattern=f"{con.WHO_GOES}_\d+", string=query.data)
    if search:
        status_int = int(re.search(pattern="\d+", string=search.group()).group())
        session = Session()
        party_data = session.query(Party).join(User, User.id==Party.user_id).filter(
            and_(Party.event_id == event_id, Event.deleted == False, Event.id == event_id, Party.status == status_int)).order_by(User.nickname).all()
        if party_data:
            for party in party_data:
                who_goes_str = who_goes_str + get_full_user_name(party.user.first_name, party.user.second_name, party.user.nickname) + '\n'
    if query.message.caption:
        query.delete_message()
        update = query.message.reply_text
    else:
        update = query.message.edit_text
    keyboard = [
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=f"{con.SELECT_EVENT}_{event_id}{from_find_cb}")],
    ]
    send_text_and_keyboard(
        update=update,
        keyboard=keyboard,
        message_text=who_goes_str if who_goes_str != '' else "Отметок не поставлено"
    )
    return con.CALENDAR


def get_user_to_find_events(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    user_data[con.CALLBACK_QUERY] = query
    user_id = user_data[con.LOGGED_USER_ID]
    keyboard = [
        [InlineKeyboardButton(f"{emoji.PERS_SURFING} Мои события", callback_data=f"{con.FIND_EVENTS}_{user_id}")],
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.START_OVER)],
    ]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text="Поиск событий по участнику:\n"
                     "перешлите боту любое личное сообщение пользователя или "
                     "отправьте сообщением имя пользователя (начинается с символа @)",
    )
    return con.FIND_EVENTS


def find_events_select_status(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    logged_user_id = user_data[con.LOGGED_USER_ID]
    if update.message:
        _cb = user_data[con.CALLBACK_QUERY]
        update.message.delete()
        forward_from_user = update.message.forward_from
        if forward_from_user:
            user_id = forward_from_user.id
        else:
            username = get_username_from_text(update.message.text)
            session = Session()
            user = session.query(User).filter_by(nickname=username).one_or_none()
            if user:
                user_id = user.unique_id
            else:
                keyboard = [[InlineKeyboardButton("Ок", callback_data=con.MANAGE_USERS)]]
                message_text = f"Пользователь с таким именем не найден в списке пользователей бота"
                send_text_and_keyboard(
                    update=_cb.message.edit_text,
                    keyboard=keyboard,
                    message_text=message_text
                )
                return con.FIND_EVENTS
    else:
        _cb = update.callback_query
        _cb.answer()
        search = re.search(pattern=f"{con.FIND_EVENTS}_\d+", string=_cb.data)
        user_id = 0
        if search:
            user_id = int(re.search(pattern="\d+", string=search.group()).group())
    if user_id != 0:
        session = Session()
        user = session.query(User).filter_by(unique_id=user_id).one_or_none()
        status_numbers = update_numbers_who_goes(user_id=user_id)
    else:
        user = None
        status_numbers = [0, 0]
    keyboard = [
        [InlineKeyboardButton(f"Точно {'пойду' if user_id == logged_user_id else 'пойдет'} ({status_numbers[0]})", callback_data=f"{con.EVENTS_USER}_{con.DEF_GO}{con.ADD_USER}_{user_id}")],
        [InlineKeyboardButton(f"Возможно {'пойду' if user_id == logged_user_id else 'пойдет'} ({status_numbers[1]})", callback_data=f"{con.EVENTS_USER}_{con.PROB_GO}{con.ADD_USER}_{user_id}")],
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.MANAGE_USERS)],
        [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)]
    ]
    send_text_and_keyboard(
        update=_cb.message.edit_text,
        keyboard=keyboard,
        message_text=f"Поиск событий по участнику {get_full_user_name(user.first_name, user.second_name, user.nickname)}:\nвыберите отметку"
    )
    return con.FIND_EVENTS


def find_events(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data[con.CALLBACK_QUERY] = query

    search = re.search(pattern=f"{con.EVENTS_USER}_\d+", string=query.data)
    status_int = 0
    if search:
        status_int = int(re.search(pattern="\d+", string=search.group()).group())
    search = re.search(pattern=f"{con.ADD_USER}_\d+", string=query.data)
    user_id = 0
    if search:
        user_id = int(re.search(pattern="\d+", string=search.group()).group())
    session = Session()
    user = session.query(User).filter_by(unique_id=user_id).one_or_none()
    event_data = session.query(Event).filter(
            and_(Party.event_id == Event.id, Event.deleted == False,
                 Party.status == status_int, Party.user_id == User.id,
                 User.unique_id == user_id)).order_by(Event.event_date_start).order_by(Event.event_date_start).all()
    keyboard_nav = [
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=f"{con.FIND_EVENTS}_{user_id}")],
        [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)]
    ]
    update_func = query.message.edit_text
    if query.message.caption:
        query.delete_message()
        update_func = query.message.reply_text
    if event_data:
        keyboard_list = []
        for event in event_data:
            _date_str_for_button = '{:02d}'.format(event.event_date_start.month) + '.' + '{:02d}'.format(event.event_date_start.year - 2000)
            keyboard_list.append(
                [InlineKeyboardButton(
                    f"{_date_str_for_button}, {event.event_name} {emoji.PIN}{event.event_city}, {event.event_country}",
                    callback_data=f"{con.SELECT_EVENT}_{event.id}_{con.ADD_USER}")]
            )
        send_text_and_keyboard(
            update=update_func,
            keyboard=keyboard_list + keyboard_nav,
            message_text=f"Cписок событий пользователя {get_full_user_name(user.first_name, user.second_name, user.nickname)} c отметкой {con.STATUS_TEXT[status_int]}",
        )
    else:
        send_text_and_keyboard(
            update=update_func,
            keyboard=keyboard_nav,
            message_text=f"Отметок не найдено",
        )
    return con.FIND_EVENTS


def check_in_event(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    event_id = user_data[con.CURRENT_EVENT_ID]
    user_id = user_data[con.LOGGED_USER_ID]
    search = re.search(pattern=f"{con.CHECK_IN}_\d+", string=query.data)
    if search:
        status_int = int(re.search(pattern="\d+", string=search.group()).group())
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
    if re.match(pattern=f"^{con.GO_BACK}.*$", string=query.data) is not None:
        date_list = list(user_data[con.DATE_COUNTER].keys())
        event_date_int = int(re.search(pattern="\d{6}", string=query.data).group())
        y_from_data, m_from_data = event_date_int // 100, event_date_int - (event_date_int // 100) * 100
        start = (date_list.index(datetime.date(y_from_data, m_from_data, 1))) // con.NUM_EVENTS_ON_PAGE
        start = start * con.NUM_EVENTS_ON_PAGE
        stop = start + con.NUM_EVENTS_ON_PAGE
    if start + con.NUM_EVENTS_ON_PAGE < len(user_data[con.DATE_COUNTER]):
        button_forward = [InlineKeyboardButton(f"{emoji.FAST_FORWARD} Вперед", callback_data=con.FORWARD_LIST)]
    if start - con.NUM_EVENTS_ON_PAGE >= 0:
        button_back = [InlineKeyboardButton(f"{emoji.FAST_REVERSE} Назад", callback_data=con.BACK_LIST)]
    user_data[con.START_PAGE] = start
    user_data[con.END_PAGE] = stop
    button_list = button_back + button_forward
    keyboard = [
        button_list,
        [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)]
    ]
    return keyboard


def update_checkbox_party(context) -> int:
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


def update_numbers_who_goes(event_id=None, user_id=None):
    numbers_list = [0, 0]
    session = Session()
    if user_id is None:
        party_data = session.query(Party).filter(
            and_(Party.event_id == event_id, Event.deleted == False,
                 Event.id == event_id, or_(Party.status == 1, Party.status == 2))).all()
    else:
        party_data = session.query(Party).filter(
            and_(Event.deleted == False, or_(Party.status == 1, Party.status == 2),
                 Party.user_id == User.id, User.unique_id == user_id, Party.event_id == Event.id)).all()
    if party_data:
        for party in party_data:
            if party.status == 1:
                numbers_list[0] = numbers_list[0] + 1
            else:
                numbers_list[1] = numbers_list[1] + 1
    return numbers_list