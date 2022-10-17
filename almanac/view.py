from time import strftime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar

import const as con
from core.view import set_keyboard, send_text_and_keyboard


def show_event_calendar(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    _text = context.user_data['FAKE_TEXT']
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
        keyboard = [[InlineKeyboardButton("Ок", callback_data=con.GO_BACK)]]
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
    keyboard = [[InlineKeyboardButton("Ок", callback_data=con.GO_BACK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(
        text="Событие удалено!",
        reply_markup=reply_markup
    )
    return con.CALENDAR


def show_select_1(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    keyboard = list()
    for n in range(10):
        keyboard.append([InlineKeyboardButton("Сентябрь '22 " + str(n), callback_data=con.SELECT_ALM + '_' + str(2022*100+9))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(
        text="Нет активных событий",
        reply_markup=reply_markup
        )
    return con.CALENDAR


def show_select_2(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    calendar, step = DetailedTelegramCalendar(
        calendar_id=1,
        additional_buttons=[{"text": "\U00002B05 Назад", 'callback_data': con.GO_BACK}], ).build()
    send_text_and_keyboard(
        update=query.edit_message_text,
        keyboard=calendar,
        message_text=query.data
    )
    return con.CALENDAR


# strftime