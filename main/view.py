import logging

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

import const as con
from core.view import send_text_and_keyboard, set_default_userdata, generate_text_event, set_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> int:
    """Send a message on `/start`."""
    logger.info("User %s started the conversation.", update.message.from_user.first_name)
    send_text_and_keyboard(
        update=update.message.reply_text,
        keyboard=set_keyboard(context, con.START),
        message_text="\U0001F483 Я бот для отслеживания танцевальных событий и расскажу, что происходит в мире танцев "
                     "\U0001F525",
    )
    set_default_userdata(context)
    context.user_data['FAKE_TEXT'] = generate_text_event(event_name='FESTIVALITO LA VIDA, MÚSICA Y TANGO 2022',
                                                         event_city='Челябинск',
                                                         event_country='Россия',
                                                         event_desc='Душевное вятское гостеприимство, высокий уровень организации мероприятий, атмосфера уюта, '
                                                                    'праздника, дружбы,любви и радости, комфорт для каждого участника - всё это ждет вас на любом нашем танго-мероприятии.'
                                                                    'Шикарный зал 700 кв. метров в самом центре города, шикарный пол, звук и свет,'
                                                                    ' любимые маэстрос, оркестры и танго-диджеи и многое другое мы готовим для участников осеннего фестиваля.'
                                                                    'В программе: ПЯТЬ милонг, ТРИ оркестра.'
                                                                    'Показательные выступления Себастьяна Арсе и Марии Мариновой.'
                                                                    'Показательные выступления Михаила Надточего и Эльвиры Ламбо.',
                                                         event_date_end='2022-10-30',
                                                         event_date_start='2022-10-28')
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

