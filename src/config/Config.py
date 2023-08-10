<<<<<<< HEAD
import configparser

config = configparser.ConfigParser()
config.read('config.config')

# Read Slack configuration
SLACK_WEBHOOK_URL = config.get('SLACK', 'SLACK_WEBHOOK_URL')



# Read Telegram configuration
TELEGRAM_TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = config.get('TELEGRAM', 'TELEGRAM_CHAT_ID')

# Read Database configuration
DB_HOST = config.get('DATABASE', 'DB_HOST')
DB_PORT = config.getint('DATABASE', 'DB_PORT')
DB_NAME = config.get('DATABASE', 'DB_NAME')
COLLECTION_NAME = config.get('DATABASE', 'COLLECTION_NAME')
DB_USER = config.get('DATABASE', 'DB_USER')
DB_PWD = config.get('DATABASE', 'DB_PWD')

# Read Resolvers configuration
resolvers_list = config.get('RESOLVERS', 'RESOLVERS_LIST').split('\n')
# Remove empty entries
RESOLVERS_LIST = [resolver.strip() for resolver in resolvers_list if resolver.strip()]
