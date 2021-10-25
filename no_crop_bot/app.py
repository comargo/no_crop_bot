from telegram.ext import Updater, Dispatcher

from no_crop_bot import config, handlers

updater = Updater(config.TOKEN)
dispatcher: Dispatcher = updater.dispatcher

dispatcher.add_handler(handlers.photo_handler)


def app():
    if config.WEBHOOK_URL:
        updater.start_webhook(listen='0.0.0.0',
                              port=config.PORT,
                              url_path=config.TOKEN,
                              webhook_url=config.WEBHOOK_URL)
    else:
        updater.start_polling()
    updater.idle()
