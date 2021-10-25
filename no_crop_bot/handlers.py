from telegram import Update
from telegram.ext import MessageHandler, Filters
from telegram.ext.utils.types import CCT

from .photo import process_photo


def _photo_handler(update: Update, context: CCT):
    new_photo = process_photo(
        update.message.photo[-1].get_file().download_as_bytearray())
    update.message.reply_photo(new_photo)
    update.message.edit_media()


photo_handler = MessageHandler(filters=Filters.photo, callback=_photo_handler)
