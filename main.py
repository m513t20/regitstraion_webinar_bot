from configs.config import TOKEN
from src.telegram.bot import dp,bot
import asyncio



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('hello world')
    asyncio.run(main())