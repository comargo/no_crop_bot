from telegram.ext import Updater, Dispatcher

from no_crop_bot import config, handlers

updater = Updater(config.TOKEN)
dispatcher: Dispatcher = updater.dispatcher

dispatcher.add_handler(handlers.photo_handler)

