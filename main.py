import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from config import BOT_TOKEN
from view import (
    start,
    start_over,
    cancel,
    creating_event,
    get_property_to_edit,
    set_property_value,
    get_date_to_edit,
    cal,
    get_photo_to_edit,
    set_photo,
    set_doc,
    show_edit_preview,
    publish_event,
    show_event_calendar,
    delete_event,
    delete_event_confirm,
)

import const as con

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
            ],
            con.CREATE_EVENT: [
                CallbackQueryHandler(
                    get_date_to_edit, pattern='^(' + con.EDIT_DATE_START + '|' + con.EDIT_DATE_END + ')$'
                ),
                CallbackQueryHandler(
                    get_photo_to_edit, pattern='^(' + con.EDIT_PHOTO + ')$'
                ),
                CallbackQueryHandler(
                    get_property_to_edit,
                    pattern='^(' + con.EDIT_NAME + '|' + con.EDIT_CITY + '|' +
                            con.EDIT_DESC + '|' + con.EDIT_COUNTRY + ')$'
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
                    cal
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
                CallbackQueryHandler(show_event_calendar, pattern='^' + con.CALENDAR + '$'),
                CallbackQueryHandler(delete_event_confirm, pattern='^' + con.DELETE_EVENT + '$'),
                CallbackQueryHandler(delete_event, pattern='^' + con.DELETE_EVENT_OK + '$'),
                CallbackQueryHandler(start_over, pattern='^' + con.GO_BACK + '$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('start', start),],
    )
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
