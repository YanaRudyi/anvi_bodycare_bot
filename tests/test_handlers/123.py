from unittest.mock import Mock
import pytest
import asyncio

from telebot import types
from bot import send_main_menu, main_menu_keyboard

# Создаем мок бота
bot = Mock()


@pytest.mark.asyncio
async def test_send_main_menu():
    # Создаем мок объекта message
    message = Mock()

    # Создаем событийный цикл
    loop = asyncio.get_event_loop()

    # Запускаем функцию send_main_menu в событийном цикле
    await loop.create_task(send_main_menu(message, bot))

    # Ждем некоторое время (например, 1 секунду) для завершения задачи
    await asyncio.sleep(1)

    # Проверяем, что bot.send_message был вызван с правильными аргументами
    bot.send_message.assert_called_once_with(
        message.chat.id,
        "Ласкаво просимо в Anvi! Як ми можемо допомогти вам сьогодні?",
        reply_markup=main_menu_keyboard
    )
