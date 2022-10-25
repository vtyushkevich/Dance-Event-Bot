import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import const as con
from config import BASIC_ADMIN_ID
from core.view import send_text_and_keyboard, set_default_userdata, generate_text_event, set_keyboard
from main_models import Session, User, Base

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    """Send a message on `/start`."""
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    Base.metadata.create_all(checkfirst=True)
    session = Session()
    user_data = session.query(User).filter_by(unique_id=BASIC_ADMIN_ID).one_or_none()
    if not user_data:
        new_user = User(
            unique_id=BASIC_ADMIN_ID,
            first_name="",
            second_name="",
            nickname="",
            access_level=1,
            deleted=False,
            created_at=datetime.today()
        )
        session.add(new_user)
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

