from datetime import datetime

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext

import const as con
import emoji
from config import BASIC_ADMIN_ID
from core.view import send_text_and_keyboard, set_keyboard, update_admins_list, get_full_user_name, \
    get_id_from_callback_data, get_username_from_text, get_query_and_data
from main_models import Session, User


def manage_users(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    message = query.message
    send_text_and_keyboard(
        update=message.edit_text,
        keyboard=set_keyboard(context, con.MANAGE_USERS),
        message_text=con.TEXT_REQUEST[con.MANAGE_USERS],
    )
    return con.MANAGE_USERS


def show_admins_list(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    message = query.message
    admins_list = update_admins_list()
    keyboard_list = []
    message_text = ""
    for admin in admins_list:
        if user_data[con.LOGGED_USER_ID] != admin.unique_id:
            keyboard_list.append(
                [InlineKeyboardButton(get_full_user_name(admin.first_name, admin.second_name, admin.nickname),
                                      callback_data=con.ADMINS_LIST + '_id' + str(admin.unique_id))],
            )
        else:
            message_text = get_full_user_name(admin.first_name, admin.second_name, admin.nickname)
    keyboard_nav = [
        [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.MANAGE_USERS)],
        [InlineKeyboardButton(f"{emoji.GOLF} В основное меню", callback_data=con.START_OVER)]
    ]
    send_text_and_keyboard(
        update=message.edit_text,
        keyboard=keyboard_list + keyboard_nav,
        message_text=f"Список администраторов:\n{message_text} (это вы)",
    )
    return con.MANAGE_USERS


def delete_admin_confirm(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    admin_id = get_id_from_callback_data(query.data)
    session = Session()
    admin = session.query(User).filter_by(unique_id=admin_id).one_or_none()
    session.commit()
    keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=f"{con.DELETE_USER_CONFIRMED}_id{admin_id}")],
        [InlineKeyboardButton("Назад", callback_data=con.ADMINS_LIST)],
    ]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text=f"Вы уверены, что хотите удалить пользователя {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} из списка администраторов?",
    )
    return con.MANAGE_USERS


def delete_admin(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    admin_id = get_id_from_callback_data(query.data)
    session = Session()
    admin = session.query(User).filter_by(unique_id=admin_id).one_or_none()
    session.commit()
    if admin:
        if admin.unique_id != BASIC_ADMIN_ID:
            admin.access_level = con.USER_AL
            session.commit()
            message_text = f"Пользователь {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} удален из списка администраторов"
        else:
            message_text = "Базовый администратор не может быть удален из списка администраторов"
    else:
        message_text = "Пользователь не найден в списке администраторов"
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.ADMINS_LIST)]]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text=message_text
    )
    return con.MANAGE_USERS


def add_admin_confirm(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    user_data[con.CALLBACK_QUERY] = query
    keyboard = [[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.MANAGE_USERS)]]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text="Перешлите боту любое личное сообщение пользователя, которого планируете добавить в список "
                     "администраторов, или отправьте сообщением имя пользователя (начинается с символа @)",
    )
    return con.MANAGE_USERS


def add_admin(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    _cb = user_data[con.CALLBACK_QUERY]
    session = Session()
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.ADMINS_LIST)]]

    update.message.delete()
    forward_from_user = update.message.forward_from
    if forward_from_user:
        admin = session.query(User).filter_by(unique_id=forward_from_user.id).one_or_none()
        if admin is None:
            new_admin = User(
                unique_id=forward_from_user.id,
                first_name=forward_from_user.first_name,
                second_name=forward_from_user.last_name,
                nickname=forward_from_user.username,
                access_level=con.ADMIN_AL,
                deleted=False,
                created_at=datetime.today()
            )
            session.add(new_admin)
        else:
            admin.first_name = forward_from_user.first_name
            admin.second_name = forward_from_user.last_name
            admin.nickname = forward_from_user.username
            admin.access_level = con.ADMIN_AL
            admin.deleted = False
        session.commit()
        send_text_and_keyboard(
            update=_cb.message.edit_text,
            keyboard=keyboard,
            message_text=f"Пользователь {get_full_user_name(forward_from_user.first_name, forward_from_user.last_name, forward_from_user.username)} добавлен в список администраторов",
        )
    else:
        username = get_username_from_text(update.message.text)
        admin = session.query(User).filter_by(nickname=username).one_or_none()
        if admin:
            admin.access_level = con.ADMIN_AL
            admin.deleted = False
            admin = session.query(User).filter_by(nickname=username).one_or_none()
            session.commit()
            message_text = f"Пользователь {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} добавлен в список администраторов"
        else:
            keyboard = [[InlineKeyboardButton("Ок", callback_data=con.ADD_USER)]]
            message_text = "Пользователь с таким именем не найден в списке пользователей бота"
        send_text_and_keyboard(
            update=_cb.message.edit_text,
            keyboard=keyboard,
            message_text=message_text,
        )
    return con.MANAGE_USERS