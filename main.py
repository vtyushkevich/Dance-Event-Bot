import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
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
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
FIRST, SECOND = range(2)
# Callback data
ONE, TWO, THREE, FOUR = range(4)
Y2022, Y2023, Y2024 = range(2022, 2025)
ARCHIVE, START_OVER = 'ARCHIVE', 'START_OVER'
JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC = range(1, 13)


def end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="До встречи!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    # updater = Updater("5318589168:AAHji914LUBoYbIrwnfv3RFsL-me7KJcOFU")
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST: [
                CallbackQueryHandler(show_calendar, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(show_month_list, pattern='^' + str(Y2022) + '$'),
                CallbackQueryHandler(show_month_oct, pattern='^' + str(OCT) + '$'),
                CallbackQueryHandler(show_month_dec, pattern='^' + str(DEC) + '$'),
                CallbackQueryHandler(show_archive, pattern='^' + str(ARCHIVE) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(START_OVER) + '$'),
            ],
            SECOND: [
                CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()