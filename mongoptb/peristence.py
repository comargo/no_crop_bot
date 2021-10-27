import json
import pickle
from collections import defaultdict
from typing import DefaultDict, Tuple, Optional

from bson.binary import Binary, USER_DEFINED_SUBTYPE
from bson.codec_options import TypeDecoder, CodecOptions, TypeRegistry
from pymongo import MongoClient
from telegram.ext import BasePersistence
from telegram.ext.utils.types import ConversationDict, CDCData, UD, CD, BD


def fallback_pickle_encoder(value):
    return Binary(pickle.dumps(value), USER_DEFINED_SUBTYPE)


class PickledBinaryDecoder(TypeDecoder):
    bson_type = Binary

    def transform_bson(self, value):
        if value.subtype == USER_DEFINED_SUBTYPE:
            return pickle.loads(value)
        return value


_codec_options = CodecOptions(type_registry=TypeRegistry(
    [PickledBinaryDecoder()], fallback_encoder=fallback_pickle_encoder))


class MongoDBPersistence(BasePersistence):
    def __init__(self, url: str, database: str, prefix: str = None,
                 store_user_data: bool = True, store_chat_data: bool = True,
                 store_bot_data: bool = True,
                 store_callback_data: bool = False):
        super().__init__(store_user_data, store_chat_data, store_bot_data,
                         store_callback_data)
        client = MongoClient(url)
        prefix = prefix or ''
        self.db = client.get_database(name=database,
                                      codec_options=_codec_options)
        self.user = self.db[f'{prefix}user']
        self.chat = self.db[f'{prefix}chat']
        self.conversations = self.db[f'{prefix}conversations']
        self.callback = self.db[f'{prefix}callback']

    def get_user_data(self) -> DefaultDict[int, UD]:
        return defaultdict(dict, {
            data['_id']: {i: data[i] for i in data if i != '_id'} for data in
            self.user.find({'_id': {'$ne': 'me'}})})

    def get_chat_data(self) -> DefaultDict[int, CD]:
        return defaultdict(dict, {
            data['_id']: {i: data[i] for i in data if i != '_id'} for data in
            self.chat.find({})})

    def get_bot_data(self) -> BD:
        return defaultdict(dict, self.user.find_one({'_id': 'me'}) or dict())

    def get_callback_data(self) -> Optional[CDCData]:
        return None

    def get_conversations(self, name: str) -> ConversationDict:
        return {tuple(json.loads(_id)): data for _id, data in
                (self.conversations.find_one({'_id': name}) or {}).items() if
                _id != '_id'}

    def update_conversation(self, name: str, key: Tuple[int, ...],
                            new_state: Optional[object]) -> None:
        if new_state is not None:
            self.conversations.update_one({'_id': str(name)}, {
                '$set': {json.dumps(key): new_state}}, upsert=True)
        else:
            self.conversations.update_one({'_id': str(name)},
                                          {'$unset': {json.dumps(key): ""}},
                                          upsert=True)

    def update_user_data(self, user_id: int, data: UD) -> None:
        if data:
            self.user.update_one({'_id': user_id}, {'$set': data}, upsert=True)
        else:
            self.user.delete_one({'_id': user_id})

    def update_chat_data(self, chat_id: int, data: CD) -> None:
        if data:
            self.chat.update_one({'_id': chat_id}, {'$set': data}, upsert=True)
        else:
            self.chat.delete_one({'_id': chat_id})

    def update_bot_data(self, data: BD) -> None:
        user_id = 'me'
        if data:
            self.user.update_one({'_id': user_id}, {'$set': data}, upsert=True)
        else:
            self.user.delete_one({'_id': user_id})

    def update_callback_data(self, data: CDCData) -> None:
        pass
