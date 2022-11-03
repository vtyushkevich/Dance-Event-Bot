import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import const as con
from config import BASIC_ADMIN_ID
from core.view import send_text_and_keyboard, set_default_userdata, set_keyboard
from main_models import Session, User, Base

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    user_data = context.user_data
    user_data[con.LOGGED_USER_ID] = update.message.from_user.id

    session = Session()
    user_info = session.query(User).filter_by(unique_id=update.message.from_user.id).one_or_none()
    if not user_info:
        new_user = User(
            unique_id=update.message.from_user.id,
            first_name=update.message.from_user.first_name,
            second_name=update.message.from_user.last_name,
            nickname=update.message.from_user.username,
            access_level=con.USER_AL,
            deleted=False,
            created_at=datetime.today()
        )
        session.add(new_user)
    else:
        user_info.first_name = update.message.from_user.first_name
        user_info.second_name = update.message.from_user.last_name
        user_info.nickname = update.message.from_user.username
        user_info.deleted = False
    session.commit()
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard=set_keyboard(context, con.START),
        message_text="\U0001F483 Я бот для отслеживания танцевальных событий и расскажу, что происходит в мире танцев "
                     "\U0001F525",
    )
    set_default_userdata(context)
    return con.TOP_LEVEL


def start_over(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.message.caption:
        query.delete_message()
    send_text_and_keyboard(
        update=query.message.reply_text if query.message.caption else query.edit_message_text,
        keyboard=set_keyboard(context, con.START),
        message_text="\U000026F3 Что делаем дальше?",
    )
    set_default_userdata(context)
    return con.TOP_LEVEL


def cancel(update: Update, context: CallbackContext) -> int:
    logger.info("User %s canceled the conversation.", update.message.from_user.first_name)
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard='',
        message_text='До встречи!',
    )
    return ConversationHandler.END


def startup_deploy():
    logger.info("Started the bot",)
    Base.metadata.create_all(checkfirst=True)
    session = Session()
    user_info = session.query(User).filter_by(unique_id=BASIC_ADMIN_ID).one_or_none()
    if not user_info:
        new_user = User(
            unique_id=BASIC_ADMIN_ID,
            first_name=None,
            second_name=None,
            nickname='Базовый администратор бота',
            access_level=con.SUPER_ADMIN_AL,
            deleted=False,
            created_at=datetime.today()
        )
        session.add(new_user)
    else:
        user_info.deleted = False
        user_info.access_level = con.SUPER_ADMIN_AL
    session.commit()