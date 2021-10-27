import os
from distutils.util import strtobool

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT', 8443)
MONGODB_URL = os.environ.get('MONGODB_URL')
MONGODB_DB = os.environ.get('MONGODB_DB')
DEBUG = bool(strtobool(os.environ.get('DEBUG', 'False')))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
