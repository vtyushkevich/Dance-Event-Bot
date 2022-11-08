# Dance-Event-Bot
Telegram bot for checking dance events\
Main functions:
 - view of calendar events
 - creating, updating and deleting events (if administrator)
 - check-in for events in calendar
 - search check-ins of other users

To use the bot:
- clone project from git
- install requirements
- create config.py in project dir with following contents:

BOT_TOKEN = "1234567890:[A-z]"\
DB_URL = "postgresql+pg8000://[login]:[password]@localhost:5432/[dbname]"\
DB_ECHO = True

BASIC_ADMIN_ID = 123456789\
BASIC_ADMIN_USERNAME = 'BASIC_ADMIN'

- create .env file for docker in project dir with following contents:\
POSTGRES_DB="dbname"\
POSTGRES_USER="login"\
POSTGRES_PASSWORD="password"