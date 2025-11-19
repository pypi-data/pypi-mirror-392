from typing import Any, NoReturn

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Chat, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message


def get_from_user(update: Any) -> int | Chat:
    return update.from_user


def get_chat_id(update: Any) -> int | NoReturn:
    chat = get_chat(update)
    return chat.id


def get_chat(update: Any) -> int | Chat:
    if isinstance(update, Message):
        return update.chat
    if isinstance(update, CallbackQuery):
        return update.message.chat
    exc_txt = "Unsupported update type for chat ID retrieval."
    raise ValueError(exc_txt)


async def send_media_group(
    bot: AsyncTeleBot, chat_id: int, media_items: list[dict[str, str]], media_types: list[str]
) -> None:
    media = []
    for item in media_items:
        if item["type"] not in media_types:
            continue
        if item["type"] == "photo":
            media.append(InputMediaPhoto(item["file_id"]))
        elif item["type"] == "video":
            media.append(InputMediaVideo(item["file_id"]))
        elif item["type"] == "document":
            media.append(InputMediaDocument(item["file_id"]))
        if media and len(media) % 10 == 0:
            await bot.send_media_group(chat_id=chat_id, media=media)
            media = []
    if media:
        await bot.send_media_group(chat_id=chat_id, media=media)


# username = f" @{update.from_user.username}" if update.from_user.username else ""
# author = f"{update.from_user.full_name}{username}"
