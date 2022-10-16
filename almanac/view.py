from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

import const as con
from core.view import set_keyboard


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