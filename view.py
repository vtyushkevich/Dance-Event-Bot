from pathlib import Path
import logging
import const as con
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove,
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# def start(update: Update, context: CallbackContext) -> int:
#     """Send a message on `/start`."""
#     logger.info("User %s started the conversation.", update.message.from_user.first_name)
#     send_text_and_keyboard(
#         update=update.message.reply_text,
#         keyboard=set_keyboard(context, con.START),
#         message_text="\U0001F483 Я бот для отслеживания танцевальных событий и расскажу, что происходит в мире танцев "
#                      "\U0001F525",
#     )
#     set_default_userdata(context)
#     context.user_data['FAKE_TEXT'] = generate_text_event(event_name='FESTIVALITO LA VIDA, MÚSICA Y TANGO 2022',
#                                                          event_city='Челябинск',
#                                                          event_country='Россия',
#                                                          event_desc='Душевное вятское гостеприимство, высокий уровень организации мероприятий, атмосфера уюта, '
#                                                                     'праздника, дружбы,любви и радости, комфорт для каждого участника - всё это ждет вас на любом нашем танго-мероприятии.'
#                                                                     'Шикарный зал 700 кв. метров в самом центре города, шикарный пол, звук и свет,'
#                                                                     ' любимые маэстрос, оркестры и танго-диджеи и многое другое мы готовим для участников осеннего фестиваля.'
#                                                                     'В программе: ПЯТЬ милонг, ТРИ оркестра.'
#                                                                     'Показательные выступления Себастьяна Арсе и Марии Мариновой.'
#                                                                     'Показательные выступления Михаила Надточего и Эльвиры Ламбо.',
#                                                          event_date_end='2022-10-30',
#                                                          event_date_start='2022-10-28')
#     return con.TOP_LEVEL
#
#
# def start_over(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     if query.message.caption:
#         query.delete_message()
#     send_text_and_keyboard(
#         update=query.message.reply_text if query.message.caption else query.edit_message_text,
#         keyboard=set_keyboard(context, con.START),
#         message_text="\U000026F3 Что делаем дальше?",
#     )
#     set_default_userdata(context)
#     return con.TOP_LEVEL
#
#
# def cancel(update: Update, context: CallbackContext) -> int:
#     logger.info("User %s canceled the conversation.", update.message.from_user.first_name)
#     send_text_and_keyboard(
#         update=update.message.reply_text,
#         keyboard='',
#         message_text='До встречи!',
#     )
#     return ConversationHandler.END


