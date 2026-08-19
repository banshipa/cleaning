import asyncio, os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN=os.getenv('BOT_TOKEN','')
PUBLIC_URL=os.getenv('PUBLIC_URL','http://localhost:8080')

HTML='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><script src="https://telegram.org/js/telegram-web-app.js"></script><style>body{font-family:Arial;margin:0;background:#f4f7f5;color:#17201b}.wrap{padding:24px}.hero{background:#fff;border-radius:24px;padding:24px;box-shadow:0 8px 30px #0001}h1{margin:0 0 8px;font-size:30px}.green{color:#20a464}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}.card{background:#fff;border-radius:18px;padding:18px;box-shadow:0 5px 18px #0000000d}.btn{display:block;background:#20a464;color:white;text-align:center;padding:16px;border-radius:16px;text-decoration:none;font-weight:700;margin-top:20px}</style></head><body><div class="wrap"><div class="hero"><div class="green">CLEANING SERVICE</div><h1>Чистота без лишних забот</h1><p>Закажите профессиональную уборку квартиры, дома или офиса прямо в Telegram.</p><a class="btn" href="#services">Рассчитать стоимость</a></div><div id="services" class="grid"><div class="card"><b>Поддерживающая</b><p>Регулярная уборка</p></div><div class="card"><b>Генеральная</b><p>Глубокая уборка</p></div><div class="card"><b>После ремонта</b><p>Удаление пыли и следов работ</p></div><div class="card"><b>Офисы</b><p>Для бизнеса</p></div></div></div><script>Telegram.WebApp.ready();Telegram.WebApp.expand();</script></body></html>'''

async def index(request): return web.Response(text=HTML,content_type='text/html')

async def run_web():
    app=web.Application(); app.router.add_get('/',index)
    runner=web.AppRunner(app); await runner.setup(); await web.TCPSite(runner,'0.0.0.0',8080).start()

async def main():
    await run_web()
    if not TOKEN or TOKEN.startswith('PASTE_'):
        print('BOT_TOKEN not configured; Mini App web server is running on :8080')
        while True: await asyncio.sleep(3600)
    bot=Bot(TOKEN); dp=Dispatcher()
    @dp.message(CommandStart())
    async def start(m: Message):
        kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Открыть приложение',web_app=WebAppInfo(url=PUBLIC_URL))]])
        await m.answer('Добро пожаловать в клининговую компанию. Выберите услугу и оформите заказ в приложении.',reply_markup=kb)
    await dp.start_polling(bot)

if __name__=='__main__': asyncio.run(main())
