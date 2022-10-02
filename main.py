import logging
from telegram import Update, Message
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
    show_calendar,
    show_month_list,
    show_month_oct,
    show_month_dec,
    show_archive,
    show_management,
    go_back,
    cancel,
    creating_event,
    get_property_to_edit,
    set_property_value,
    get_date_to_edit,
    cal
)

from view import EDIT_NAME, EDIT_CITY, EDIT_DESC, EDIT_DATE_START


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
TOP_LEVEL, CREATE_EVENT, CREATE_DATE = range(3)
# Callback data
ONE, TWO, THREE, FOUR = range(4)
Y2022, Y2023, Y2024 = range(2022, 2025)
ARCHIVE, START_OVER, MANAGEMENT, EDIT, CREATE, BACK = 'ARCHIVE', 'START_OVER', 'MANAGEMENT', 'EDIT', 'CREATE', 'BACK'
JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC = range(1, 13)
GENDER, PHOTO, LOCATION, BIO = range(4)


def main() -> None:
    """Run the bot."""
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TOP_LEVEL: [
                CallbackQueryHandler(show_calendar, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(show_archive, pattern='^' + str(ARCHIVE) + '$'),
                CallbackQueryHandler(creating_event, pattern='^' + str(MANAGEMENT) + '$'),
                # CallbackQueryHandler(show_month_list, pattern='^' + str(Y2022) + '$'),
                # CallbackQueryHandler(show_month_oct, pattern='^' + str(OCT) + '$'),
                # CallbackQueryHandler(show_month_dec, pattern='^' + str(DEC) + '$'),
                # CallbackQueryHandler(start_over, pattern='^' + str(START_OVER) + '$'),
                # CallbackQueryHandler(go_back, pattern='^' + str(CREATE) + '$'),
                # CallbackQueryHandler(go_back, pattern='^' + str(EDIT) + '$'),
            ],
            CREATE_EVENT: [
                CallbackQueryHandler(
                    get_property_to_edit, pattern='^(' + EDIT_NAME + '|' + EDIT_CITY + '|' + EDIT_DESC + ')$'
                ),
                CallbackQueryHandler(
                    get_date_to_edit, pattern='^(' + EDIT_DATE_START + ')$'
                ),
                CallbackQueryHandler(go_back, pattern='^' + str(BACK) + '$'),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    set_property_value,
                )
            ],
            CREATE_DATE: [
                CallbackQueryHandler(
                    cal
                ),
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