# def creating_event(update: Update, context: CallbackContext) -> int:
#     update.callback_query.answer()
#     message = update.callback_query.message
#     if message.caption:
#         message.delete()
#     send_text_and_keyboard(
#         update=message.reply_text if message.caption else message.edit_text,
#         keyboard=set_keyboard(context, con.CREATE_EVENT),
#         message_text=con.TEXT_REQUEST[con.CREATE_EVENT],
#     )
#     return con.CREATE_EVENT
#
#
# def get_property_to_edit(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     context.user_data[con.PROPERTY_TO_EDIT] = query.data
#     context.user_data[con.CALLBACK_QUERY] = query
#     send_text_and_keyboard(
#         update=query.edit_message_text,
#         keyboard=[[InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)]],
#         message_text=con.TEXT_REQUEST[query.data],
#     )
#     return con.CREATE_PHOTO if query.data == con.EDIT_PHOTO else con.CREATE_PROPERTY
#
#
# def set_property_value(update: Update, context: CallbackContext) -> int:
#     _cb = context.user_data[con.CALLBACK_QUERY]
#     _cb.message.delete()
#     user_data = context.user_data
#     input_from_user = update.message.text
#     category = user_data[con.PROPERTY_TO_EDIT]
#     _validation_passed, _validation_comment = validate_user_data(category, input_from_user)
#     if _validation_passed:
#         user_data[category] = input_from_user
#         del user_data[con.PROPERTY_TO_EDIT]
#         send_text_and_keyboard(
#             update=update.message.reply_text,
#             keyboard=set_keyboard(context, con.CREATE_EVENT),
#             message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
#         )
#         return con.CREATE_EVENT
#     else:
#         send_text_and_keyboard(
#             update=update.message.reply_text,
#             keyboard=[[InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)]],
#             message_text=_validation_comment
#         )
#         return con.CREATE_PROPERTY
#
#
# def get_date_to_edit(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     context.user_data[con.PROPERTY_TO_EDIT] = query.data
#     calendar, step = DetailedTelegramCalendar(
#         calendar_id=1,
#         additional_buttons=[{"text": "\U00002B05 Назад", 'callback_data': con.GO_BACK}], ).build()
#     send_text_and_keyboard(
#         update=query.edit_message_text,
#         keyboard=calendar,
#         message_text=con.TEXT_REQUEST[query.data]
#     )
#     return con.CREATE_DATE
#
#
# def set_date_value(update: Update, context: CallbackContext):
#     query = update.callback_query
#     query.answer()
#     result, key, step = DetailedTelegramCalendar().process(query.data)
#     if not result and key:
#         send_text_and_keyboard(
#             update=query.edit_message_text,
#             keyboard=key,
#             message_text=f"Select {LSTEP[step]}"
#         )
#         return con.CREATE_DATE
#     elif result:
#         user_data = context.user_data
#         category = user_data[con.PROPERTY_TO_EDIT]
#         user_data[category + '_dt'] = result
#         _validation_passed, _validation_comment = validate_user_data(category + '_dt', checked_date=result)
#         if _validation_passed:
#             _validation_passed, _validation_comment = validate_user_data(
#                 category + '_dt',
#                 checked_date=user_data[con.EDIT_DATE_START + '_dt'],
#                 checked_sec_date=user_data[con.EDIT_DATE_END + '_dt']
#             )
#         if _validation_passed:
#             _datetype = {con.EDIT_DATE_START: 'Дата начала ', con.EDIT_DATE_END: 'Дата окончания '}
#             user_data[category] = _datetype[category] + str(result)
#             del user_data[con.PROPERTY_TO_EDIT]
#             send_text_and_keyboard(
#                 update=query.edit_message_text,
#                 keyboard=set_keyboard(context, con.CREATE_EVENT),
#                 message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
#             )
#             return con.CREATE_EVENT
#         else:
#             user_data[category + '_dt'] = None
#             send_text_and_keyboard(
#                 update=query.edit_message_text,
#                 keyboard=[[InlineKeyboardButton("\U00002B05 Назад", callback_data=category)]],
#                 message_text=_validation_comment
#             )
#             return con.CREATE_DATE
#
#
# def set_photo(update: Update, context: CallbackContext) -> int:
#     _cb = context.user_data[con.CALLBACK_QUERY]
#     _cb.message.delete()
#     user_data = context.user_data
#     category = user_data[con.PROPERTY_TO_EDIT]
#     photo_file = update.message.photo[-1]
#     user_data[category] = photo_file.file_id
#     del user_data[con.PROPERTY_TO_EDIT]
#     send_text_and_keyboard(
#         update=update.message.reply_text,
#         keyboard=set_keyboard(context, con.CREATE_EVENT),
#         message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
#     )
#     return con.CREATE_EVENT
#
#
# def set_doc(update: Update, context: CallbackContext) -> int:
#     _cb = context.user_data[con.CALLBACK_QUERY]
#     _cb.message.delete()
#     user_data = context.user_data
#     category = user_data[con.PROPERTY_TO_EDIT]
#     doc_file = update.message.document
#     photo_file = doc_file.get_file()
#     photo_file.download(custom_path='./banners/' + photo_file.file_unique_id)
#     _validation_passed, _validation_comment = validate_user_data(category, userdata=photo_file.file_size)
#     _validation_mime_passed, _validation_mime_comment = validate_user_data(category, mimetype=doc_file.mime_type)
#     if _validation_passed and _validation_mime_passed:
#         user_data[category] = Path.cwd() / 'banners' / photo_file.file_unique_id
#         del user_data[con.PROPERTY_TO_EDIT]
#         _msg = update.message.reply_photo(
#             photo=open(user_data[category], 'rb'),
#         )
#         user_data[category] = _msg.photo[-1]
#         send_text_and_keyboard(
#             update=update.message.reply_text,
#             keyboard=set_keyboard(context, con.CREATE_EVENT),
#             message_text=con.TEXT_REQUEST[con.CREATE_EVENT]
#         )
#         return con.CREATE_EVENT
#     else:
#         send_text_and_keyboard(
#             update=update.message.reply_text,
#             keyboard=[[InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)]],
#             message_text=(_validation_comment if _validation_comment else _validation_mime_comment)
#         )
#         return con.CREATE_PHOTO
#
#
# def show_edit_preview(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     user_data = context.user_data
#     _validation_passed, _validation_comment = validate_user_data(con.PUBLISH_EVENT, userdata=context)
#     if _validation_passed:
#         keyboard = [
#             [InlineKeyboardButton("Опубликовать", callback_data=con.PUBLISH_EVENT)],
#             [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
#         ]
#     else:
#         keyboard = [[InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)]]
#     _text = generate_text_event(user_data[con.EDIT_NAME], user_data[con.EDIT_CITY], user_data[con.EDIT_COUNTRY],
#                                 user_data[con.EDIT_DATE_START], user_data[con.EDIT_DATE_END], user_data[con.EDIT_DESC])
#     if user_data[con.EDIT_PHOTO]:
#         query.message.delete()
#     send_text_and_keyboard(
#         update=query.message.reply_photo if user_data[con.EDIT_PHOTO] else query.edit_message_text,
#         keyboard=keyboard,
#         message_text=_text,
#         photo=user_data[con.EDIT_PHOTO] if user_data[con.EDIT_PHOTO] else None
#     )
#     return con.CREATE_EVENT
#
#
# def publish_event(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     send_text_and_keyboard(
#         update=query.message.edit_reply_markup,
#         keyboard='',
#         message_text=None
#     )
#     send_text_and_keyboard(
#         update=query.message.reply_text,
#         keyboard=[[InlineKeyboardButton("Ок", callback_data=con.START_OVER)]],
#         message_text="\U0001F4F0 Событие опубликовано!"
#     )
#     return con.CREATE_EVENT


