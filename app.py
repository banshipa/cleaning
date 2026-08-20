import asyncio, json, os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = os.getenv('BOT_TOKEN', '')
PUBLIC_URL = os.getenv('PUBLIC_URL', 'http://localhost:8080')

HTML = r'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{box-sizing:border-box}body{font-family:Arial,sans-serif;margin:0;background:#f4f7f5;color:#17201b}.wrap{padding:18px;max-width:640px;margin:auto}.hero{background:#fff;border-radius:24px;padding:22px;box-shadow:0 8px 30px #0001}.green{color:#20a464;font-weight:700;font-size:13px;letter-spacing:.08em}h1{margin:7px 0 8px;font-size:29px;line-height:1.05}.hero p{color:#647067;line-height:1.4}.btn{border:0;width:100%;display:block;background:#20a464;color:white;text-align:center;padding:16px;border-radius:16px;font-weight:700;margin-top:18px;font-size:16px;cursor:pointer}.section-title{font-size:19px;margin:22px 2px 12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.card{background:#fff;border:2px solid transparent;border-radius:18px;padding:17px;box-shadow:0 5px 18px #0000000d;cursor:pointer;transition:.15s;min-height:112px}.card:active{transform:scale(.98)}.card.selected{border-color:#20a464;background:#effbf4}.card b{display:block;margin-bottom:7px}.card p{margin:0;color:#778078;font-size:14px;line-height:1.3}.price{margin-top:10px;color:#20a464;font-weight:700}.summary{display:none;margin-top:16px;background:#fff;border-radius:18px;padding:18px}.summary.show{display:block}.summary-row{display:flex;justify-content:space-between;gap:12px}.total{font-size:21px;font-weight:700;margin-top:10px}.muted{color:#778078;font-size:13px;margin-top:7px}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <div class="green">CLEANING SERVICE</div>
    <h1>Чистота без лишних забот</h1>
    <p>Выберите услугу, узнайте ориентировочную стоимость и отправьте заявку прямо из Telegram.</p>
    <button class="btn" onclick="document.getElementById('services').scrollIntoView({behavior:'smooth'})">Выбрать уборку</button>
  </div>

  <div class="section-title" id="services">Выберите услугу</div>
  <div class="grid">
    <div class="card" data-name="Поддерживающая уборка" data-price="2500"><b>Поддерживающая</b><p>Регулярная уборка квартиры</p><div class="price">от 2 500 ₽</div></div>
    <div class="card" data-name="Генеральная уборка" data-price="4500"><b>Генеральная</b><p>Глубокая уборка всех зон</p><div class="price">от 4 500 ₽</div></div>
    <div class="card" data-name="Уборка после ремонта" data-price="6500"><b>После ремонта</b><p>Пыль, следы работ, сложные загрязнения</p><div class="price">от 6 500 ₽</div></div>
    <div class="card" data-name="Уборка офиса" data-price="3500"><b>Офисы</b><p>Уборка коммерческих помещений</p><div class="price">от 3 500 ₽</div></div>
  </div>

  <div class="summary" id="summary">
    <div class="summary-row"><span>Выбрано</span><b id="selectedName"></b></div>
    <div class="total" id="selectedPrice"></div>
    <div class="muted">Финальная стоимость зависит от площади и состояния помещения.</div>
    <button class="btn" id="orderBtn">Отправить заявку</button>
  </div>
</div>
<script>
const tg = window.Telegram?.WebApp;
if (tg) { tg.ready(); tg.expand(); }
let selected = null;
const cards = document.querySelectorAll('.card');
const summary = document.getElementById('summary');
const nameEl = document.getElementById('selectedName');
const priceEl = document.getElementById('selectedPrice');

cards.forEach(card => {
  card.addEventListener('click', () => {
    cards.forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    selected = {service: card.dataset.name, price: Number(card.dataset.price)};
    nameEl.textContent = selected.service;
    priceEl.textContent = 'от ' + selected.price.toLocaleString('ru-RU') + ' ₽';
    summary.classList.add('show');
    summary.scrollIntoView({behavior:'smooth', block:'nearest'});
    if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();
  });
});

document.getElementById('orderBtn').addEventListener('click', () => {
  if (!selected) return;
  const payload = JSON.stringify({type:'cleaning_order', ...selected});
  if (tg?.sendData) {
    tg.sendData(payload);
  } else {
    alert('Заявка: ' + selected.service + ' — от ' + selected.price.toLocaleString('ru-RU') + ' ₽');
  }
});
</script>
</body>
</html>'''

async def index(request):
    return web.Response(text=HTML, content_type='text/html')

async def run_web():
    app = web.Application()
    app.router.add_get('/', index)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', 8080).start()

async def main():
    await run_web()
    if not TOKEN or TOKEN.startswith('PASTE_'):
        print('BOT_TOKEN not configured; Mini App web server is running on :8080')
        while True:
            await asyncio.sleep(3600)

    bot = Bot(TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(m: Message):
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text='Открыть приложение', web_app=WebAppInfo(url=PUBLIC_URL))
        ]])
        await m.answer('Добро пожаловать в клининговую компанию. Выберите услугу и оформите заказ в приложении.', reply_markup=kb)

    @dp.message(lambda m: m.web_app_data is not None)
    async def webapp_order(m: Message):
        try:
            data = json.loads(m.web_app_data.data)
            service = data.get('service', 'Уборка')
            price = int(data.get('price', 0))
            await m.answer(f'Заявка принята ✅\nУслуга: {service}\nОриентировочно: от {price:,} ₽'.replace(',', ' ') + '\n\nМенеджер свяжется с вами для уточнения площади, адреса и времени.')
        except Exception:
            await m.answer('Заявка получена ✅ Менеджер свяжется с вами для уточнения деталей.')

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
