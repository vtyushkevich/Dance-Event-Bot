import datetime
from pathlib import Path

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext
from telegram_bot_calendar import DetailedTelegramCalendar

import const as con
import emoji
from core.view import send_text_and_keyboard, set_keyboard, generate_text_event, update_date_id_dict, get_query_and_data
from events.validators import validate_user_data
from main_models import Event, Session


def creating_event(update: Update, context: CallbackContext) -> int:
    message = update.callback_query.message
    if message.caption:
        message.delete()
    send_text_and_keyboard(
        update=message.reply_text if message.caption else message.edit_text,
        keyboard=set_keyboard(context, con.CREATE_EVENT),
        message_text=con.TEXT_REQUEST[con.CREATE_EVENT],
    )
    return con.CREATE_EVENT


def get_property_to_edit(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    user_data[con.PROPERTY_TO_EDIT] = query.data
    user_data[con.CALLBACK_QUERY] = query
    send_text_and_keyboard(
        update=query.edit_message_text,
        keyboard=[[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.GO_BACK)]],
        message_text=con.TEXT_REQUEST[query.data],
    )
    return con.CREATE_PHOTO if query.data == con.EDIT_PHOTO else con.CREATE_PROPERTY


def set_property_value(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data

    _cb = user_data[con.CALLBACK_QUERY]
    _cb.message.delete() if _cb is not None else None
    input_from_user = update.message.text
    category = user_data[con.PROPERTY_TO_EDIT]
    _validation_passed, _validation_comment = validate_user_data(category, input_from_user)
    if _validation_passed:
        user_data[category] = input_from_user
        del user_data[con.PROPERTY_TO_EDIT]
        send_text_and_keyboard(
            update=update.message.reply_text,
            keyboard=set_keyboard(context, con.CREATE_EVENT),
            message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
        )
        return con.CREATE_EVENT
    else:
        user_data[con.CALLBACK_QUERY] = None
        send_text_and_keyboard(
            update=update.message.reply_text,
            keyboard=[[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.GO_BACK)]],
            message_text=_validation_comment
        )
        return con.CREATE_PROPERTY


def get_date_to_edit(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    user_data[con.PROPERTY_TO_EDIT] = query.data
    calendar, step = DetailedTelegramCalendar(
        calendar_id=1,
        additional_buttons=[{"text": f"{emoji.LEFT_ARROW} Назад", 'callback_data': con.GO_BACK}],
        locale='ru',
    ).build()
    send_text_and_keyboard(
        update=query.edit_message_text,
        keyboard=calendar,
        message_text=con.TEXT_REQUEST[query.data]
    )
    return con.CREATE_DATE


def set_date_value(update: Update, context: CallbackContext):
    query, user_data = get_query_and_data(update, context)

    result, key, step = DetailedTelegramCalendar(
        calendar_id=1,
        additional_buttons=[{"text": f"{emoji.LEFT_ARROW} Назад", 'callback_data': con.GO_BACK}],
        locale='ru',
    ).process(query.data)
    if not result and key:
        send_text_and_keyboard(
            update=query.edit_message_text,
            keyboard=key,
            message_text=con.TEXT_REQUEST[context.user_data[con.PROPERTY_TO_EDIT]],
        )
        return con.CREATE_DATE
    elif result:
        category = user_data[con.PROPERTY_TO_EDIT]
        user_data[f"{category}_DT"] = result
        _validation_passed, _validation_comment = validate_user_data(f"{category}_DT", checked_date=result)
        if _validation_passed:
            _validation_passed, _validation_comment = validate_user_data(
                f"{category}_DT",
                checked_date=user_data[con.EDIT_DATE_START_DT],
                checked_sec_date=user_data[con.EDIT_DATE_END_DT]
            )
        if _validation_passed:
            _datetype = {con.EDIT_DATE_START: 'Дата начала ', con.EDIT_DATE_END: 'Дата окончания '}
            user_data[category] = f"{_datetype[category]} {result.day} {con.RU_MONTH.get(result.month)} " \
                                  f"{result.year} г."
            del user_data[con.PROPERTY_TO_EDIT]
            send_text_and_keyboard(
                update=query.edit_message_text,
                keyboard=set_keyboard(context, con.CREATE_EVENT),
                message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
            )
            return con.CREATE_EVENT
        else:
            user_data[f"{category}_DT"] = None
            send_text_and_keyboard(
                update=query.edit_message_text,
                keyboard=[[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=category)]],
                message_text=_validation_comment
            )
            return con.CREATE_DATE


def set_photo(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    _cb = context.user_data[con.CALLBACK_QUERY]
    _cb.message.delete() if _cb is not None else None
    category = user_data[con.PROPERTY_TO_EDIT]
    photo_file = update.message.photo[-1]
    user_data[category] = photo_file.file_id
    del user_data[con.PROPERTY_TO_EDIT]
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard=set_keyboard(context, con.CREATE_EVENT),
        message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
    )
    return con.CREATE_EVENT


