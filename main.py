import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)

from almanac.view import show_event_calendar, delete_event_confirm, delete_event, show_select_2, \
    browse_event_calendar, show_events_of_month, update_page_of_month, show_selected_event
from config import BOT_TOKEN
# from core.models import Base
from events.view import creating_event, get_date_to_edit, get_property_to_edit, show_edit_preview, publish_event, \
    set_date_value, set_property_value, set_photo, set_doc
from main.view import (
    start,
    start_over,
    cancel,
)

import const as con
from main_models import Session

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            con.TOP_LEVEL: [
                CallbackQueryHandler(creating_event, pattern='^' + con.MANAGEMENT + '$'),
                CallbackQueryHandler(show_event_calendar, pattern='^' + con.CALENDAR + '$'),
                CallbackQueryHandler(show_select_2, pattern='^' + con.DELETE_EVENT + '$'),
            ],
            con.CREATE_EVENT: [
                CallbackQueryHandler(
                    get_date_to_edit, pattern='^(' + con.EDIT_DATE_START + '|' + con.EDIT_DATE_END + ')$'
                ),
                CallbackQueryHandler(
                    get_property_to_edit,
                    pattern='^(' + con.EDIT_NAME + '|' + con.EDIT_CITY + '|' +
                            con.EDIT_DESC + '|' + con.EDIT_COUNTRY + '|' + con.EDIT_PHOTO + ')$'
                ),
                CallbackQueryHandler(
                    show_edit_preview,
                    pattern='^(' + con.EDIT_PREVIEW + ')$'
                ),
                CallbackQueryHandler(
                    publish_event,
                    pattern='^(' + con.PUBLISH_EVENT + ')$'
                ),
                CallbackQueryHandler(start_over, pattern='^' + con.START_OVER + '$'),
                CallbackQueryHandler(creating_event, pattern='^' + con.GO_BACK + '$'),
            ],
            con.CREATE_DATE: [
                CallbackQueryHandler(creating_event, pattern='^' + con.GO_BACK + '$'),
                CallbackQueryHandler(
                    set_date_value, pattern='^' + 'cbcal.*' + '$'
                ),
                CallbackQueryHandler(
                    get_date_to_edit, pattern='^(' + con.EDIT_DATE_START + '|' + con.EDIT_DATE_END + ')$'
                ),
            ],
            con.CREATE_PROPERTY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    set_property_value,
                ),
                CallbackQueryHandler(creating_event, pattern='^' + con.GO_BACK + '$'),
            ],
            con.CREATE_PHOTO: [
                MessageHandler(
                    Filters.photo & ~(Filters.command | Filters.regex('^Done$')),
                    set_photo,
                ),
                MessageHandler(
                    Filters.document & ~(Filters.command | Filters.regex('^Done$')),
                    set_doc,
                ),
                CallbackQueryHandler(creating_event, pattern='^' + con.GO_BACK + '$'),
            ],
            con.CALENDAR: [
                CallbackQueryHandler(show_event_calendar, pattern='^' + con.CALENDAR + '|' + con.GO_BACK + '<' + '$'),
                CallbackQueryHandler(update_page_of_month, pattern='^' + con.BACK_LIST + '|' + con.FORWARD_LIST + '$'),
                CallbackQueryHandler(show_events_of_month, pattern='^' + con.SELECT_ALM + '_\d{6}' + '|' + con.GO_BACK + '<<' + '$'),
                CallbackQueryHandler(show_selected_event, pattern='^' + con.SELECT_EVENT + '.*$'),
                CallbackQueryHandler(delete_event_confirm, pattern='^' + con.DELETE_EVENT + '.*$'),
                CallbackQueryHandler(delete_event, pattern='^' + con.DELETE_CONFIRMED + '.*$'),
                CallbackQueryHandler(start_over, pattern='^' + con.GO_BACK + '$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