# def show_event_calendar(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     _text = context.user_data['FAKE_TEXT']
#     if _text:
#         query.delete_message()
#         keyboard = set_keyboard(context, con.CALENDAR)
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         query.message.reply_photo(
#             photo='AgACAgIAAxkBAAIC8mNEWei1pJxkp_kZXTGbHNV6tF1ZAALfwzEbsOsgSjmF2xeA2UOiAQADAgADbQADKgQ',
#             caption=_text,
#             reply_markup=reply_markup
#         )
#     else:
#         keyboard = [[InlineKeyboardButton("Ок", callback_data=con.GO_BACK)]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         query.message.edit_text(
#             text="Нет активных событий",
#             reply_markup=reply_markup
#         )
#     return con.CALENDAR
#
#
# def delete_event_confirm(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     query.delete_message()
#     keyboard = [
#         [InlineKeyboardButton("Удалить", callback_data=con.DELETE_EVENT_OK)],
#         [InlineKeyboardButton("Назад", callback_data=con.CALENDAR)],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.message.reply_text(
#         text="Вы уверены, что хотите удалить событие?",
#         reply_markup=reply_markup
#     )
#     return con.CALENDAR
#
#
# def delete_event(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     context.user_data['FAKE_TEXT'] = ''
#     keyboard = [[InlineKeyboardButton("Ок", callback_data=con.GO_BACK)]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     query.message.edit_text(
#         text="Событие удалено!",
#         reply_markup=reply_markup
#     )
#     return con.CALENDAR


# def set_default_userdata(context: CallbackContext):
#     context.user_data[con.EDIT_NAME] = "Название события"
#     context.user_data[con.EDIT_CITY] = "Город"
#     context.user_data[con.EDIT_COUNTRY] = "Страна"
#     context.user_data[con.EDIT_DESC] = ""
#     context.user_data[con.EDIT_DATE_START] = "Дата начала"
#     context.user_data[con.EDIT_DATE_END] = "Дата окончания"
#     context.user_data[con.EDIT_DATE_START + '_dt'] = None
#     context.user_data[con.EDIT_DATE_END + '_dt'] = None
#     context.user_data[con.EDIT_PHOTO] = ""
#     context.user_data[con.PROPERTY_TO_EDIT] = None
#     context.user_data[con.CALLBACK_QUERY] = None
#
#
# def set_keyboard(context: CallbackContext, stage: str):
#     user_data = context.user_data
#     keyboard = None
#     if stage == con.START:
#         keyboard = [
#             [InlineKeyboardButton("\U0001F4C6   Календарь событий", callback_data=con.CALENDAR)],
#             [InlineKeyboardButton("\U0001FAA9   Создать событие", callback_data=con.MANAGEMENT)],
#             # [InlineKeyboardButton("\U0001F5C4   Посмотреть архив", callback_data=con.ARCHIVE)],
#         ]
#     if stage == con.CREATE_EVENT:
#         keyboard = [
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_NAME] != "Название события") +
#                                   "   " + user_data[con.EDIT_NAME], callback_data=con.EDIT_NAME)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_COUNTRY] != "Страна") +
#                                   "   " + user_data[con.EDIT_COUNTRY], callback_data=con.EDIT_COUNTRY)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_CITY] != "Город") +
#                                   "   " + user_data[con.EDIT_CITY], callback_data=con.EDIT_CITY)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_START] != "Дата начала") +
#                                   "   " + str(user_data[con.EDIT_DATE_START]), callback_data=con.EDIT_DATE_START)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DATE_END] != "Дата окончания") +
#                                   "   " + str(user_data[con.EDIT_DATE_END]), callback_data=con.EDIT_DATE_END)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_DESC] != "") +
#                                   "   Описание", callback_data=con.EDIT_DESC)],
#             [InlineKeyboardButton(check_symbol(user_data[con.EDIT_PHOTO] != "") +
#                                   "   Картинка", callback_data=con.EDIT_PHOTO)],
#             [InlineKeyboardButton("\U0001F57A Предварительный просмотр", callback_data=con.EDIT_PREVIEW)],
#             [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.START_OVER)],
#         ]
#     if stage == con.CALENDAR:
#         keyboard = [
#             [InlineKeyboardButton("\U0001F5D1 Удалить событие", callback_data=con.DELETE_EVENT)],
#             [InlineKeyboardButton("\U00002B05 Назад", callback_data=con.GO_BACK)],
#         ]
#     return keyboard
#
#
# def generate_text_event(
#         event_name: str,
#         event_city: str,
#         event_country: str,
#         event_date_start: str,
#         event_date_end: str,
#         event_desc: str,
# ):
#     _text = '\U0001F46B ' + event_name + '\n' * 2
#     _text = _text + '\U0001F4CD ' + ('' if event_city == 'Город' else event_city + ', ')
#     _text = _text + ('' if event_country == 'Страна' else event_country) + '\n' * 2
#     _text = _text + '\U0001F680 ' + ("Дата начала не указана" if event_date_start == "Дата начала" else
#                                      event_date_start) + '\n' * 2
#     _text = _text + '\U0001F3C1 ' + ("Дата окончания не указана" if event_date_end == "Дата окончания" else
#                                      event_date_end) + '\n' * 2
#
#     _text = _text + ("" if event_desc == "" else
#                      'О событии:\n' + event_desc)
#     return _text


