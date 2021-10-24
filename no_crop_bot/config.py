import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT')
MONGODB = os.environ.get('MONGODB')
DEBUG = os.environ.get('DEBUG')
