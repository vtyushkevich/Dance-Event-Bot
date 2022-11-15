import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import const as con
import emoji
from config import BASIC_ADMIN_ID
from core.view import send_text_and_keyboard, set_default_userdata, set_keyboard, get_query_and_data
from main_models import Session, User, Base

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
    # filename="main_view_logger.log"
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    query, user_data = get_query_and_data(update, context)

    user_data[con.LOGGED_USER_ID] = update.message.from_user.id
    session = Session()
    try:
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
        message_text = ""
        user_info = session.query(User).filter_by(unique_id=update.message.from_user.id).one_or_none()
        if user_info:
            if user_info.access_level <= con.ADMIN_AL:
                message_text = f"\nВы - администратор проекта {emoji.CROWN}"
        send_text_and_keyboard(
            update=update.message.reply_text,
            keyboard=set_keyboard(context, con.START),
            message_text=f"{emoji.DANCING_WOMAN} Я бот для отслеживания танцевальных событий и расскажу, "
                         f"что происходит в мире танцев {emoji.FIRE}{message_text}"
        )
        set_default_userdata(context)
        session.close()
    except Exception as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        send_text_and_keyboard(
            update=update.message.reply_text,
            keyboard=[],
            message_text=f"Ошибка\n"
                         f"{e.__class__.__name__}: {e}"
        )
        session.rollback()
    return con.TOP_LEVEL


def start_over(update: Update, context: CallbackContext) -> int:
    query, user_data = get_query_and_data(update, context)

    session = Session()
    message_text = ""
    try:
        user_info = session.query(User).filter_by(unique_id=user_data[con.LOGGED_USER_ID]).one_or_none()
        if user_info:
            if user_info.access_level <= con.ADMIN_AL:
                message_text = f"\nВы - администратор проекта {emoji.CROWN}"
        if query.message.caption:
            query.delete_message()
        send_text_and_keyboard(
            update=query.message.reply_text if query.message.caption else query.edit_message_text,
            keyboard=set_keyboard(context, con.START),
            message_text=f"{message_text}\n{emoji.GOLF} Что делаем дальше?",
        )
        set_default_userdata(context)
        session.close()
    except Exception as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        send_text_and_keyboard(
            update=update.message.reply_text,
            keyboard=[],
            message_text=f"Ошибка\n"
                         f"{e.__class__.__name__}: {e}"
        )
        session.rollback()
    return con.TOP_LEVEL


def cancel(update: Update, context: CallbackContext) -> int:
    logger.info("User %s canceled the conversation.", update.message.from_user.first_name)
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard='',
        message_text="До встречи!",
    )
    return ConversationHandler.END


def startup_deploy():
    logger.info("Started the bot",)
    session = Session()
    try:
        Base.metadata.create_all(checkfirst=True)
        user_info = session.query(User).filter_by(unique_id=BASIC_ADMIN_ID).one_or_none()
        if not user_info:
            new_user = User(
                unique_id=BASIC_ADMIN_ID,
                first_name=None,
                second_name=None,
                nickname="Базовый администратор бота",
                access_level=con.SUPER_ADMIN_AL,
                deleted=False,
                created_at=datetime.today()
            )
            session.add(new_user)
        else:
            user_info.deleted = False
            user_info.access_level = con.SUPER_ADMIN_AL
        session.close()
    except Exception as e:
        logger.error(f"{e.__class__.__name__}: {e}")
        session.rollback()
    session.commit()