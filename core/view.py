import re
from datetime import date

from sqlalchemy import and_
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import const as con
import emoji
from main_models import Session, Event, User


def set_default_userdata(context: CallbackContext, event_data=None):
    if event_data is None:
        context.user_data[con.EDIT_NAME] = ""
        context.user_data[con.EDIT_CITY] = ""
        context.user_data[con.EDIT_COUNTRY] = ""
        context.user_data[con.EDIT_DESC] = ""
        context.user_data[con.EDIT_DATE_START] = "Дата начала"
        context.user_data[con.EDIT_DATE_END] = "Дата окончания"
        context.user_data[con.EDIT_DATE_START_DT] = None
        context.user_data[con.EDIT_DATE_END_DT] = None
        context.user_data[con.EDIT_PHOTO] = ""
        context.user_data[con.PROPERTY_TO_EDIT] = None
        context.user_data[con.CALLBACK_QUERY] = None
        context.user_data[con.CURRENT_EVENT_ID] = None
        context.user_data[con.START_PAGE] = 0
        context.user_data[con.END_PAGE] = con.NUM_EVENTS_ON_PAGE
    else:
        context.user_data[con.EDIT_NAME] = event_data.event_name
        context.user_data[con.EDIT_CITY] = event_data.event_city
        context.user_data[con.EDIT_COUNTRY] = event_data.event_country
        context.user_data[con.EDIT_DESC] = event_data.event_desc
        context.user_data[con.EDIT_DATE_START] = f"Дата начала {event_data.event_date_start.day} {con.RU_MONTH.get(event_data.event_date_start.month)} {event_data.event_date_start.year} г."
        context.user_data[con.EDIT_DATE_END] = f"Дата окончания {event_data.event_date_end.day} {con.RU_MONTH.get(event_data.event_date_end.month)} {event_data.event_date_end.year} г."
        context.user_data[con.EDIT_DATE_START_DT] = date(event_data.event_date_start.year, event_data.event_date_start.month, event_data.event_date_start.day)
        context.user_data[con.EDIT_DATE_END_DT] = date(event_data.event_date_end.year, event_data.event_date_end.month, event_data.event_date_end.day)
        context.user_data[con.EDIT_PHOTO] = event_data.event_photo


def set_keyboard(context: CallbackContext, stage: str):
    user_data = context.user_data
    keyboard = []
    if stage == con.START:
        keyboard.append([InlineKeyboardButton(f"{emoji.CALENDAR}   Календарь событий", callback_data=con.CALENDAR)])
        keyboard.append([InlineKeyboardButton(f"{emoji.PLANE}   События участника", callback_data=con.FIND_EVENTS)])
        if user_access(context) <= con.ADMIN_AL:
            keyboard.append([InlineKeyboardButton(f"{emoji.DANCE_BALL}   Создать событие", callback_data=con.MANAGEMENT)])
            keyboard.append([InlineKeyboardButton("Управление пользователями", callback_data=con.MANAGE_USERS)])
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
            [InlineKeyboardButton(f"{emoji.DANCING_MAN} Предварительный просмотр", callback_data=con.EDIT_PREVIEW)],
            [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.START_OVER if user_data[con.CURRENT_EVENT_ID] is None else f"{con.SELECT_EVENT}_{user_data[con.CURRENT_EVENT_ID]}")],
        ]
    if stage == con.MANAGE_USERS:
        keyboard = [
            [InlineKeyboardButton("Список администраторов", callback_data=con.ADMINS_LIST)],
            [InlineKeyboardButton("Добавить администратора", callback_data=con.ADD_USER)],
            [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)],
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
    _text = f"{emoji.COUPLE} {event_name}\n\n"
    _text = _text + f"{emoji.PIN} {'' if event_city == '' else f'{event_city}, '}"
    _text = _text + f"{'' if event_country == '' else event_country}\n\n"
    _text = _text + f"{emoji.ROCKET} {'Дата начала не указана ' if event_date_start == 'Дата начала' else event_date_start}\n\n"
    _text = _text + f"{emoji.RACING_FLAG} {'Дата окончания не указана' if event_date_end == 'Дата окончания' else event_date_end}\n\n"
    _text = _text + ('' if event_desc == '' else 'О событии:\n' + event_desc)
    return _text


def check_symbol(checked: bool):
    if checked:
        return f"{emoji.GREEN_CHECK}"
    else:
        return f"{emoji.GREY_CHECK}"


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
    future_events = session.query(Event).filter(and_(Event.event_date_start >= date.today(), Event.deleted == False)).order_by(
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


def update_admins_list() -> dict:
    session = Session()
    admins = session.query(User).filter(
        and_(User.access_level <= con.ADMIN_AL, User.deleted == False)).order_by(
        User.created_at)
    session.commit()
    admins_list = []
    for admin in admins:
        admins_list.append(admin)
    return admins_list


def get_full_user_name(first_name, second_name, nickname) -> str:
    first_name = "" if first_name is None else first_name
    second_name = "" if second_name is None else second_name
    nickname = "" if nickname is None else '@' + nickname
    return ('%s %s %s' % (str(first_name), str(second_name), str(nickname))).strip()


def get_id_from_callback_data(query_data: str) -> int:
    id_str = str(re.search(pattern='_id[0-9]*', string=query_data).group())
    id_int = int(re.search(pattern='[0-9]+', string=id_str).group())
    return id_int


def get_username_from_text(some_text: str) -> str:
    search_result = re.search(pattern='@[a-zA-Z]{1}[\d\w]{4,31}', string=some_text)
    if search_result:
        nickname = search_result.group()
        nickname = re.search(pattern='[a-zA-Z]{1}[\d\w]{4,31}', string=nickname).group()
    else:
        nickname = next(m.group() for m in re.finditer(r'\w+', some_text))
    return nickname


def user_access(context: CallbackContext) -> int:
    session = Session()
    user_id = context.user_data[con.LOGGED_USER_ID]
    user = session.query(User).filter_by(unique_id=user_id).one_or_none()
    session.commit()
    if user:
        return user.access_level
    else:
        return con.USER_AL