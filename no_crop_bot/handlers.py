import enum
from distutils.util import strtobool
from enum import Enum

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, ConversationHandler, \
    CommandHandler, CallbackQueryHandler, TypeHandler, CallbackContext

from .context import UserData
from .photo import process_photo


def _photo_handler(update: Update, context: CallbackContext):
    new_photo = process_photo(
        update.message.photo[-1].get_file().download_as_bytearray(),
        resize=context.user_data['resize'])
    update.message.reply_photo(new_photo)
    if context.user_data['auto_delete']:
        update.message.delete()


photo_handler = MessageHandler(filters=Filters.photo, callback=_photo_handler)


class SettingsState(Enum):
    CHOOSING = enum.auto()
    CHANGE_SETTING = enum.auto()
    AUTO_DELETE = enum.auto()


CheckBox = {False: '\u2717', True: '\u2713'}


def _option_buttons(context: CallbackContext):
    for option in UserData.settings:
        if option.type == bool:
            if option.id not in context.user_data:
                context.user_data[option.id] = bool(option.default)
            check = CheckBox[context.user_data[option.id]]
            yield InlineKeyboardButton(text=check + option.name,
                                       callback_data=option.id)


def _settings_handler(update: Update,
                      context: CallbackContext[dict, dict, dict]):
    option_buttons = list(_option_buttons(context))
    option_buttons.append(
        InlineKeyboardButton(f'Return', callback_data='return'))
    keyboard = InlineKeyboardMarkup.from_column(option_buttons)
    if not context.user_data.get(UserData.Extra.settings_message_id):
        context.user_data[
            UserData.Extra.settings_message_id] = update.effective_message.message_id
        update.effective_message.reply_text("Settings", reply_markup=keyboard)
    else:
        update.effective_message.edit_text("Settings", reply_markup=keyboard)
    return SettingsState.CHOOSING


def _return_handler(update: Update,
                    context: CallbackContext[dict, dict, dict]):
    context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.user_data[UserData.Extra.settings_message_id])
    update.effective_message.delete()
    context.user_data[UserData.Extra.settings_message_id] = None
    return ConversationHandler.END


def _change_setting_request_handler(update: Update, context: CallbackContext):
    if update.callback_query.data == 'return':
        return _return_handler(update, context)

    option = next((option for option in UserData.settings if
                   option.id == update.callback_query.data), None)
    if not option:
        return None
    if option.id not in context.user_data:
        return None
    if option.type == bool:
        value = context.user_data[option.id]
        yes_check = CheckBox[True] if value else ''
        no_check = CheckBox[True] if not value else ''
        keyboard = InlineKeyboardMarkup.from_row([
            InlineKeyboardButton(f'{yes_check}Yes',
                                 callback_data=option.id + ':yes'),
            InlineKeyboardButton(f'{no_check}No',
                                 callback_data=option.id + ':no')
        ])
        update.effective_message.edit_text(option.text, reply_markup=keyboard)
        return SettingsState.CHANGE_SETTING


def _change_setting_answer_handler(update: Update, context: CallbackContext):
    option_id, value = update.callback_query.data.split(':', maxsplit=1)
    option = next(
        (option for option in UserData.settings if option.id == option_id),
        None)
    if not option:
        return None
    if option.id not in context.user_data:
        return None
    try:
        if option.type == bool:
            value = bool(strtobool(value))
    except ValueError:
        return None
    context.user_data[option.id] = value
    return _settings_handler(update, context)


settings_handler = ConversationHandler(
    name="settings", conversation_timeout=300,
    # per_message=True,
    persistent=True,
    entry_points=[CommandHandler("settings", _settings_handler)],
    states={
        SettingsState.CHOOSING: [
            CallbackQueryHandler(pattern='return', callback=_return_handler),
            CallbackQueryHandler(callback=_change_setting_request_handler),
        ],
        SettingsState.CHANGE_SETTING: [
            CallbackQueryHandler(callback=_change_setting_answer_handler)
        ],
        ConversationHandler.TIMEOUT: [
            TypeHandler(type=Update, callback=_return_handler),
        ]
    },
    fallbacks=[]
)
