import re
from datetime import date

from sqlalchemy import and_
from telegram import Update, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

import const as con
from core.view import send_text_and_keyboard, set_keyboard, update_admins_list, get_full_user_name, \
    get_id_from_callback_data
from main_models import Session, Event, User


def manage_users(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    message = update.callback_query.message
    user_data = context.user_data
    send_text_and_keyboard(
        update=message.edit_text,
        keyboard=set_keyboard(context, con.MANAGE_USERS),
        message_text=con.TEXT_REQUEST[con.MANAGE_USERS],
    )
    return con.MANAGE_USERS


def show_admins_list(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    message = update.callback_query.message
    user_data = context.user_data
    admins_list = update_admins_list()
    keyboard_list = []
    for admin in admins_list:
        keyboard_list.append(
            [InlineKeyboardButton(get_full_user_name(admin.first_name, admin.second_name, admin.nickname),
                                  callback_data=con.ADMINS_LIST + '_id' + str(admin.unique_id))],
        )
    keyboard_nav = [
        [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.MANAGE_USERS)],
        [InlineKeyboardButton("\U000026F3 В основное меню", callback_data=con.START_OVER)]
    ]
    send_text_and_keyboard(
        update=message.edit_text,
        keyboard=keyboard_list + keyboard_nav,
        message_text="Список администраторов",
    )
    return con.MANAGE_USERS


def delete_admin_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    admin_id = get_id_from_callback_data(query.data)
    session = Session()
    admin = session.query(User).filter_by(unique_id=admin_id).one_or_none()
    session.commit()
    keyboard = [
        [InlineKeyboardButton("Удалить", callback_data=con.DELETE_USER_CONFIRMED + '_id' + str(admin_id))],
        [InlineKeyboardButton("Назад", callback_data=con.ADMINS_LIST)],
    ]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text=f"Вы уверены, что хотите удалить пользователя {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} из списка администраторов?",
    )
    return con.MANAGE_USERS


def delete_admin(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_data = context.user_data

    admin_id = get_id_from_callback_data(query.data)
    session = Session()
    admin = session.query(User).filter_by(unique_id=admin_id).one_or_none()
    session.commit()
    if admin:
        admin.access_level = 100
        session.commit()
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.ADMINS_LIST)]]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text=f"Пользователь {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} удален из списка администраторов",
    )
    return con.MANAGE_USERS


def add_admin_confirm(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data[con.CALLBACK_QUERY] = query
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data=con.MANAGE_USERS)],
    ]
    send_text_and_keyboard(
        update=query.message.edit_text,
        keyboard=keyboard,
        message_text="Отправьте контакт пользователя, которого планируете добавить в список администраторов",
    )
    # reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    # query.message.reply_text(
    #     text='Отправьте контакт пользователя, которого планируете сделать администратором',
    #     reply_markup=reply_markup
    # )
    return con.MANAGE_USERS


def add_admin(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # query.answer()
    user_data = context.user_data
    _cb = context.user_data[con.CALLBACK_QUERY]

    admin_id = update.message.contact.user_id
    update.message.delete()
    session = Session()
    admin = session.query(User).filter_by(unique_id=admin_id).one_or_none()
    session.commit()
    if admin:
        admin.access_level = 1
        session.commit()
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.ADMINS_LIST)]]
    send_text_and_keyboard(
        update=_cb.message.edit_text,
        keyboard=keyboard,
        message_text=f"Пользователь {get_full_user_name(admin.first_name, admin.second_name, admin.nickname)} добавлен в список администраторов",
    )
    return con.MANAGE_USERS