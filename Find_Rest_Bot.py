import asyncio
import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

# Налаштування логування для допомоги у налагодженні
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функція для запуску бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привіт! Надішліть мені назву міста для пошуку вебсайтів ресторанів.')

# Функція для обробки пошукового запиту
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text
    websites = find_restaurant_websites(city)
    if websites:
        await update.message.reply_text('\n'.join(websites))
    else:
        await update.message.reply_text('Не вдалося знайти вебсайти ресторанів для цього міста.')

# Функція для пошуку вебсайтів ресторанів
def find_restaurant_websites(city: str) -> list:
    search_url = f"https://www.yelp.com/search?find_desc=Restaurants&find_loc={city}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        websites = []
        for link in soup.find_all('a', class_='css-1m051bw'):
            if 'biz' in link['href']:
                websites.append("https://www.yelp.com" + link['href'])
        
        return websites
    except requests.RequestException as e:
        logger.error(f"Помилка запиту: {e}")
        return []
    except Exception as e:
        logger.error(f"Сталася помилка: {e}")
        return []

async def run_bot():
    # Використовуйте токен вашого бота з перемінних середовища
    token = os.getenv('BOT_TOKEN')
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

def main():
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