# def validate_user_data(category: str, userdata=None, mimetype=None, checked_date=None, checked_sec_date=None):
#     validation_passed, validation_comment = True, None
#     if category == con.EDIT_NAME or category == con.EDIT_COUNTRY or category == con.EDIT_CITY:
#         _name_len = 50
#         validation_passed = len(userdata) < _name_len
#         if not validation_passed:
#             validation_comment = '\U0001F6AB Название не должно быть длиннее ' + str(_name_len) + ' символов'
#             return validation_passed, validation_comment
#     if category == con.EDIT_DESC:
#         _name_len = 1000
#         validation_passed = len(userdata) < _name_len
#         if not validation_passed:
#             validation_comment = '\U0001F6AB Описание не должно быть длиннее ' + str(_name_len) + ' символов'
#             return validation_passed, validation_comment
#     if category == con.EDIT_PHOTO:
#         if userdata:
#             _name_len = 10485760
#             validation_passed = userdata < _name_len
#             if not validation_passed:
#                 validation_comment = '\U0001F6AB Картинка не должна весить более 10 Мб'
#                 return validation_passed, validation_comment
#         if mimetype:
#             validation_passed = mimetype == 'image/gif' or mimetype == 'image/jpeg' or mimetype == 'image/png'
#             if not validation_passed:
#                 validation_comment = '\U0001F6AB Некорректный формат файла'
#                 return validation_passed, validation_comment
#     if category == con.EDIT_DATE_START + '_dt' and checked_date is not None or \
#             category == con.EDIT_DATE_END + '_dt' and checked_date is not None:
#         validation_passed = checked_date >= date.today()
#         if not validation_passed:
#             validation_comment = '\U0001F6AB Дата события не должна быть в прошлом времени'
#             return validation_passed, validation_comment
#     if (category == con.EDIT_DATE_START + '_dt' or category == con.EDIT_DATE_END + '_dt') \
#             and checked_date is not None and checked_sec_date is not None:
#         _delta: timedelta = (checked_sec_date - checked_date)
#         validation_passed = _delta.total_seconds() > 0
#         if not validation_passed:
#             validation_comment = '\U0001F6AB Дата окончания события не должна быть раньше начала события'
#             return validation_passed, validation_comment
#     if category == con.PUBLISH_EVENT:
#         validation_passed = userdata.user_data[con.EDIT_NAME] != "Название события" \
#                             and userdata.user_data[con.EDIT_CITY] != "Город" \
#                             and userdata.user_data[con.EDIT_COUNTRY] != "Страна" \
#                             and userdata.user_data[con.EDIT_DESC] != "" \
#                             and userdata.user_data[con.EDIT_DATE_START + '_dt'] is not None \
#                             and userdata.user_data[con.EDIT_DATE_END + '_dt'] is not None
#         if not validation_passed:
#             validation_comment = '\U0001F6AB Не заполнены все поля события'
#             return validation_passed, validation_comment
#     return validation_passed, validation_comment


# def check_symbol(checked: bool):
#     if checked:
#         return "\U00002705"
#     else:
#         return "\U00002611"
#
#
# def send_text_and_keyboard(update, keyboard, message_text, photo=None):
#     if message_text is None:
#         update(
#             reply_markup=InlineKeyboardMarkup(keyboard)
#         )
#     else:
#         if isinstance(keyboard, str):
#             reply_markup = keyboard
#         else:
#             reply_markup = InlineKeyboardMarkup(keyboard)
#         if photo is None:
#             update(
#                 text=message_text,
#                 reply_markup=reply_markup
#             )
#         else:
#             update(
#                 caption=message_text,
#                 reply_markup=reply_markup,
#                 photo=photo
#             )