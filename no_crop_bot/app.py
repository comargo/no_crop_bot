from typing import Optional

from telegram.ext import Updater, Dispatcher, ContextTypes

from mongoptb import MongoDBPersistence
from no_crop_bot import config, handlers

persistence: Optional[MongoDBPersistence] = None
if config.MONGODB_URL and config.MONGODB_DB:
    persistence = MongoDBPersistence(url=config.MONGODB_URL,
                                     database=config.MONGODB_DB)
updater = Updater(token=config.TOKEN,
                  persistence=persistence)
dispatcher: Dispatcher = updater.dispatcher

dispatcher.add_handler(handlers.photo_handler)
if not persistence:
    handlers.settings_handler.persistent = False
dispatcher.add_handler(handlers.settings_handler)


def app():
    if config.WEBHOOK_URL:
        updater.start_webhook(listen='0.0.0.0',
                              port=config.PORT,
                              url_path=config.TOKEN,
                              webhook_url=config.WEBHOOK_URL)
    else:
        updater.start_polling()
    updater.idle()
