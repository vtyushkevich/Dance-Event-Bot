import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
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
    show_edit_preview,
    publish_event
)

import const as con


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
TOP_LEVEL, CREATE_EVENT, CREATE_DATE, CREATE_PROPERTY, CREATE_PHOTO = range(5)
# Callback data
START, ARCHIVE, START_OVER, MANAGEMENT, EDIT, CREATE, GO_BACK = 'START', 'ARCHIVE', 'START_OVER', 'MANAGEMENT', 'EDIT', 'CREATE', 'GO_BACK'


def main() -> None:
    """Run the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOP_LEVEL: [
                CallbackQueryHandler(creating_event, pattern='^' + MANAGEMENT + '$'),
            ],
            CREATE_EVENT: [
                CallbackQueryHandler(
                    get_date_to_edit, pattern='^(' + con.EDIT_DATE_START + '|' + con.EDIT_DATE_END + ')$'
                ),
                CallbackQueryHandler(
                    get_photo_to_edit, pattern='^(' + con.EDIT_PHOTO + ')$'
                ),
                CallbackQueryHandler(
                    get_property_to_edit,
                    pattern='^(' + con.EDIT_NAME + '|' + con.EDIT_CITY + '|' + con.EDIT_DESC + '|' + con.EDIT_COUNTRY + ')$'
                ),
                CallbackQueryHandler(
                    show_edit_preview,
                    pattern='^(' + con.EDIT_PREVIEW + ')$'
                ),
                CallbackQueryHandler(
                    publish_event,
                    pattern='^(' + con.PUBLISH_EVENT + ')$'
                ),
                CallbackQueryHandler(start_over, pattern='^' + START_OVER + '$'),
                CallbackQueryHandler(creating_event, pattern='^' + GO_BACK + '$'),
            ],
            CREATE_DATE: [
                CallbackQueryHandler(
                    cal
                ),
            ],
            CREATE_PROPERTY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    set_property_value,
                ),
                CallbackQueryHandler(creating_event, pattern='^' + GO_BACK + '$'),
            ],
            CREATE_PHOTO: [
                MessageHandler(
                    Filters.photo & ~(Filters.command | Filters.regex('^Done$')),
                    set_photo,
                ),
                CallbackQueryHandler(creating_event, pattern='^' + GO_BACK + '$'),
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()