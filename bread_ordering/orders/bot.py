import telegram
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def send_telegram_notification(orders):
    bot_token = os.getenv("telegram")
    chat_id = '712395220'  # Ваш Telegram Chat ID
    bot = telegram.Bot(token=bot_token)
    for order in orders:
        message = (
            f"Новый заказ!\n\n"
            f"Хлеб: {order.bread.name}\n"
            f"Количество: {order.quantity}\n"
            f"Имя клиента: {order.customer_name}\n"
            f"Телефон: {order.phone}\n"
            f"Адрес: {order.address}"
        )
        await bot.send_message(chat_id=chat_id, text=message)

