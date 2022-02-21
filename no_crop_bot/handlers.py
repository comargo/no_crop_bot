import enum
from distutils.util import strtobool
from enum import Enum

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import MessageHandler, Filters, ConversationHandler, \
    CommandHandler, CallbackQueryHandler, TypeHandler, CallbackContext

from .context import UserData
from .photo import process_photo


def _photo_handler(update: Update, context: CallbackContext[dict, dict, dict]):
    new_photo = process_photo(
        update.message.photo[-1].get_file().download_as_bytearray(),
        resize=context.user_data.get('resize',
                                     UserData.settings['resize'].default),
        blur=context.user_data.get('blur', UserData.settings['blur'].default))
    update.message.reply_photo(new_photo)
    if context.user_data.get('auto_delete',
                             UserData.settings['auto_delete'].default):
        update.message.delete()


photo_handler = MessageHandler(filters=Filters.photo, callback=_photo_handler)


class SettingsState(Enum):
    CHOOSING = enum.auto()
    CHANGE_SETTING = enum.auto()
    AUTO_DELETE = enum.auto()


CheckBox = {False: '\u2717', True: '\u2713'}


def _option_buttons(context: CallbackContext):
    for key, option in UserData.settings.items():
        if key not in context.user_data:
            context.user_data[key] = option.default
        if option.type == bool:
            check = CheckBox[context.user_data[key]]
            yield InlineKeyboardButton(text=f'{check} {option.name}',
                                       callback_data=key)
        elif option.type == int:
            check = CheckBox[bool(context.user_data[key])]
            yield InlineKeyboardButton(
                text=f'{check} {option.name}({context.user_data[key]})',
                callback_data=key)


def _settings_entry_handler(update: Update,
                            context: CallbackContext[dict, dict, dict]):
    update.effective_message.delete()
    return _settings_handler(update, context, initial=True)


def _settings_handler(update: Update,
                      context: CallbackContext[dict, dict, dict], *,
                      initial: bool = False):
    option_buttons = list(_option_buttons(context))
    option_buttons.append(
        InlineKeyboardButton(f'Return', callback_data='return'))
    keyboard = InlineKeyboardMarkup.from_column(option_buttons)
    if initial:
        msg = update.effective_message.reply_text("Settings",
                                                  reply_markup=keyboard)
        context.user_data[
            UserData.Extra.settings_ack_message_id] = msg.message_id
    else:
        context.bot.edit_message_text(
            chat_id=update.effective_message.chat_id,
            message_id=context.user_data[
                UserData.Extra.settings_ack_message_id],
            text="Settings", reply_markup=keyboard)
    context.user_data.pop(UserData.Extra.setting_to_change, None)
    return SettingsState.CHOOSING


def _return_handler(update: Update,
                    context: CallbackContext[dict, dict, dict]):
    update.effective_message.delete()
    context.user_data.pop(UserData.Extra.settings_req_message_id, None)
    return ConversationHandler.END


def _change_setting_req_handler(update: Update,
                                context: CallbackContext[dict, dict, dict]):
    if update.callback_query.data == 'return':
        return _return_handler(update, context)

    option_id = update.callback_query.data
    option = UserData.settings.get(option_id)
    if not option:
        return None
    if option.type == bool:
        value = context.user_data.get(option_id, option.default)
        yes_check = CheckBox[True] if value else ''
        no_check = CheckBox[True] if not value else ''
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text=f'{yes_check}Yes',
                                     callback_data=option_id + ':yes'),
                InlineKeyboardButton(text=f'{no_check}No',
                                     callback_data=option_id + ':no')
            ],
            [
                InlineKeyboardButton(f'Return', callback_data='return')
            ]
        ])
        update.effective_message.edit_text(option.text, reply_markup=keyboard)
        return SettingsState.CHANGE_SETTING
    if option.type == int:
        keyboard = InlineKeyboardMarkup.from_button(
            InlineKeyboardButton(f'Return', callback_data='return')
        )
        update.effective_message.edit_text(option.text, reply_markup=keyboard)
        context.user_data[UserData.Extra.setting_to_change] = option_id
        return SettingsState.CHANGE_SETTING


def _change_setting_ack_cb_handler(update: Update,
                                   context: CallbackContext):
    if update.callback_query.data == 'return':
        return _settings_handler(update, context)

    option_id, value = update.callback_query.data.split(':', maxsplit=1)
    option = UserData.settings.get(option_id)
    if not option:
        return None
    try:
        if option.type == bool:
            value = bool(strtobool(value))
    except ValueError:
        return None
    context.user_data[option_id] = value
    return _settings_handler(update, context)


def _change_setting_ack_msg_handler(update: Update,
                                    context: CallbackContext):
    update.effective_message.delete()
    option_id = context.user_data.get(UserData.Extra.setting_to_change)
    value = update.effective_message.text
    option = UserData.settings.get(option_id)
    if not option:
        return None
    try:
        if option.type == int:
            value = int(value)
    except ValueError:
        return None
    context.user_data[option_id] = value
    return _settings_handler(update, context)


settings_handler = ConversationHandler(
    name="settings", conversation_timeout=300,
    # per_message=True,
    persistent=True,
    entry_points=[CommandHandler("settings", _settings_entry_handler)],
    states={
        SettingsState.CHOOSING: [
            CallbackQueryHandler(pattern='return', callback=_return_handler),
            CallbackQueryHandler(callback=_change_setting_req_handler),
        ],
        SettingsState.CHANGE_SETTING: [
            CallbackQueryHandler(
                callback=_change_setting_ack_cb_handler),
            MessageHandler(filters=Filters.text,
                           callback=_change_setting_ack_msg_handler)
        ],
        ConversationHandler.TIMEOUT: [
            TypeHandler(type=Update, callback=_return_handler),
        ]
    },
    fallbacks=[],
    allow_reentry=True
)
