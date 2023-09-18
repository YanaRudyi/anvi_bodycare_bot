from unittest.mock import AsyncMock

import pytest

from bot import send_main_menu, main_menu_keyboard


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await send_main_menu(message)
    # message.answer.assert_called_with(message.chat.id, "Ласкаво просимо в Anvi! Як ми можемо допомогти вам сьогодні?",
    #                                   reply_markup=main_menu_keyboard)