def set_doc(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    _cb = context.user_data[con.CALLBACK_QUERY]
    _cb.message.delete() if _cb is not None else None
    category = user_data[con.PROPERTY_TO_EDIT]
    doc_file = update.message.document
    _validation_passed, _validation_comment = None, None
    _validation_mime_passed, _validation_mime_comment = validate_user_data(category, mimetype=doc_file.mime_type)
    if _validation_mime_passed:
        photo_file = doc_file.get_file()
        photo_file.download(custom_path=f"{con.PATH_TO_PICS}{photo_file.file_unique_id}")
        _validation_passed, _validation_comment = validate_user_data(category, userdata=photo_file.file_size)
        if _validation_passed:
            user_data[category] = Path.cwd() / con.PATH_TO_PICS / photo_file.file_unique_id
            del user_data[con.PROPERTY_TO_EDIT]
            _msg = update.message.reply_photo(
                photo=open(user_data[category], 'rb'),
            )
            user_data[category] = _msg.photo[-1].file_id
            send_text_and_keyboard(
                update=update.message.reply_text,
                keyboard=set_keyboard(context, con.CREATE_EVENT),
                message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
            )
            return con.CREATE_EVENT
    context.user_data[con.CALLBACK_QUERY] = None
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard=[[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.GO_BACK)]],
        message_text=(_validation_comment if _validation_comment else _validation_mime_comment)
    )
    return con.CREATE_PHOTO


def show_edit_preview(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    _validation_passed, _validation_comment = validate_user_data(con.PUBLISH_EVENT, userdata=context)
    if _validation_passed:
        keyboard = [
            [InlineKeyboardButton("Опубликовать", callback_data=con.PUBLISH_EVENT)],
            [InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.GO_BACK)],
        ]
    else:
        keyboard = [[InlineKeyboardButton(f"{emoji.LEFT_ARROW} Назад", callback_data=con.GO_BACK)]]
    _text = generate_text_event(user_data[con.EDIT_NAME], user_data[con.EDIT_CITY], user_data[con.EDIT_COUNTRY],
                                user_data[con.EDIT_DATE_START], user_data[con.EDIT_DATE_END], user_data[con.EDIT_DESC])
    if user_data[con.EDIT_PHOTO]:
        query.message.delete()
    send_text_and_keyboard(
        update=query.message.reply_photo if user_data[con.EDIT_PHOTO] else query.edit_message_text,
        keyboard=keyboard,
        message_text=_text,
        photo=user_data[con.EDIT_PHOTO] if user_data[con.EDIT_PHOTO] else None
    )
    return con.CREATE_EVENT


def publish_event(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    session = Session()
    if user_data[con.CURRENT_EVENT_ID] is None:
        event = Event(
            event_name=user_data[con.EDIT_NAME],
            event_city=user_data[con.EDIT_CITY],
            event_country=user_data[con.EDIT_COUNTRY],
            event_desc=user_data[con.EDIT_DESC],
            event_date_start=user_data[con.EDIT_DATE_START_DT],
            event_date_end=user_data[con.EDIT_DATE_END_DT],
            event_photo=user_data[con.EDIT_PHOTO],
            created_by=1,
            created_at=datetime.datetime.today()
        )
        session.add(event)
        _cb = con.START_OVER
    else:
        event_id_int = user_data[con.CURRENT_EVENT_ID]
        event_data = session.query(Event).filter_by(id=event_id_int).one_or_none()
        if event_data:
            session.query(Event).filter_by(id=event_id_int).update(
                {'event_name': user_data[con.EDIT_NAME],
                 'event_city': user_data[con.EDIT_CITY],
                 'event_country': user_data[con.EDIT_COUNTRY],
                 'event_desc': user_data[con.EDIT_DESC],
                 'event_date_start': user_data[con.EDIT_DATE_START_DT],
                 'event_date_end': user_data[con.EDIT_DATE_END_DT],
                 "event_photo": user_data[con.EDIT_PHOTO], }
            )
        _cb = con.SELECT_EVENT + '_' + str(event_id_int)
    session.commit()
    query.message.delete()
    send_text_and_keyboard(
        update=query.message.reply_text,
        keyboard=[[InlineKeyboardButton("Ок", callback_data=_cb)]],
        message_text=f"{emoji.RED_EXCLAMATION_SIGN} Событие опубликовано!"
    )
    user_data[con.DATE_COUNTER] = update_date_id_dict()
    if user_data[con.CURRENT_EVENT_ID] is None:
        return con.CREATE_EVENT
    else:
        return con.CALENDAR