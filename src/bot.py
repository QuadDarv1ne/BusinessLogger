import asyncio
from aiogram import F, Bot, Dispatcher, types, exceptions
from loguru import logger
from redis.asyncio import Redis
from typing import Optional

from .settings import settings
from .keyboards import link_markup, Callbacks

# Инициализация бота и Redis
bot = Bot(token=settings.TOKEN.get_secret_value())
dp = Dispatcher()
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD.get_secret_value() if settings.REDIS_PASSWORD else None,
)
EX_TIME = 60 * 60 * 24 * 21  # 21 день

async def set_message(message: types.Message) -> None:
    """Сохраняет сообщение в Redis с истечением через EX_TIME."""
    try:
        await redis.set(
            f"{message.chat.id}:{message.message_id}",
            message.model_dump_json(),
            ex=EX_TIME,
        )
        logger.info(f"Сообщение сохранено: {message.chat.id}:{message.message_id}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении сообщения: {e}")

@dp.message_handler()
async def handle_message(message: types.Message) -> None:
    """Обработчик для входящих сообщений."""
    await set_message(message)


@dp.edited_business_message()
async def edited_message(message: types.Message):
    model_dump = await redis.get(f"{message.chat.id}:{message.message_id}")
    await set_message(message)

    if not model_dump:
        return

    original_message = types.Message.model_validate_json(model_dump)
    if not original_message.from_user:
        return

    await original_message.send_copy(
        chat_id=settings.USER_ID,
        reply_markup=link_markup("✏️", original_message.from_user.id),
    ).as_(bot)


async def copy_message(message: types.Message):
    await message.send_copy(
        chat_id=settings.USER_ID,
    ).as_(bot)


@dp.deleted_business_messages()
async def deleted_message(business_messages: types.BusinessMessagesDeleted):
    pipe = redis.pipeline()
    for message_id in business_messages.message_ids:
        pipe.get(f"{business_messages.chat.id}:{message_id}")
    messages_data = await pipe.execute()

    keys_to_delete = []
    for message_id, model_dump in zip(business_messages.message_ids, messages_data):
        if not model_dump:
            continue

        original_message = types.Message.model_validate_json(model_dump)
        if not original_message.from_user:
            continue

        send_copy = original_message.send_copy(
            chat_id=settings.USER_ID,
            reply_markup=link_markup("🗑️", original_message.from_user.id),
        ).as_(bot)

        try:
            await send_copy
        except exceptions.TelegramRetryAfter as exp:
            logger.warning(f"Retry after {exp.retry_after} seconds")
            await asyncio.sleep(exp.retry_after + 0.1)
            await send_copy
        finally:
            await asyncio.sleep(0.1)

        keys_to_delete.append(f"{business_messages.chat.id}:{message_id}")

    if keys_to_delete:
        await redis.delete(*keys_to_delete)


@dp.callback_query(F.data == Callbacks.EMPTY)
async def empty(query: types.CallbackQuery):
    await query.answer()


@dp.callback_query(F.data == Callbacks.CLOSE)
async def close(query: types.CallbackQuery):
    await query.answer()
    if isinstance(query.message, types.Message):
        await query.message.delete()
