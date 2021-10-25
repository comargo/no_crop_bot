import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT', 8443)
MONGODB = os.environ.get('MONGODB')
DEBUG = os.environ.get('DEBUG')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', None)
